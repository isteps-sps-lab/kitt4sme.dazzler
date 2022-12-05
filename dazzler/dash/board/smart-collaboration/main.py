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
from fipy.ngsi.quantumleap import QuantumLeapClient
from uri import URI

THEME = [dbc.themes.SLATE]
load_figure_template("slate")

input_path = "assets/camera.png"
screw_coords = [(15, 127, 47, 159),
                (126, 54, 158, 86),
                (323, 20, 355, 52),
                (538, 75, 570, 107),
                (355, 154, 387, 186),
                (210, 255, 242, 287),
                (485, 250, 517, 282),
                (150, 368, 182, 400),
                (345, 410, 377, 442)]


def _update_config(last_configuration):
    img = cv2.imread(input_path)

    for position, present in zip(screw_coords, last_configuration):
        if present == 1:
            cv2.rectangle(img, (position[0], position[1]),
                          (position[2], position[3]), (0, 255, 0), 5)
        else:
            cv2.rectangle(img, (position[0], position[1]),
                          (position[2], position[3]), (0, 0, 255), 5)

    return base64.b64encode(cv2.imencode('.jpg', img)[1]).decode('ascii')


app = Dash(
    __name__,
    suppress_callback_exceptions=False,
    prevent_initial_callbacks=False,
    external_stylesheets=THEME
)

_quantumleap = QuantumLeapClient(
    base_url=URI("http://quantumleap:8668"),
    ctx=FiwareContext(
        # service=base_path.tenant(),
        service_path="/"
    )
)

app.layout = dbc.Container(
    [
        html.H1("Self-assignment dashboard"),

        dbc.Row(
            [
                dbc.Col(
                    # dbc.Card(
                    dcc.Markdown(
                        '''
                                This graph shows the current levels of **fatigue** and **buffer**.
                                Also, it shows to the operator the current screw-driving configuration (
                                **green boxes** are assigned to the operator)
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
                                    dcc.Graph(
                                        id='fatigue',
                                    ),
                                    md=6),
                                dbc.Col(
                                    dcc.Graph(
                                        id='buffer',
                                    ),
                                    md=6
                                ),
                                dcc.Interval(
                                    id='graphs-interval',
                                    interval=1 * 1000,  # in milliseconds
                                    n_intervals=0
                                )
                            ],
                            align="center",
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


@app.callback(Output('config', 'children'),
              Input('config-interval', 'n_intervals'))
def update_config(n):
    return [
        html.Img(src='data:image/png;base64,{}'.format(_update_config(np.random.randint(2, size=9)))),
    ]


@app.callback(Output('fatigue', 'figure'),
              Input('graphs-interval', 'n_intervals'))
def update_fatigue(n):
    fatigue = fetch_entity_series(
        entity_id="12345", entity_type="Worker",
        entries_from_latest=10,
        # from_timepoint=datetime.now() - timedelta(seconds=60) - timedelta(hours=1),
        # to_timepoint=datetime.now() - timedelta(hours=1)
    )

    fatigue = fatigue.workerStates.apply(lambda x: x["fatigue"]["level"]["value"] if x else x).rename("Fatigue")

    return px.line(fatigue, x=fatigue.index, y="Fatigue", markers=True, color_discrete_sequence=['coral'])


@app.callback(Output('buffer', 'figure'),
              Input('graphs-interval', 'n_intervals'))
def update_buffer(n):
    buffer = fetch_entity_series(
        entity_id="EquipmentIoTMeasurement1", entity_type="EquipmentIoTMeasurement",
        entries_from_latest=10,
        # from_timepoint=datetime.now() - timedelta(seconds=60) - timedelta(hours=1),
        # to_timepoint=datetime.now() - timedelta(hours=1)
    )

    buffer = buffer.fields.apply(lambda x: x["bufferLevel"]["t2"] if x else x).rename("Buffer")

    return px.line(buffer, x=buffer.index, y="Buffer", markers=True, color_discrete_sequence=['silver'])


if __name__ == '__main__':
    app.run_server(debug=True)
