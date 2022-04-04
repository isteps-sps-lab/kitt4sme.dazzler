from dash import Dash, html
import dash_bootstrap_components as dbc

from dazzler.dash.wiring import BasePath


def dash_builder(app: Dash) -> Dash:
    _build_layout(app)
    _build_callbacks(app)
    return app


def _build_layout(app: Dash):
    app.layout = dbc.Container(
        [
            html.H1("Roughnator Dashboard"),
            html.Hr(),
            html.H3(f"tenant: {BasePath.from_board_app(app).tenant()}"),
            html.H3(f"sp: {BasePath.from_board_app(app).service_path()}")
        ]
    )


def _build_callbacks(app: Dash):
    pass
