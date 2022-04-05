from dash import Dash, Input, Output, dcc, html
from dash.development.base_component import Component
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px

from dazzler.dash.wiring import BasePath
from dazzler.dash.timeseries import QuantumLeapSource
from dazzler.ngsy import ROUGHNESS_ESTIMATE_TYPE


GRAPH_REFRESH_RATE = 5*1000  # millis

INTERVAL_COMPONENT_ID = 'interval-component'
LOAD_BUTTON_ID = 'load-ids-button'
ENTITY_SELECT_ID = 'entity-id'
ENTRIES_INPUT_ID = 'entries-from-latest'
GRAPH_ID = 'graph'


def dash_builder(app: Dash) -> Dash:
    _build_layout(app)
    _build_callbacks(app)
    return app


def _build_layout(app: Dash):
    app.layout = dbc.Container(
        [
            html.H1('Surface Roughness'),
            html.Hr(),
            dbc.Row(
                [
                    dbc.Col(_build_card(app), md=4),
                    dbc.Col(dcc.Graph(id=GRAPH_ID, figure=_empty_fig()), md=8)
                ],
                align="center",
            ),
            dcc.Interval(
                id=INTERVAL_COMPONENT_ID,
                interval=GRAPH_REFRESH_RATE,
                n_intervals=0
            )
        ],
        fluid=True
    )


def _build_card(app: Dash) -> Component:
    base_path = BasePath.from_board_app(app)

    return dbc.Card(
        [
            html.Div([
                html.H3(base_path.tenant())
            ]),
            html.Div([
                html.H5(f"service path: {base_path.service_path()}")
            ]),
            html.Hr(),
            _build_explanation(),
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


def _build_explanation() -> Component:
    return dcc.Markdown(
        '''
        This graph shows how **acceleration** and **roughness** estimates
        for the selected milling machine vary over time. For each time point
        the graph plots the machine **acceleration** at that time and the
        corresponding **roughness** estimate the AI computed.

        The graph updates automatically every few seconds so you can monitor
        your machine in near real time. To start a monitoring session, load
        the IDs of the machines connected to the system, then select the ID
        of the machine you'd like to monitor. Optionally choose how many data
        points back in time to display from the latest received data point.
        '''
    )


def _build_callbacks(app: Dash):
    app.callback(
        Output(ENTITY_SELECT_ID, 'options'),
        Input(LOAD_BUTTON_ID, 'n_clicks')
    )(_populate_entity_ids(app))

    app.callback(
        Output(GRAPH_ID, 'figure'),
        Input(INTERVAL_COMPONENT_ID, 'n_intervals'),
        Input(ENTITY_SELECT_ID, 'value'),
        Input(ENTRIES_INPUT_ID, 'value')
    )(_update_graph(app))


def _populate_entity_ids(app: Dash):
    def callback(value):
        ql = QuantumLeapSource(app)
        xs = ql.fetch_entity_ids(entity_type=ROUGHNESS_ESTIMATE_TYPE)
        return [{'label': x, 'value': x} for x in xs]

    return callback


def _update_graph(app: Dash):
    def callback(intervals, entity_id, entries_from_latest):
        if not entity_id:
            return _empty_fig()

        ql = QuantumLeapSource(app)
        df = ql.fetch_data_frame(
            entity_id=entity_id, entity_type=ROUGHNESS_ESTIMATE_TYPE,
            entries_from_latest=entries_from_latest
        )
        return _make_figure(df)

    return callback


def _make_figure(df: pd.DataFrame):
    return px.line(df, x=df.index, y=[df.acceleration, df.roughness])


def _empty_fig():
    data = {
        'index': [0],
        'acceleration': [0],
        'roughness': [0]
    }
    df = pd.DataFrame(data).set_index('index')

    return _make_figure(df)
