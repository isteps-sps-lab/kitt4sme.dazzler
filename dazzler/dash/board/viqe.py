from dash import Dash, html
import dash_bootstrap_components as dbc


def dash_builder(app: Dash) -> Dash:
    _build_layout(app)
    _build_callbacks(app)
    return app


def _build_layout(app: Dash):
    app.layout = dbc.Container(
        [
            html.H1("VIQE Dashboard")
        ]
    )


def _build_callbacks(app: Dash):
    pass
