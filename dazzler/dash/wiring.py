"""
Wiring of Dash apps into FastAPI.

A Dash app can only run in a Flash server container. Since we use FastAPI
as a Web app framework, we need a way to serve Flask containers from
FastAPI. Luckily Flask containers are WSGI apps and FastAPI lets you
serve any WSGI app by "mounting" it as a "sub-app" on a URL below the
root. That's done through `WSGIMiddleware`s:

- https://fastapi.tiangolo.com/advanced/wsgi/

And that's basically what we do here. We put every Dash app into its
own Flask container instance and then wrap the Flask instance with a
WSGIMiddleware we then connect to the FastAPI Web container.

See also:
- https://github.com/rusnyder/fastapi-plotly-dash
- https://towardsdatascience.com/embed-multiple-dash-apps-in-flask-with-microsoft-authenticatio-44b734f74532
"""
from typing import Callable

from dash import Dash
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template
from fastapi import FastAPI
from fastapi.middleware.wsgi import WSGIMiddleware
from flask import Flask


DashBuilder = Callable[[Dash], Dash]
"""Factory to build a Dash dashboard.
Every dashboard we have has to provide an implementation of this function.
We build the Dash instance in the `wiring` module (so we can wire it into
FastAPI), pass it into the function and ask it to populate it with widgets
and dashboard logic.
"""

THEME = [dbc.themes.SLATE]
load_figure_template("slate")  # (*) see NOTE below.
# NOTE. Theming.
# We load our themed figure template from dash-bootstrap-templates, add
# it to plotly.io and make it the default figure template. Then we select
# a matching Bootstrap theme for best UI results---see DashboardSubApp.


class DashboardSubApp:
    """Wires Dash apps into a FastAPI container."""

    def __init__(self, app: FastAPI, flask_app_name: str):
        """Create a new instance to do the wiring.

        Args:
            app: FastAPI container instance where to put dashboard apps.
            flask_app_name: the name of the Flask container in which to
                host the Dash dashboards. Every dashboards gets its own
                Flask instance, but all instances are named the same, i.e.
                the value of this parameter.
        """
        self._app = app
        self._flask_app_name = flask_app_name

    def _make_board(self, base_path: str) -> Dash:
        flask_app = Flask(self._flask_app_name)
        return Dash(
            server=flask_app,
            # url_base_pathname=base_path,
            requests_pathname_prefix=base_path,
            suppress_callback_exceptions=True,
            external_stylesheets=THEME
        )

    def assemble(self, base_path: str, builder: DashBuilder):
        """Instantiate a Dash dashboard, delegate its filling with app logic
        and widgets, then wire it into FastAPI.

        Args:
            base_path: base URL from where the dashboard app will be served.
                Needs to start and end with a '/'.
            builder: factory function to populate the dashboard with widgets
                and app logic.
        """
        dashapp = builder(self._make_board(base_path))
        self._app.mount(base_path, WSGIMiddleware(dashapp.server))
