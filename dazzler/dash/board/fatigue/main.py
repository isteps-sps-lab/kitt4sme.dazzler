# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.
import base64
from datetime import datetime, timedelta
from typing import Optional

import cv2
import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
import plotly.express as px
from dash import Dash, html, dcc, Output, Input
from dash_bootstrap_templates import load_figure_template
from fipy.ngsi.headers import FiwareContext
from fipy.ngsi.orion import OrionClient
from fipy.ngsi.quantumleap import QuantumLeapClient
from uri import URI

from entities import TaskExecutionEntity

THEME = [dbc.themes.SLATE]
load_figure_template("slate")

app = Dash(
    __name__,
    suppress_callback_exceptions=False,
    prevent_initial_callbacks=False,
    external_stylesheets=THEME
)

_orion_client = OrionClient(
    URI("http://sps-lab01.supsi.ch:8006"),
    FiwareContext(service=None, service_path=None, correlator=None))

# all_time_series
_quantumleap = QuantumLeapClient(
    base_url=URI("http://sps-lab01.supsi.ch:8008"),
    ctx=FiwareContext(
        # service=base_path.tenant(),
        service_path="/"
    )
)

app.layout = dbc.Container(
    [
        html.H1("Worker cells monitoring dashboard"),

        dbc.Row(
            [
                dbc.Col(
                    # dbc.Card(
                    dcc.Markdown(
                        '''
                                This graph shows the current levels of **fatigue** for each worker assigned to
                                the related production cell.
                        '''
                    ),
                    # body=False
                    # ),
                    md=12),
                html.Hr(),
                dbc.Col(
                    [
                        dbc.Row(
                            [
                                html.Center(id='config'),
                                dcc.Interval(
                                    id='config-interval',
                                    interval=5 * 1000,  # in milliseconds
                                    n_intervals=0
                                )
                            ],
                            align="center"
                        ),
                        # html.Hr(),
                        html.Br(),
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        html.H3("Cell 1"),
                                        dcc.Graph(
                                            id='fatigue_1',
                                        ),
                                        html.Br(),
                                        dcc.Graph(
                                            id='fatigue_4',
                                        ),
                                    ],
                                    md=4,
                                ),
                                dbc.Col(
                                    [
                                        html.H3("Cell 2"),
                                        dcc.Graph(
                                            id='fatigue_2',
                                        ),
                                        html.Br(),
                                        dcc.Graph(
                                            id='fatigue_5',
                                        ),
                                    ],
                                    md=4,
                                ),
                                dbc.Col(
                                    [
                                        html.H3("Cell 3"),
                                        dcc.Graph(
                                            id='fatigue_3',
                                        ),
                                        html.H3(""),
                                    ],
                                    md=4,
                                ),
                                dcc.Interval(
                                    id='graphs-interval',
                                    interval=1 * 1000,  # in milliseconds
                                    n_intervals=0
                                )
                            ],
                        ),
                    ],
                    md=12
                ),
            ]
        ),
    ],
    fluid=False
)


def fetch_entity_series(entity_id: str, entity_type: str,
                        entries_from_latest: Optional[int] = None,
                        from_timepoint: Optional[datetime] = None,
                        to_timepoint: Optional[datetime] = None) -> pd.DataFrame:
    r = _quantumleap.entity_series(
        entity_id=entity_id, entity_type=entity_type,
        entries_from_latest=entries_from_latest,
        from_timepoint=from_timepoint, to_timepoint=to_timepoint
    )
    time_indexed_df = pd.DataFrame(r.dict()).set_index('index')
    return time_indexed_df


@app.callback(Output('fatigue_1', 'figure'),
              Input('graphs-interval', 'n_intervals'))
def update_fatigue_1(n):
    worker_id = "worker1"
    fatigue = fetch_entity_series(
        entity_id=worker_id, entity_type="Worker",
        entries_from_latest=10,
        # from_timepoint=datetime.now() - timedelta(seconds=60) - timedelta(hours=1),
        # to_timepoint=datetime.now() - timedelta(hours=1)
    )

    fatigue = fatigue.workerStates.apply(lambda x: x["fatigue"]["level"] if x else x).rename("Fatigue")

    return px.line(fatigue, title=worker_id, x=fatigue.index, y="Fatigue", markers=True, color_discrete_sequence=['coral'])


@app.callback(Output('fatigue_2', 'figure'),
              Input('graphs-interval', 'n_intervals'))
def update_fatigue_2(n):
    worker_id = "worker2"
    fatigue = fetch_entity_series(
        entity_id=worker_id, entity_type="Worker",
        entries_from_latest=10,
        # from_timepoint=datetime.now() - timedelta(seconds=60) - timedelta(hours=1),
        # to_timepoint=datetime.now() - timedelta(hours=1)
    )

    fatigue = fatigue.workerStates.apply(lambda x: x["fatigue"]["level"] if x else x).rename("Fatigue")

    return px.line(fatigue, title=worker_id, x=fatigue.index, y="Fatigue", markers=True, color_discrete_sequence=['coral'])


@app.callback(Output('fatigue_3', 'figure'),
              Input('graphs-interval', 'n_intervals'))
def update_fatigue_3(n):
    worker_id = "worker3"
    fatigue = fetch_entity_series(
        entity_id=worker_id, entity_type="Worker",
        entries_from_latest=10,
        # from_timepoint=datetime.now() - timedelta(seconds=60) - timedelta(hours=1),
        # to_timepoint=datetime.now() - timedelta(hours=1)
    )

    fatigue = fatigue.workerStates.apply(lambda x: x["fatigue"]["level"] if x else x).rename("Fatigue")

    return px.line(fatigue, title=worker_id, x=fatigue.index, y="Fatigue", markers=True, color_discrete_sequence=['coral'])


@app.callback(Output('fatigue_4', 'figure'),
              Input('graphs-interval', 'n_intervals'))
def update_fatigue_4(n):
    worker_id = "worker4"
    fatigue = fetch_entity_series(
        entity_id=worker_id, entity_type="Worker",
        entries_from_latest=10,
        # from_timepoint=datetime.now() - timedelta(seconds=60) - timedelta(hours=1),
        # to_timepoint=datetime.now() - timedelta(hours=1)
    )

    fatigue = fatigue.workerStates.apply(lambda x: x["fatigue"]["level"] if x else x).rename("Fatigue")

    return px.line(fatigue, title=worker_id, x=fatigue.index, y="Fatigue", markers=True, color_discrete_sequence=['coral'])


@app.callback(Output('fatigue_5', 'figure'),
              Input('graphs-interval', 'n_intervals'))
def update_fatigue_5(n):
    worker_id = "worker5"
    fatigue = fetch_entity_series(
        entity_id=worker_id, entity_type="Worker",
        entries_from_latest=10,
        # from_timepoint=datetime.now() - timedelta(seconds=60) - timedelta(hours=1),
        # to_timepoint=datetime.now() - timedelta(hours=1)
    )

    fatigue = fatigue.workerStates.apply(lambda x: x["fatigue"]["level"] if x else x).rename("Fatigue")

    return px.line(fatigue, title=worker_id, x=fatigue.index, y="Fatigue", markers=True, color_discrete_sequence=['coral'])


if __name__ == '__main__':
    app.run_server(debug=True)
