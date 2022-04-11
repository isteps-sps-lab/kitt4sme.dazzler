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
from itertools import dropwhile, islice, takewhile
from pathlib import PurePosixPath
from typing import Callable, Generator

from dash import Dash
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template
from fastapi import FastAPI
from fastapi.middleware.wsgi import WSGIMiddleware
from flask import Flask

from dazzler.config import BoardAssembly, Settings


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
            suppress_callback_exceptions=False,
            prevent_initial_callbacks=True,
            external_stylesheets=THEME
        )

    def assemble(self, builder: DashBuilder, tenant_name: str,
                service_path: str = '/', board_path: str = '/'):
        """Instantiate a Dash dashboard, delegate its filling with app logic
        and widgets, then wire it into FastAPI.
        The Dash app base path will be in the format detailed in `BasePath`.

        Args:
            builder: factory function to populate the dashboard with widgets
                and app logic.
            tenant_name: the name of the tenant the Dash app is for.
            service_path: Optional FIWARE service path.
            board_path: Optional dashboard path. Use this to run different
                dashboard apps for the same tenant.
        """
        base_path = str(BasePath(tenant_name, service_path, board_path))
        dashapp = builder(self._make_board(base_path))
        self._app.mount(base_path, WSGIMiddleware(dashapp.server))

    def mount_dashboards(self, config: Settings):
        """Create and mount a Dash dashboard app on FastAPI for each dashboard
        assembly description found in the given configuration settings.

        Args:
            config: Dazzler configuration settings.
        """
        for args in DashboardsConfig(config).assemble_args():
            self.assemble(**args)


class DashboardsConfig:
    """Streams dashboard assembly settings from configuration.

    The `assemble_args` method produces a stream where each element is a
    dictionary containing the arguments `DashboardSubApp.assemble` takes
    in, read from the corresponding fields in the Dazzler settings.
    """

    def __init__(self, config: Settings):
        self._cfg = config.boards

    @staticmethod
    def _args_from_config(tenant_name: str, board_spec: BoardAssembly) -> dict:
        args = {
            'tenant_name': tenant_name,
            'builder': board_spec.builder
        }
        if board_spec.service_path:
            args['service_path'] = board_spec.service_path
        if board_spec.board_path:
            args['board_path'] = board_spec.board_path

        return args

    def assemble_args(self) -> Generator[dict, None, None]:
        """Produce a stream where each element is a dictionary containing
        the arguments `DashboardSubApp.assemble` takes in, read from the
        corresponding fields in the Dazzler settings.

        Yields:
            The next dictionary in the stream.
        """
        for tenant_name in self._cfg:
            for board_spec in self._cfg[tenant_name]:
                yield self._args_from_config(tenant_name, board_spec)


class BasePath:
    """Base URL from where the dashboard app will be served.
    This class makes sure the path is in the format
    ```
        DAZZLER_ROOT / tenant_name / service_path /-/ board_path
    ```
    where the service and board paths are optional. Also notice Dash wants
    base paths to start and end with a '/' which this class enforces when
    converting to string.
    """

    DAZZLER_ROOT = '/dazzler'
    BOARD_PATH_SEPARATOR = '-'

    @staticmethod
    def from_board_app(app: Dash) -> 'BasePath':
        proto = BasePath(tenant_name='x')
        proto._path = PurePosixPath(app.config.requests_pathname_prefix)
        return proto
    # NOTE. This works as long as the DashboardSubApp always uses BasePath
    # to configure Dash's requests_pathname_prefix. Have a look at the
    # DashboardSubApp's class implementation for the details.

    @staticmethod
    def _make_relative(path: str) -> PurePosixPath:
        p = PurePosixPath(path)
        return p.relative_to(p.anchor)
    # NOTE. Stripping leading '/'.
    # Using the above trick if there's a leading '/', it gets removed. If the
    # path isn't absolute, then it's returned as is. We do this b/c if you
    # join two absolute paths, then you only get the second path.
    # See: https://stackoverflow.com/questions/50846049

    @staticmethod
    def _build_base_path(tenant_name: str, service_path: str,
                         board_path: str) -> PurePosixPath:
        root = PurePosixPath(BasePath.DAZZLER_ROOT)
        tenant = BasePath._make_relative(tenant_name)
        svc = BasePath._make_relative(service_path)
        board = BasePath._make_relative(board_path)

        return root / tenant / svc / BasePath.BOARD_PATH_SEPARATOR / board

    @staticmethod
    def _not_board_path_sep(path_component: str) -> bool:
        return path_component != BasePath.BOARD_PATH_SEPARATOR

    def __init__(self, tenant_name: str, service_path: str = '/',
                 board_path: str = '/'):
        assert len(tenant_name) > 0
        self._path = self._build_base_path(tenant_name, service_path,
                                           board_path)

    def __str__(self) -> str:
        return str(self._path) + '/'
    # NOTE. Dash base paths. They must end with a '/' which is why we
    # append it here.

    def tenant(self) -> str:
        return self._path.parts[2]

    def service_path(self) -> str:
        path_after_tenant = self._path.parts[3:]
        svc_path_components = takewhile(self._not_board_path_sep,
                                        path_after_tenant)
        ps = [f"/{p}" for p in svc_path_components]
        return ''.join(ps) + '/'

    def dashboard_path(self) -> str:
        path_after_tenant = self._path.parts[3:]
        svc_path_components = dropwhile(self._not_board_path_sep,
                                        path_after_tenant)
        ps = [f"/{p}" for p in islice(svc_path_components, 1, None)]
        return ''.join(ps) + '/'
