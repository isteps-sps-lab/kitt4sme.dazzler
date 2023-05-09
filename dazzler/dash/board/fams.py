from abc import ABC
from typing import Tuple

import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
import plotly.express as px
from dash import Dash, html, dcc, Output, Input
from dash.development.base_component import Component
from requests import HTTPError, ConnectionError

from dazzler.dash.fiware import QuantumLeapSource, OrionSource
from dazzler.dash.wiring import BasePath


def dash_builder(app: Dash) -> Dash:
    return FatigueDashboard(app).build_dash_app()


class FatigueDashboard(ABC):
    def __init__(self, app: Dash):
        super().__init__()

        self.app = app
        self._orion = OrionSource(app)
        self._quantumleap = QuantumLeapSource(app)
        self._base_path = BasePath.from_board_app(app)

        self.worker_data = dict()

    def build_dash_app(self) -> Dash:
        self._build_layout()
        self._build_callbacks()
        return self.app

    def _build_layout(self):
        self.app.layout = dbc.Container(
            [
                html.H1("Worker cells fatigue monitoring dashboard"),
                dbc.Row(
                    [
                        dbc.Col(
                            dcc.Markdown(
                                '''This graph shows the current levels of **fatigue** for each worker assigned to the
                                related production cell.'''
                            ),
                            md=12),
                        html.Hr(),

                        dbc.Col(
                            children=[self._build_worker_graphs()],
                            md=12,
                            id="worker_graphs"
                        ),
                        dcc.Interval(
                            id='worker-interval',
                            interval=5 * 1000,  # in milliseconds
                            n_intervals=0
                        )
                    ]
                ),
            ],
            fluid=False
        )

    def _date_time_index_utc(self, minutes=10):
        tix = pd.Timestamp.now('utc') - pd.Timedelta(minutes=minutes - 1)
        return pd.date_range(tix, periods=minutes, freq="T")

    def _worker_cell(self, worker_id):
        return ord(worker_id[-1]) % 3

    def _fetch_workers_data(self) -> Tuple[pd.DataFrame, pd.DataFrame]:

        dti = self._date_time_index_utc()

        try:
            r = self._quantumleap.fetch_entity_type_series(entity_type="Worker",
                                                           from_timepoint=dti[0],
                                                           to_timepoint=dti[-1])
            worker_data = {
                k: r[k].set_index('index').workerStates.apply(
                    lambda x: x["fatigue"]["level"]["value"] if x else x).resample('T').mean().to_frame(
                    name=f'Cell{self._worker_cell(k) + 1}'
                )
                for k in r if r[k]['workerStates'].any()}

            fatigue_df = self._empty_dataset(dti)
            for worker_df in worker_data.values():
                fatigue_df = pd.concat([fatigue_df, worker_df])

        except (HTTPError, ConnectionError) as e:
            print(f"No data available for the given time window {dti[0]} -- {dti[-1]}")
            print(e)
            return self._empty_dataset()

        workers_cells_df = pd.DataFrame(
            {'workers': worker_data.keys(),
             'cell': [f'Cell{self._worker_cell(w_id) + 1}' for w_id in worker_data]}
        ).groupby('cell').count()

        return workers_cells_df, fatigue_df.groupby(fatigue_df.index).mean()

    def _empty_dataset(self, dti=None) -> pd.DataFrame:
        if dti is None:
            dti = self._date_time_index_utc()
        df = pd.DataFrame({
            'Cell1': [np.nan] * len(dti),
            'Cell2': [np.nan] * len(dti),
            'Cell3': [np.nan] * len(dti)
        }, index=dti)

        return df.resample('T').mean()

    def _build_worker_graphs(self, n=0) -> Component:
        workers_by_cell_df, worker_data = self._fetch_workers_data()
        worker_data.index = worker_data.index.tz_convert('CET')  # read timezone from env

        return dbc.Row(
            [
                dbc.Col(
                    [
                        html.Center([
                            html.H2(f'Connected workers: {workers_by_cell_df["workers"].sum()}'),
                        ]),
                    ],
                    md=12
                ),
                dbc.Col(
                    [
                        html.Center([
                            html.H4(f'% of workers per workcell'),
                        ]),
                        dbc.Col(
                            dcc.Graph(id="workers-by-cell",
                                      figure=px.pie(
                                          workers_by_cell_df,
                                          title="",
                                          values="workers",
                                          names=workers_by_cell_df.index,
                                          color=workers_by_cell_df.index,
                                          color_discrete_sequence=['rgb(248,156,116)', 'rgb(139,224,164)',
                                                                   'rgb(158,185,243)'],
                                      ))
                        )
                    ],
                    className="gy-3",
                    md=4),
                dbc.Col(
                    [
                        html.Center([
                            html.H4("Current fatigue per workcell"),
                        ]),
                        dbc.Col(
                            dcc.Graph(id="current-fatigue",
                                      figure=self._build_worker_cell_fatigue_last(worker_data)),
                            # width={"size": 8, "offset": 2},
                        ),
                    ],
                    className="gy-3",
                    md=4,
                ),
                dbc.Col(
                    [
                        html.Center([
                            html.H4("Historical fatigue per workcell"),
                        ]),
                        dbc.Col(
                            dcc.Graph(id="timeseries-fatigue",
                                      figure=self._build_worker_cell_fatigue_timeseries(worker_data)),
                            # width={"size": 8, "offset": 2},
                        ),
                    ],
                    className="gy-3",
                    md=4,
                ),
            ],
        )

    def _build_worker_cell_fatigue_last(self, fatigue_df):
        return px.bar(
            # title='Control',
            x=fatigue_df.columns,
            y=[fatigue_df[cell].mean() for cell in fatigue_df.columns],
            error_y=[fatigue_df[col].std() for col in fatigue_df.columns],
            labels={'x': 'Cell', 'y': 'Fatigue [avg]', 'color': 'Legend'},
            color=fatigue_df.columns,
            color_discrete_sequence=['rgb(248,156,116)', 'rgb(139,224,164)', 'rgb(158,185,243)'],
            range_y=[0, 10]
        )

    def _build_worker_cell_fatigue_timeseries(self, fatigue_df):
        return px.line(
            fatigue_df,
            labels={'index': 'Time', 'value': 'Fatigue [avg]', 'variable': 'Legend'},
            color_discrete_sequence=['rgb(248,156,116)', 'rgb(139,224,164)', 'rgb(158,185,243)'],
            range_y=[0, 10])

    def _build_callbacks(self):
        self.app.callback(
            Output("worker_graphs", 'children'),
            Input('worker-interval', 'n_intervals')
        )(self._build_worker_graphs)
