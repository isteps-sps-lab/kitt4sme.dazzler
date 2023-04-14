# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.
from abc import ABC
from datetime import datetime, timedelta, timezone
from typing import Optional, Any

import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import pytz
from dash import Dash, html, dcc, Output, Input
from dash.development.base_component import Component
from dash.html import Figure
from dash_bootstrap_templates import load_figure_template
from fipy.ngsi.headers import FiwareContext
from fipy.ngsi.orion import OrionClient
from fipy.ngsi.quantumleap import QuantumLeapClient
from requests import HTTPError
from uri import URI

THEME = [dbc.themes.SLATE]
load_figure_template("slate")


class FatigueDashboard(ABC):
    def __init__(self):
        super().__init__()

        self.app = Dash(
            __name__,
            suppress_callback_exceptions=True,
            prevent_initial_callbacks=False,
            external_stylesheets=THEME
        )

        self._orion_client = OrionClient(
            URI("http://sps-lab01.supsi.ch:8006"),
            FiwareContext(service=None, service_path=None, correlator=None))

        self._quantumleap = QuantumLeapClient(
            base_url=URI("http://sps-lab01.supsi.ch:8008"),
            ctx=FiwareContext(
                # service=base_path.tenant(),
                service_path="/"
            )
        )

        self.worker_data = dict()

    def empty_data_set(self) -> dict:
        return {
            'index': [0],
            'fatigue': [0]
        }

    def make_figure(self, df: pd.DataFrame) -> Any:
        color_map = {True: 'coral', False: 'silver'}
        fig = px.scatter(df, x=df.index, y=df.fatigue,
                         color_discrete_map=color_map)
        fig.update_layout(legend_title_text='Defect?')
        return fig

    def _empty_fig(self) -> Any:
        data = self.empty_data_set()
        df = pd.DataFrame(data).set_index('index')
        return self.make_figure(df)

    def build_dash_app(self) -> Dash:
        self._build_layout()
        self._build_callbacks()
        return self.app

    def _build_layout(self):
        self.app.layout = dbc.Container(
            [
                html.H1("Worker cells monitoring dashboard"),

                dbc.Row(
                    [
                        dbc.Col(
                            dcc.Markdown(
                                '''
                                        This graph shows the current levels of **fatigue** for each worker assigned to
                                        the related production cell.
                                '''
                            ),
                            md=12),
                        html.Hr(),

                        dcc.Interval(
                            id='worker-interval',
                            interval=5 * 1000,  # in milliseconds
                            n_intervals=0
                        ),

                        dbc.Col(self._build_worker_graphs(), md=12),

                        dcc.Interval(
                            id='graphs-interval',
                            interval=1 * 1000,  # in milliseconds
                            n_intervals=0
                        )
                    ]
                ),
            ],
            fluid=False
        )

    def fetch_entity_series(self, entity_id: str, entity_type: str,
                            entries_from_latest: Optional[int] = None,
                            from_timepoint: Optional[datetime] = None,
                            to_timepoint: Optional[datetime] = None) -> pd.DataFrame:
        r = self._quantumleap.entity_series(
            entity_id=entity_id, entity_type=entity_type,
            entries_from_latest=entries_from_latest,
            from_timepoint=from_timepoint, to_timepoint=to_timepoint
        )
        time_indexed_df = pd.DataFrame(r.dict()).set_index('index')
        return time_indexed_df

    def fetch_entity_type_series(self, entity_type: str,
                                 entries_from_latest: Optional[int] = None,
                                 from_timepoint: Optional[datetime] = None,
                                 to_timepoint: Optional[datetime] = None) -> dict:
        try:
            r = self._quantumleap.entity_type_series(
                entity_type=entity_type, entries_from_latest=entries_from_latest,
                from_timepoint=from_timepoint, to_timepoint=to_timepoint
            )
            for key in r:
                r[key] = pd.DataFrame(r[key].dict()).set_index('index')
                r[key].index = map(lambda x: x.astimezone(pytz.timezone('CET')),
                                   r[key].index)  # TODO: put timezone as environment variable
            return r
        except HTTPError:
            print("No results found in the given interval")
            return dict()

    def _fetch_workers_data(self):
        self.worker_data = self.fetch_entity_type_series(entity_type="Worker", entries_from_latest=20,
                                                         from_timepoint=datetime.now(timezone.utc) - timedelta(
                                                             minutes=3),
                                                         to_timepoint=datetime.now(timezone.utc))

    def _build_worker_graphs(self, n=0) -> Component:
        self._fetch_workers_data()

        children = []
        children_cell_1 = []
        children_cell_2 = []
        children_cell_3 = []

        for worker in self.worker_data:
            cell_id = ord(worker[-1]) % 3
            if cell_id == 0:
                children_cell_1.append(
                    dcc.Graph(id=worker, figure=self._update_worker_fatigue(worker))
                )
                children_cell_1.append(
                    html.Br()
                )
            elif cell_id == 1:
                children_cell_2.append(
                    dcc.Graph(id=worker, figure=self._update_worker_fatigue(worker))
                )
                children_cell_2.append(
                    html.Br()
                )
            else:
                children_cell_3.append(
                    dcc.Graph(id=worker, figure=self._update_worker_fatigue(worker))
                )
                children_cell_3.append(
                    html.Br()
                )

        children.append(
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.H3("Cell 1"),
                            dbc.Col(
                                children_cell_1
                            ),
                        ],
                        md=4,
                    ),
                    dbc.Col(
                        [
                            html.H3("Cell 2"),
                            dbc.Col(
                                children_cell_2
                            ),
                        ],
                        md=4,
                    ),
                    dbc.Col(
                        [
                            html.H3("Cell 3"),
                            dbc.Col(
                                children_cell_3
                            ),
                        ],
                        md=4,
                    )
                ],
            ),
        )

        return dbc.Col(children=children, id="worker_graphs")

    def _update_worker_fatigue(self, worker_id) -> Figure:
        fatigue = self.worker_data[worker_id].workerStates.apply(
            lambda x: x["fatigue"]["level"]["value"] if x else x).rename("Fatigue")

        return px.line(fatigue, title=worker_id, x=fatigue.index, y="Fatigue", markers=True,
                       color_discrete_sequence=['coral'])

    # def _update_worker_2_fatigue(self, n, worker_id="worker2"):
    #     self._fetch_workers_data()
    #     fatigue = self.worker_data[worker_id].workerStates.apply(
    #         lambda x: x["fatigue"]["level"]["value"] if x else x).rename("Fatigue")
    #
    #     return px.line(fatigue, title=worker_id, x=fatigue.index, y="Fatigue", markers=True,
    #                    color_discrete_sequence=['coral'])
    #
    # def _update_worker_3_fatigue(self, n, worker_id="worker3"):
    #     self._fetch_workers_data()
    #     fatigue = self.worker_data[worker_id].workerStates.apply(
    #         lambda x: x["fatigue"]["level"]["value"] if x else x).rename("Fatigue")
    #
    #     return px.line(fatigue, title=worker_id, x=fatigue.index, y="Fatigue", markers=True,
    #                    color_discrete_sequence=['coral'])
    #
    # def _update_worker_4_fatigue(self, n, worker_id="worker4"):
    #     self._fetch_workers_data()
    #     fatigue = self.worker_data[worker_id].workerStates.apply(
    #         lambda x: x["fatigue"]["level"]["value"] if x else x).rename("Fatigue")
    #
    #     return px.line(fatigue, title=worker_id, x=fatigue.index, y="Fatigue", markers=True,
    #                    color_discrete_sequence=['coral'])
    #
    # def _update_worker_5_fatigue(self, n, worker_id="worker5"):
    #     self._fetch_workers_data()
    #     fatigue = self.worker_data[worker_id].workerStates.apply(
    #         lambda x: x["fatigue"]["level"]["value"] if x else x).rename("Fatigue")
    #
    #     return px.line(fatigue, title=worker_id, x=fatigue.index, y="Fatigue", markers=True,
    #                    color_discrete_sequence=['coral'])

    def _build_callbacks(self):
        self.app.callback(
            Output("worker_graphs", 'children'),
            Input('worker-interval', 'n_intervals')
        )(self._build_worker_graphs)

        # self.app.callback(
        #     Output("worker1", 'figure'),
        #     Input('graphs-interval', 'n_intervals'),
        #     # Input("worker4", 'value')
        # )(self._update_worker_1_fatigue)

        # self.app.callback(
        #     Output("worker2", 'figure'),
        #     Input('graphs-interval', 'n_intervals'),
        #     # Input("worker4", 'value')
        # )(self._update_worker_2_fatigue)
        #
        # self.app.callback(
        #     Output("worker3", 'figure'),
        #     Input('graphs-interval', 'n_intervals'),
        #     # Input("worker4", 'value')
        # )(self._update_worker_3_fatigue)
        #
        # self.app.callback(
        #     Output("worker4", 'figure'),
        #     Input('graphs-interval', 'n_intervals'),
        #     # Input("worker4", 'value')
        # )(self._update_worker_4_fatigue)
        #
        # self.app.callback(
        #     Output("worker5", 'figure'),
        #     Input('graphs-interval', 'n_intervals'),
        #     # Input("worker4", 'value')
        # )(self._update_worker_5_fatigue)


fatigue_dashboard = FatigueDashboard()

if __name__ == '__main__':
    fatigue_dashboard.build_dash_app().run_server(debug=True)
