import datetime
from abc import ABC
from typing import Tuple, Dict

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
                html.H1("Worker lines fatigue monitoring dashboard"),
                dbc.Row(
                    [
                        dbc.Col(
                            html.P(
                                [
                                    'This graph shows the current levels of ',
                                    html.Strong('fatigue'),
                                    ' for each worker assigned to the related production line.'
                                ],
                                className='lead'
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
                        ),

                        dbc.Col(
                            children=[self._build_interventions()],
                            md=12,
                            id="interventions"
                        ),
                        dcc.Interval(
                            id='interventions-interval',
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

    def _worker_line(self, worker_id):
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
                    name=f'Line{self._worker_line(k) + 1}'
                )
                for k in r if r[k]['workerStates'].any()}

            fatigue_df = self._empty_dataset(dti)
            for worker_df in worker_data.values():
                fatigue_df = pd.concat([fatigue_df, worker_df])

        except (HTTPError, ConnectionError) as e:
            print(f"No data available for the given time window {dti[0]} -- {dti[-1]}")
            print(e)
            return pd.DataFrame(columns=['workers', 'line']), self._empty_dataset()

        workers_lines_df = pd.DataFrame(
            {'workers': worker_data.keys(),
             'line': [f'Line{self._worker_line(w_id) + 1}' for w_id in worker_data]}
        ).groupby('line').count()

        return workers_lines_df, fatigue_df.groupby(fatigue_df.index).mean()

    def _empty_dataset(self, dti=None) -> pd.DataFrame:
        if dti is None:
            dti = self._date_time_index_utc()
        df = pd.DataFrame({
            'Line1': [np.nan] * len(dti),
            'Line2': [np.nan] * len(dti),
            'Line3': [np.nan] * len(dti)
        }, index=dti)

        return df.resample('T').mean()

    def _build_worker_graphs(self, n=0) -> Component:
        workers_by_line_df, worker_data = self._fetch_workers_data()
        worker_data.index = worker_data.index.tz_convert('CET')  # read timezone from env

        return dbc.Row(
            [
                dbc.Col(
                    [
                        html.Center([
                            html.H2(f'Connected workers: {workers_by_line_df["workers"].sum()}'),
                        ]),
                    ],
                    md=12
                ),
                dbc.Col(
                    [
                        html.Center([
                            html.H4(f'% of workers per line'),
                        ]),
                        dbc.Col(
                            dcc.Graph(id="workers-by-line",
                                      figure=px.pie(
                                          workers_by_line_df,
                                          title="",
                                          values="workers",
                                          names=workers_by_line_df.index,
                                          color=workers_by_line_df.index,
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
                            html.H4("Current fatigue per line"),
                        ]),
                        dbc.Col(
                            dcc.Graph(id="current-fatigue",
                                      figure=self._build_worker_line_fatigue_last(worker_data)),
                            # width={"size": 8, "offset": 2},
                        ),
                    ],
                    className="gy-3",
                    md=4,
                ),
                dbc.Col(
                    [
                        html.Center([
                            html.H4("Historical fatigue per line"),
                        ]),
                        dbc.Col(
                            dcc.Graph(id="timeseries-fatigue",
                                      figure=self._build_worker_line_fatigue_timeseries(worker_data)),
                            # width={"size": 8, "offset": 2},
                        ),
                    ],
                    className="gy-3",
                    md=4,
                ),
            ],
        )

    def _build_worker_line_fatigue_last(self, fatigue_df):
        return px.bar(
            # title='Control',
            x=fatigue_df.columns,
            y=[fatigue_df[line].mean() for line in fatigue_df.columns],
            error_y=[fatigue_df[col].std() for col in fatigue_df.columns],
            labels={'x': 'Line', 'y': 'Fatigue [avg]', 'color': 'Legend'},
            color=fatigue_df.columns,
            color_discrete_sequence=['rgb(248,156,116)', 'rgb(139,224,164)', 'rgb(158,185,243)'],
            range_y=[0, 10]
        )

    def _build_worker_line_fatigue_timeseries(self, fatigue_df):
        return px.line(
            fatigue_df,
            labels={'index': 'Time', 'value': 'Fatigue [avg]', 'variable': 'Legend'},
            color_discrete_sequence=['rgb(248,156,116)', 'rgb(139,224,164)', 'rgb(158,185,243)'],
            range_y=[0, 10])

    def _fetch_intervention(self) -> Dict:
        try:
            from_ = pd.Timestamp.now('utc') - pd.Timedelta(hours=1)
            assignment = list(self._quantumleap.fetch_entity_type_series(entity_type="TaskAssignment",
                                                                         from_timepoint=from_).values())[0].to_dict(
                orient='records')[-1]
            execution = list(self._quantumleap.fetch_entity_type_series(entity_type="TaskExecution",
                                                                        from_timepoint=from_).values())[0].to_dict(
                orient='records')[-1]
            if int(assignment['creationTimestamp']) > int(execution['creationTimestamp']):
                return {
                    'datetime': datetime.datetime.fromtimestamp(int(assignment['creationTimestamp']) / 1000),
                    'intervention': "Reconfigure",
                    "from": int(assignment['oldTask'][-1]),
                    "to": int(assignment['newTask'][-1]),
                    "workers": assignment['additionalParameters']['numberOfWorkers']
                }

            else:
                return {
                    'datetime': datetime.datetime.fromtimestamp(int(execution['creationTimestamp']) / 1000),
                    'intervention': "Continue"
                }

        except Exception as e:
            return {}

    def _build_interventions(self, n=0) -> Component:
        intervention = self._fetch_intervention()
        if not intervention:
            p = [html.Small(datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S"), className="text-muted"),
                 ' No interventions']
        else:
            p = [html.Small(intervention['datetime'].strftime("%d-%m-%Y %H:%M:%S"), className="text-muted")]
            if intervention['intervention'] == 'Reconfigure':
                p += [
                    ' Move ',
                    html.Strong(intervention['workers']),
                    ' workers from ',
                    html.Strong(f'Line{intervention["from"]}'),
                    ' to ',
                    html.Strong(f'Line{intervention["to"]}'),
                ]
            else:
                p += ['Keep the current configuration']

        return dbc.Row([
            dbc.Col(
                [
                    html.H2(f'Last accepted intervention'),
                    html.P(p, className='lead')
                ],
                md=12,
                className='gy-4'
            ),
        ])

    def _build_callbacks(self):
        self.app.callback(
            Output("worker_graphs", 'children'),
            Input('worker-interval', 'n_intervals')
        )(self._build_worker_graphs)

        self.app.callback(
            Output("interventions", 'children'),
            Input('interventions-interval', 'n_intervals')
        )(self._build_interventions)
