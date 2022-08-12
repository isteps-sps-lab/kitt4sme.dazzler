from typing import Any, List

import dash_bootstrap_components as dbc
from dash import Dash, Input, Output, dcc, html
import pandas as pd
import plotly.express as px

from dazzler.dash.board.insight.model import *
from dazzler.dash.board.insight.datasource import *


class RecommendationRenderer:
    """Builds the widgets to display an `IgRecommendation` on screen.
    """

    def __init__(self, data: IgRecommendation) -> None:
        self._data = data

    @staticmethod
    def make_reco_table_row(feature: IgFeature) -> html.Tr:
        return html.Tr([html.Td(feature.name), html.Td(f"{feature.value}")])

    def make_reco_table(self) -> dbc.Table:
        header = html.Thead(html.Tr(
                    [html.Th("Parameter / Variable"), html.Th("Value")]))
        rows = [self.make_reco_table_row(f)
                for f in self._data.features]
        body = html.Tbody(rows)

        return dbc.Table([header, body], bordered=True, dark=True, hover=True,
                         responsive=True, striped=True)

    def make_estimated_optimum_toast(self) -> dbc.Toast:
        optimal_value = f"{self._data.kpi_name} = {self._data.kpi_best}"
        return dbc.Toast(
            [html.P(optimal_value, className="mb-0")],
            header="Estimated optimal value"
        )

    def make_reco_card(self) -> dbc.Card:
        return dbc.Card([
            html.H4("Recommended Actions / Optimal settings",
                    className="card-title"),
            self.make_reco_table(),
            self.make_estimated_optimum_toast()
        ], body=True)


class RecommendationTabContent:
    """Builds a tab widget to display an `IgRecommendation` on screen and
    plot the corresponding KPI value evolution over time.
    """

    def __init__(self, recommendation: IgRecommendation,
                 kpi_data: pd.DataFrame):
        self._reco = recommendation
        self._kpi_data = kpi_data

    def figure_id(self) -> str:
        return f"fig-{self._reco.kpi_name}"

    def make_figure(self) -> Any:
        color_map = {self._reco.kpi_name: 'coral'}
        return px.line(self._kpi_data,
                       x=self._kpi_data.index, y=[self._reco.kpi_name],
                       color_discrete_map=color_map)

    def make_tab_content(self) -> dbc.Card:
        kpi_graph = dcc.Graph(id=self.figure_id(), figure=self.make_figure())
        reco_card = RecommendationRenderer(self._reco).make_reco_card()
        return dbc.Card([kpi_graph, html.P(), reco_card], body=True)


class RecommendationTabs:
    """Builds a tab group widget to host a tab for each `IgRecommendation`
    extracted from an Insight Generator result table found in a given NGSI
    entity. Each tab also displays a graph that plots the evolution over
    time of the KPI the recommendation is about.
    """

    def __init__(self, analyses: List[IgAnalysis]):
        self._analyses = analyses

    @staticmethod
    def make_tab(reco: IgRecommendation, kpi_data: pd.DataFrame) -> dbc.Tab:
        content = RecommendationTabContent(reco, kpi_data).make_tab_content()
        return dbc.Tab(content, label=reco.kpi_name)

    def make_tabs(self) -> dbc.Tabs:
        ts = [self.make_tab(a.recommendation(), a.kpi_over_time())
              for a in self._analyses]
        return dbc.Tabs(ts)


class RecommendationDashboard:
    """Builds the Dash UI and acts as a controller for it, handling UI
    events.
    """

    LOAD_BUTTON_ID = 'load-ids-button'
    ENTITY_SELECT_ID = 'entity-id'
    ANALYSIS_TABS_CONTAINER_ID = 'analysis-tabs'

    def __init__(self, app: Dash, datasource: IgDataSource):
        self._app = app
        self._datasource = datasource
        self._title = 'Insight Generator Report'

    def build_dash_app(self) -> Dash:
        self._build_layout()
        self._build_callbacks()
        return self._app

    def _build_layout(self):
        self._app.layout = dbc.Container(
            [
                html.H1(self._title),
                html.Hr(),
                dbc.Row(
                    [
                        dbc.Col(self._build_card(), md=4),
                        dbc.Col(self._build_tabs_container(), md=8)
                    ],
                    align='top',
                )
            ],
            fluid=True
        )

    def _build_card(self) -> dbc.Card:
        return dbc.Card(
            [
                html.Div([
                    html.H3(self._datasource.tenant())
                ]),
                html.Div([
                    html.H5(f"service path: {self._datasource.service_path()}")
                ]),
                html.Hr(),
                dcc.Markdown(RECOMMENDATION_DASHBOARD_EXPLANATION),
                html.Hr(),
                dbc.Row([
                    dbc.Col(
                        dbc.Button('Load Entity IDs', id=self.LOAD_BUTTON_ID,
                                    n_clicks=0),
                        md=4
                    ),
                    dbc.Col(
                        dbc.Select(id=self.ENTITY_SELECT_ID, options=[],
                                    placeholder='Select...'),
                        md=8
                    )
                ])
            ],
            body=True
        )

    def _build_tabs_container(self) -> html.Div:
        return html.Div([], id=self.ANALYSIS_TABS_CONTAINER_ID)

    def _populate_tabs(self, value: str) -> dbc.Tabs:
        xs = self._datasource.load_analyses_for(value)
        return RecommendationTabs(xs).make_tabs()

    def _populate_entity_ids(self, value) -> List[dict]:
        xs = self._datasource.load_insight_entity_ids()
        return [{'label': x, 'value': x} for x in xs]

    def _build_callbacks(self):
        self._app.callback(
            Output(self.ENTITY_SELECT_ID, 'options'),
            Input(self.LOAD_BUTTON_ID, 'n_clicks')
        )(self._populate_entity_ids)

        self._app.callback(
            Output(self.ANALYSIS_TABS_CONTAINER_ID, 'children'),
            Input(self.ENTITY_SELECT_ID, 'value')
        )(self._populate_tabs)


def dash_builder(app: Dash) -> Dash:
    datasource = IgDemoDataSource(app)  # TODO IgDataSource(app)
    board = RecommendationDashboard(app, datasource)
    return board.build_dash_app()
# TODO. When we know what to do for KPI graphs, use IgDataSource instead
# of the demo data!


RECOMMENDATION_DASHBOARD_EXPLANATION = '''
This dashboard renders Insight Generator reports. Each report is made
up by a set of recommended settings for each KPI Insight Generator
analysed as well as recent KPI evolution over time.

To display a report, press the "Load Entity IDs" button, then select
the ID of the report you're interested in from the drop down menu on
the right of the button. A group of tabs will appear on the right of
the dashboard containing the report data.

There's a tab for each KPI Insight Generator analysed. The tab contains
a graph plotting the KPI values over time. Below the graph are the
parameter settings Insight Generator recommends to optimise the KPI.
The expected KPI value after applying the recommended settings is
shown below the parameter table.
'''
