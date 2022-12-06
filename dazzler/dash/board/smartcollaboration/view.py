import base64
import os
from datetime import datetime
from typing import Optional

import cv2
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from dash import Dash, html, dcc, Output, Input
from fipy.ngsi.headers import FiwareContext
from fipy.ngsi.orion import OrionClient
from fipy.ngsi.quantumleap import QuantumLeapClient
from uri import URI

from dazzler.dash.board.smartcollaboration.entities import TaskExecutionEntity


def dash_builder(app: Dash) -> Dash:
    return SmartCollaborationDashboard(app).build_dash_app()


class SmartCollaborationDashboard:

    def __init__(self, app: Dash):
        print()
        self._app = app
        self._input_path = f"{os.path.dirname(os.path.realpath(__file__))}/assets/camera.png"
        self._screw_coords = [(15, 127, 47, 159),
                              (126, 54, 158, 86),
                              (323, 20, 355, 52),
                              (538, 75, 570, 107),
                              (355, 154, 387, 186),
                              (210, 255, 242, 287),
                              (485, 250, 517, 282),
                              (150, 368, 182, 400),
                              (345, 410, 377, 442)]
        self._orion_client = OrionClient(
            URI("http://quantumleap:8668"),
            FiwareContext(service=None, service_path=None, correlator=None))

        self._quantumleap = QuantumLeapClient(
            base_url=URI("http://orion:1026"),
            ctx=FiwareContext(
                # service=base_path.tenant(),
                service_path="/"
            )
        )

    def build_dash_app(self) -> Dash:
        self._build_layout()
        self._build_callbacks()
        return self._app

    def _build_layout(self):
        self._app.layout = dbc.Container(
            [
                html.H1("Self-assignment dashboard"),

                dbc.Row(
                    [
                        dbc.Col(
                            # dbc.Card(
                            dcc.Markdown(
                                '''
                                        This graph shows the current levels of **fatigue** and **buffer**.
                                        Also, it shows to the operator the current screw-driving configuration
                                        (**green boxes** are assigned to the operator)
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
                                        html.Center([
                                            html.Img(src=f'data:image/png;base64,{base64.b64encode(cv2.imencode(".jpg", cv2.imread(self._input_path))[1]).decode("ascii")}'),
                                        ], id='config'),
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

    def _build_callbacks(self):
        self._app.callback(
            Output('config', 'children'),
            Input('config-interval', 'n_intervals'),
        )(self._update_config)

        self._app.callback(
            Output('fatigue', 'figure'),
            Input('graphs-interval', 'n_intervals'),
        )(self._update_fatigue)

        self._app.callback(
            Output('buffer', 'figure'),
            Input('graphs-interval', 'n_intervals'),
        )(self._update_buffer)

    def _fetch_entity_series(self, entity_id: str, entity_type: str,
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

    def _update_config(self, n):
        interventions = self._orion_client.list_entities_of_type(TaskExecutionEntity(id=''))  # todo read from dashboard
        intervention = interventions[len(interventions) - 1]
        last_configuration = intervention.additional_parameters.value["sequence"]
        img = cv2.imread(self._input_path)
        for position, present in zip(self._screw_coords, last_configuration):
            if present == 1:
                cv2.rectangle(img, (position[0], position[1]),
                              (position[2], position[3]), (0, 255, 0), 5)
            else:
                cv2.rectangle(img, (position[0], position[1]),
                              (position[2], position[3]), (0, 0, 255), 5)

        img_base64 = base64.b64encode(cv2.imencode('.jpg', img)[1]).decode('ascii')

        return [
            html.Img(src=f'data:image/png;base64,{img_base64}'),
        ]

    def _update_fatigue(self, _):
        fatigue = self._fetch_entity_series(
            entity_id="12345",  # todo read from dashboard
            entity_type="Worker",
            entries_from_latest=10,
            # from_timepoint=datetime.now() - timedelta(seconds=60) - timedelta(hours=1),
            # to_timepoint=datetime.now() - timedelta(hours=1)
        )

        fatigue = fatigue.workerStates.apply(lambda x: x["fatigue"]["level"]["value"] if x else x).rename("Fatigue")

        return px.line(fatigue, x=fatigue.index, y="Fatigue", markers=True, color_discrete_sequence=['coral'])

    def _update_buffer(self, _):
        buffer = self._fetch_entity_series(
            entity_id="EquipmentIoTMeasurement1",  # todo read from dashboard
            entity_type="EquipmentIoTMeasurement",
            entries_from_latest=10,
            # from_timepoint=datetime.now() - timedelta(seconds=60) - timedelta(hours=1),
            # to_timepoint=datetime.now() - timedelta(hours=1)
        )

        buffer = buffer.fields.apply(lambda x: x["bufferLevel"]["t2"] if x else x).rename("Buffer")

        return px.line(buffer, x=buffer.index, y="Buffer", markers=True, color_discrete_sequence=['silver'])
