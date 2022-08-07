from abc import ABC, abstractmethod
from typing import Any, Dict

from dash import Dash, Input, Output, dcc, html
from dash.development.base_component import Component
import dash_bootstrap_components as dbc
import pandas as pd

from dazzler.dash.components import has_triggered, datetime_local_input, \
    from_datetime_local_input
from dazzler.dash.wiring import BasePath
from dazzler.dash.timeseries import QuantumLeapSource


LOAD_BUTTON_ID = 'load-button'
ENTRIES_FROM_INPUT_ID = 'entries-from'
ENTRIES_TO_INPUT_ID = 'entries-to'
GRAPH_ID = 'graph'


class EntitiesFrameDashboard(ABC):

    def __init__(self, app: Dash,
                    title: str, entity_type: str):
        super().__init__()
        self._app = app
        self._title = title
        self._entity_type = entity_type
        self._base_path = BasePath.from_board_app(app)
        self._quantumleap = QuantumLeapSource(app)

    @abstractmethod
    def explanation(self) -> str:
        pass

    @abstractmethod
    def make_figure(self, entity_type_series: Dict[str, pd.DataFrame]) -> Any:
        pass

    def build_dash_app(self) -> Dash:
        self._build_layout()
        self._build_callbacks()
        return self._app

    def _build_layout(self):
        self._app.layout = dbc.Container(
            [
                html.H1(self._title),
                html.Hr(),
                dbc.Row(
                    [
                        dbc.Col(self._build_card(), md=4),
                        dbc.Col(
                            dcc.Graph(id=GRAPH_ID,
                                      figure=self.make_figure({})),
                            md=8
                        )
                    ],
                    align="center",
                )
            ],
            fluid=True
        )

    def _build_card(self) -> Component:
        return dbc.Card(
            [
                html.Div([
                    html.H3(self._base_path.tenant())
                ]),
                html.Div([
                    html.H5(f"service path: {self._base_path.service_path()}")
                ]),
                html.Hr(),
                dcc.Markdown(self.explanation()),
                html.Hr(),
                dbc.Row([
                    dbc.Col(
                        dbc.Label('Entities from'),
                        md=4
                    ),
                    dbc.Col(
                        datetime_local_input(ENTRIES_FROM_INPUT_ID),
                        md=8
                    )
                ]),
                html.P(),
                dbc.Row([
                    dbc.Col(
                        dbc.Label('Entities to'),
                        md=4
                    ),
                    dbc.Col(
                        datetime_local_input(ENTRIES_TO_INPUT_ID),
                        md=8
                    )
                ]),
                html.P(),
                dbc.Row([
                    dbc.Col(
                        dbc.Button('Load Entities', id=LOAD_BUTTON_ID,
                                    n_clicks=0)
                    )
                ])
            ],
            body=True
        )

    def _build_callbacks(self):
        self._app.callback(
            Output(GRAPH_ID, 'figure'),
            Input(LOAD_BUTTON_ID, 'n_clicks'),
            Input(ENTRIES_FROM_INPUT_ID, 'value'),
            Input(ENTRIES_TO_INPUT_ID, 'value')
        )(self._update_graph)

    def _update_graph(self, btn_clicks, entries_from, entries_to) -> Any:
        frames = {}  # draw empty plot

        if has_triggered(LOAD_BUTTON_ID):
            from_time = from_datetime_local_input(entries_from)
            to_time = from_datetime_local_input(entries_to)
            if from_time and to_time:
                frames = self._quantumleap.fetch_entity_type_series(
                    entity_type=self._entity_type,
                    from_timepoint=from_time, to_timepoint=to_time
                )

        return self.make_figure(frames)
