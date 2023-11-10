import dash_bootstrap_components as dbc
from dash import Dash, html, dcc, Output, Input

from dazzler.dash.board.smart_collaboration import SmartCollaborationDashboard


def dash_builder(app: Dash) -> Dash:
    return SmartCollaborationLightDashboard(app).build_dash_app()


class SmartCollaborationLightDashboard(SmartCollaborationDashboard):

    def __init__(self, app: Dash):
        super().__init__(app)
        self._image_width = "75%"

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
                                dbc.Row([
                                    html.H1("Assigned screws: -", className="display-1", id='config-number'),
                                ]),
                                dbc.Row(
                                    [
                                        html.Center(
                                            self._config_fig(),
                                            id='config'
                                        ),
                                    ],
                                    align="center",
                                    # class_name="mb-3",  # bottom spacing
                                )
                            ],
                            md=12
                        ),
                    ],
                ),
                dcc.Interval(
                    id='config-interval',
                    interval=1 * 1000,  # in milliseconds
                    n_intervals=0
                )
            ],
            fluid=False,
            # class_name='p-3'  # padding
        )

    def _update_config_number(self, n_intervals):
        return [
            html.H1(f"Assigned screws: {self._fetch_last_config().count(1)}", className="display-1"),
        ]

    def _build_callbacks(self):
        self._app.callback(
            Output('config', 'children'),
            Input('config-interval', 'n_intervals'),
        )(self._update_config)

        self._app.callback(
            Output('config-number', 'children'),
            Input('config-interval', 'n_intervals'),
        )(self._update_config_number)
