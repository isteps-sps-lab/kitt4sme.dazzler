import base64
import os

import cv2
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from dash import Dash, html, dcc, Output, Input

from dazzler.dash.board.smartcollaboration.entities import TaskExecutionEntity
from dazzler.dash.fiware import QuantumLeapSource, OrionSource
from dazzler.dash.wiring import BasePath


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
        self._orion = OrionSource(app)
        self._quantumleap = QuantumLeapSource(app)
        self._base_path = BasePath.from_board_app(app)

    def build_dash_app(self) -> Dash:
        self._build_layout()
        self._build_callbacks()
        return self._app

    def _build_layout(self):
        self._app.layout = dbc.Container(
            [
                dbc.Row([
                    html.H1(self._base_path.tenant()),
                    html.H2(f"service path: {self._base_path.service_path()}"),
                    dcc.Markdown(
                        '''
                                This graph shows the current levels of **fatigue** and **buffer**.
                                Also, it shows to the operator the current screw-driving configuration
                                (**green boxes** are assigned to the operator)
                        '''
                    ),
                ]),
                html.Hr(),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Row(
                                    [
                                        html.Center([
                                            html.Img(src=self._config_fig()),
                                        ], id='config'),
                                        dcc.Interval(
                                            id='config-interval',
                                            interval=5 * 1000,  # in milliseconds
                                            n_intervals=0
                                        )
                                    ],
                                    align="center",
                                    class_name="mb-3",  # bottom spacing
                                ),
                                dbc.Row(
                                    [
                                        dbc.Col([
                                            dbc.Select(
                                                id='config-worker-id',
                                                # todo read options from orion
                                                options=[{'label': 'urn:ngsi-ld:Worker:1',
                                                          'value': 'urn:ngsi-ld:Worker:1'}],
                                                placeholder='Select worker...'),
                                            dcc.Graph(
                                                id='fatigue',
                                                figure=self._fatigue_fig()
                                            )],
                                            md=6),
                                        dbc.Col([
                                            dbc.Select(
                                                id='config-iot-id',
                                                # todo read options from orion
                                                options=[{'label': 'urn:ngsi-ld:EquipmentIoTMeasurement:1',
                                                          'value': 'urn:ngsi-ld:EquipmentIoTMeasurement:1'}],
                                                placeholder='Select equipment iot...'),
                                            dcc.Graph(
                                                id='buffer',
                                                figure=self._buffer_fig()
                                            )],
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
                    ],
                ),
            ],
            fluid=False,
            class_name='p-3'  # padding
        )

    def _build_callbacks(self):
        self._app.callback(
            Output('config', 'children'),
            Input('config-interval', 'n_intervals'),
        )(self._update_config)

        self._app.callback(
            Output('fatigue', 'figure'),
            Input('config-interval', 'n_intervals'),
            Input('config-worker-id', 'value'),
        )(self._update_fatigue)

        self._app.callback(
            Output('buffer', 'figure'),
            Input('config-interval', 'n_intervals'),
            Input('config-iot-id', 'value'),
        )(self._update_buffer)

    def _update_config(self, n_intervals):
        task_execution = TaskExecutionEntity(id='')
        interventions = self._orion.fetch_entity_ids(task_execution.type)  # todo read ID from dashboard
        task_execution.id = interventions[-1]
        intervention = self._orion.fetch_entity(task_execution)
        last_configuration = intervention.additionalParameters.value["sequence"]
        img = cv2.imread(self._input_path)
        for position, present in zip(self._screw_coords, last_configuration):
            if present == 1:
                cv2.rectangle(img, (position[0], position[1]),
                              (position[2], position[3]), (0, 255, 0), 5)
            else:
                cv2.rectangle(img, (position[0], position[1]),
                              (position[2], position[3]), (0, 0, 255), 5)

        return [
            html.Img(src=self._config_fig(img)),
        ]

    def _update_fatigue(self, n_intervals, worker_entity_id):
        if not worker_entity_id:
            return self._fatigue_fig()

        fatigue = self._quantumleap.fetch_entity_series(
            entity_id=worker_entity_id,
            entity_type="Worker",
            entries_from_latest=10,
            # from_timepoint=datetime.now() - timedelta(seconds=60) - timedelta(hours=1),
            # to_timepoint=datetime.now() - timedelta(hours=1)
        )

        fatigue = fatigue.workerStates.apply(lambda x: x["fatigue"]["level"]["value"] if x else x).rename("fatigue")
        return self._fatigue_fig(fatigue)

    def _update_buffer(self, n_intervals, iot_entity_id):
        if not iot_entity_id:
            return self._buffer_fig()

        buffer = self._quantumleap.fetch_entity_series(
            entity_id=iot_entity_id,
            entity_type="EquipmentIoTMeasurement",
            entries_from_latest=10,
            # from_timepoint=datetime.now() - timedelta(seconds=60) - timedelta(hours=1),
            # to_timepoint=datetime.now() - timedelta(hours=1)
        )

        buffer = buffer.fields.apply(lambda x: x["bufferLevel"]["t2"] if x else x).rename("buffer")

        return self._buffer_fig(buffer)

    def _config_fig(self, img=None):
        if img is None:  # The truth value of a Series is ambiguous
            img = cv2.imread(self._input_path)

        return f"data:image/png;base64,{base64.b64encode(cv2.imencode('.jpg', img)[1]).decode('ascii')}"

    def _fatigue_fig(self, df=None):
        if df is None:  # The truth value of a Series is ambiguous
            empty_fatigue = {
                'timestamp': [],
                'fatigue': [],
            }
            df = pd.DataFrame(empty_fatigue).set_index('timestamp')
        return px.line(df, x=df.index, y="fatigue", markers=True, color_discrete_sequence=['coral'])

    def _buffer_fig(self, df=None):
        if df is None:  # The truth value of a Series is ambiguous
            empty_buffer = {
                'timestamp': [],
                'buffer': [],
            }
            df = pd.DataFrame(empty_buffer).set_index('timestamp')
        return px.line(df, x=df.index, y='buffer', markers=True, color_discrete_sequence=['silver'])
