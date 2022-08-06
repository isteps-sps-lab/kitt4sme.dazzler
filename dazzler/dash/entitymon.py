from abc import ABC, abstractmethod
from typing import Any

from dash import Dash, Input, Output, dcc, html
from dash.development.base_component import Component
import dash_bootstrap_components as dbc
import pandas as pd

from dazzler.dash.wiring import BasePath
from dazzler.dash.timeseries import QuantumLeapSource


INTERVAL_COMPONENT_ID = 'interval-component'
LOAD_BUTTON_ID = 'load-ids-button'
ENTITY_SELECT_ID = 'entity-id'
ENTRIES_INPUT_ID = 'entries-from-latest'
GRAPH_ID = 'graph'


class EntityMonitorDashboard(ABC):

    def __init__(self, app: Dash,
                    title: str, entity_type: str,
                    refresh_rate_millis: int = 5*1000):
        super().__init__()
        self._app = app
        self._title = title
        self._entity_type = entity_type
        self._refresh_rate = refresh_rate_millis
        self._base_path = BasePath.from_board_app(app)
        self._quantumleap = QuantumLeapSource(app)

    @abstractmethod
    def empty_data_set(self) -> dict:
        pass

    @abstractmethod
    def explanation(self) -> str:
        pass

    @abstractmethod
    def make_figure(self, df: pd.DataFrame) -> Any:
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
                            dcc.Graph(id=GRAPH_ID, figure=self._empty_fig()),
                            md=8
                        )
                    ],
                    align="center",
                ),
                dcc.Interval(id=INTERVAL_COMPONENT_ID,
                             interval=self._refresh_rate, n_intervals=0)
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
                        dbc.Button('Load Entity IDs', id=LOAD_BUTTON_ID,
                                    n_clicks=0),
                        md=4
                    ),
                    dbc.Col(
                        dbc.Select(id=ENTITY_SELECT_ID, options=[],
                                    placeholder='Select...'),
                        md=8
                    )
                ]),
                html.P(),
                dbc.Row([
                    dbc.Col(
                        dbc.Input(id=ENTRIES_INPUT_ID, type='number',
                                    value=100, min=1, max=1000, step=1),
                        md=4
                    ),
                    dbc.Col(
                        dbc.Label('entries from latest received data point.'),
                        md=8
                    )
                ])
            ],
            body=True
        )

    def _empty_fig(self) -> Any:
        data = self.empty_data_set()
        df = pd.DataFrame(data).set_index('index')
        return self.make_figure(df)

    def _build_callbacks(self):
        self._app.callback(
            Output(ENTITY_SELECT_ID, 'options'),
            Input(LOAD_BUTTON_ID, 'n_clicks')
        )(self._populate_entity_ids)

        self._app.callback(
            Output(GRAPH_ID, 'figure'),
            Input(INTERVAL_COMPONENT_ID, 'n_intervals'),
            Input(ENTITY_SELECT_ID, 'value'),
            Input(ENTRIES_INPUT_ID, 'value')
        )(self._update_graph)

    def _populate_entity_ids(self, value) -> Any:
        xs = self._quantumleap.fetch_entity_ids(entity_type=self._entity_type)
        return [{'label': x, 'value': x} for x in xs]

    def _update_graph(self, intervals, entity_id, entries_from_latest) -> Any:
        if not entity_id:
            return self._empty_fig()

        df = self._quantumleap.fetch_entity_series(
            entity_id=entity_id, entity_type=self._entity_type,
            entries_from_latest=entries_from_latest
        )
        return self.make_figure(df)
