from abc import ABC
from datetime import datetime, timedelta, timezone

import dash_bootstrap_components as dbc
import plotly.express as px
from dash import Dash, html, dcc, Output, Input
from dash.development.base_component import Component
from dash.html import Figure
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
        from_ = to_ - timedelta(minutes=3)
        try:
            self.worker_data = self._quantumleap.fetch_entity_type_series(entity_type="Worker",
                                                                          from_timepoint=from_,
                                                                          to_timepoint=to_)
        except HTTPError:
            print(f"No data available for the given time window {from_} -- {to_}")
            self.worker_data = {}

        # TODO: fix timezone
        # TODO: read timezone from environment vars

    def _build_worker_graphs(self, n=0) -> Component:
        self._fetch_workers_data()

        children_cell_1 = []
        children_cell_2 = []
        children_cell_3 = []

        for worker in self.worker_data:
            cell_id = ord(worker[-1]) % 3  # get the ASCII code of worker id's last character as cell identifier
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

        if len(children_cell_1) == 0:
            children_cell_1.append(
                dcc.Markdown('No worker inside the cell.'),
            )
        if len(children_cell_2) == 0:
            children_cell_2.append(
                dcc.Markdown('No worker inside the cell.'),
            )
        if len(children_cell_3) == 0:
            children_cell_3.append(
                dcc.Markdown('No worker inside the cell.'),
            )

        return dbc.Row(
            [
                dbc.Col(
                    [
                        html.H3("Workcell #1"),
                        dbc.Col(
                            children_cell_1,
                            md=12
                        ),
                    ],
                    md=4,
                ),
                dbc.Col(
                    [
                        html.H3("Workcell #2"),
                        dbc.Col(
                            children_cell_2,
                            md=12
                        ),
                    ],
                    md=4,
                ),
                dbc.Col(
                    [
                        html.H3("Workcell #3"),
                        dbc.Col(
                            children_cell_3,
                            md=12
                        ),
                    ],
                    md=4,
                )
            ],
        )

    def _update_worker_fatigue(self, worker_id) -> Figure:
        fatigue = self.worker_data[worker_id].workerStates.apply(
            lambda x: x["fatigue"]["level"]["value"] if x else x).rename("Fatigue")

        return px.line(fatigue, title=worker_id, x=fatigue.index, y="Fatigue", markers=True,
                       color_discrete_sequence=['coral'])

    def _build_callbacks(self):
        self.app.callback(
            Output("worker_graphs", 'children'),
            Input('worker-interval', 'n_intervals')
        )(self._build_worker_graphs)
