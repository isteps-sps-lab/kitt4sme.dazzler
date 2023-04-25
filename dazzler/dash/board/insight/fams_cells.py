from abc import ABC
from datetime import datetime, timedelta, timezone

import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import pytz
from dash import Dash, html, dcc, Output, Input
from dash.development.base_component import Component
from requests import HTTPError

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

    def _fetch_workers_data(self):
        to_ = datetime.now(timezone.utc)
        from_ = to_ - timedelta(minutes=10)
        try:
            r = self._quantumleap.fetch_entity_type_series(entity_type="Worker",
                                                           from_timepoint=from_,
                                                           to_timepoint=to_)
            self.worker_data = {k: r[k] for k in r if r[k]['workerStates'].any()}
            for key in self.worker_data:
                tz = pytz.timezone('CET')  # TODO: read timezone from environment vars
                self.worker_data[key]['index'] = self.worker_data[key]['index'].apply(lambda x: x.astimezone(tz))
                self.worker_data[key] = self.worker_data[key].set_index('index')

            fatigue_cell_1 = pd.DataFrame()
            fatigue_cell_2 = pd.DataFrame()
            fatigue_cell_3 = pd.DataFrame()

            for worker_id in self.worker_data:
                cell_id = ord(worker_id[-1]) % 3  # get the ASCII code of worker id's last character as cell identifier
                fatigue = self.worker_data[worker_id].workerStates.apply(
                    lambda x: x["fatigue"]["level"]["value"] if x else x).rename("Fatigue")
                fatigue = fatigue.resample('T').mean()
                if cell_id == 0:
                    fatigue_cell_1 = pd.concat([fatigue_cell_1, fatigue]).groupby(level=0).mean()
                elif cell_id == 1:
                    fatigue_cell_2 = pd.concat([fatigue_cell_2, fatigue]).groupby(level=0).mean()
                else:
                    fatigue_cell_3 = pd.concat([fatigue_cell_3, fatigue]).groupby(level=0).mean()

            self.fatigue_df = pd.concat([fatigue_cell_1, fatigue_cell_2, fatigue_cell_3], axis=1)
            self.fatigue_df.columns = ["Cell1", "Cell2", "Cell3"]
            print(self.fatigue_df)

        except HTTPError:
            print(f"No data available for the given time window {from_} -- {to_}")
            self.worker_data = {}

    def _build_worker_graphs(self, n=0) -> Component:
        self._fetch_workers_data()

        return dbc.Row(
            [
                dbc.Col(
                    html.H2(
                        f'''Number of connected workers: {len(self.worker_data.keys())}'''
                    ),
                    md=12),
                dbc.Col(
                    [
                        html.Center([
                            html.H3("Current fatigue per workcell"),
                        ]),
                        dbc.Col(
                            dcc.Graph(id="current-fatigue", figure=self._build_worker_cell_fatigue_last()),
                            # width={"size": 8, "offset": 2},
                        ),
                    ],
                    # className="gy-3",
                    md=6,
                ),
                dbc.Col(
                    [
                        html.Center([
                            html.H3("Historical fatigue per workcell"),
                        ]),
                        dbc.Col(
                            dcc.Graph(id="timeseries-fatigue", figure=self._build_worker_cell_fatigue_timeseries()),
                            # width={"size": 8, "offset": 2},
                        ),
                    ],
                    # className="gy-3",
                    md=6,
                ),
            ],
        )

    def _build_worker_cell_fatigue_last(self):
        print(px.colors.qualitative.Pastel2)
        return px.bar(
            # title='Control',
            x=self.fatigue_df.columns,
            y=[self.fatigue_df['Cell1'].mean(), self.fatigue_df['Cell2'].mean(), self.fatigue_df['Cell3'].mean()],
            error_y=[self.fatigue_df['Cell1'].std(), self.fatigue_df['Cell2'].std(), self.fatigue_df['Cell3'].std()],
            labels={'x': 'Cell', 'y': 'Fatigue [avg]', 'color': 'Legend'},
            color=self.fatigue_df.columns,
            color_discrete_sequence=['rgb(248,156,116)', 'rgb(139,224,164)', 'rgb(158,185,243)']
        )

    def _build_worker_cell_fatigue_timeseries(self):
        return px.line(
            self.fatigue_df,
            labels={'index': 'Time', 'value': 'Fatigue [avg]', 'variable': 'Legend'},
            color_discrete_sequence=['rgb(248,156,116)', 'rgb(139,224,164)', 'rgb(158,185,243)'])

    def _build_callbacks(self):
        self.app.callback(
            Output("worker_graphs", 'children'),
            Input('worker-interval', 'n_intervals')
        )(self._build_worker_graphs)
