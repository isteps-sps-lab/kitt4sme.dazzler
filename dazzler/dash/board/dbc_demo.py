"""
Dash Bootstrap Template Demo.
Adapted from
- https://hellodash.pythonanywhere.com/figure_templates
"""
from dash import Dash, dcc, html
from dash.dependencies import Input, Output
from dash.development.base_component import Component
import plotly.express as px
import dash_bootstrap_components as dbc


def dash_builder(app: Dash) -> Dash:
    figs = _mk_figures()
    _build_layout(app, figs)
    _build_callbacks(app)
    return app


def _mk_figures() -> dict:
    df = px.data.gapminder()
    figs = {}

    dff = df[df.year.between(1952, 1982)]
    dff = dff[dff.continent.isin(df.continent.unique()[1:])]
    figs['line_fig'] = px.line(
        dff, x="year", y="gdpPercap", color="continent", line_group="country"
    )

    dff = dff[dff.year == 1982]
    figs['scatter_fig'] = px.scatter(
        dff, x="lifeExp", y="gdpPercap", size="pop", color="pop", size_max=60
    ).update_traces(marker_opacity=0.8)

    avg_lifeExp = (dff["lifeExp"] * dff["pop"]).sum() / dff["pop"].sum()
    figs['map_fig'] = px.choropleth(
        dff,
        locations="iso_alpha",
        color="lifeExp",
        title="%.0f World Average Life Expectancy was %.1f years" %
                (1982, avg_lifeExp)
    )

    figs['hist_fig'] = px.histogram(dff, x="lifeExp", nbins=10,
                                    title="Life Expectancy")

    return figs


def _build_layout(app: Dash, figs: dict):
    app.layout = dbc.Container(
        [_mk_heading(), _mk_buttons(), _mk_echo_widget(), _mk_graphs(**figs)],
        fluid=True)


def _mk_heading() -> Component:
    return html.H1(
        "Dash Bootstrap Template Demo",
        className="bg-primary text-white p-2")


# These buttons are added to the app just to show the Boostrap theme colors.
def _mk_buttons() -> Component:
    bs = [
        dbc.Button("Primary", color="primary"),
        dbc.Button("Secondary", color="secondary"),
        dbc.Button("Success", color="success"),
        dbc.Button("Warning", color="warning"),
        dbc.Button("Danger", color="danger"),
        dbc.Button("Info", color="info"),
        dbc.Button("Light", color="light"),
        dbc.Button("Dark", color="dark"),
        dbc.Button("Link", color="link")
    ]
    return html.Div(bs)


def _mk_graphs(line_fig, scatter_fig, hist_fig, map_fig) -> Component:
    rs = [
        dbc.Row(
            [
                dbc.Col(dcc.Graph(figure=line_fig), lg=6),
                dbc.Col(dcc.Graph(figure=scatter_fig), lg=6),
            ],
            className="mt-4",
        ),
        dbc.Row(
            [
                dbc.Col(dcc.Graph(figure=hist_fig), lg=6),
                dbc.Col(dcc.Graph(figure=map_fig), lg=6),
            ],
            className="mt-4",
        ),
    ]
    return html.Div(rs)


def _mk_echo_widget() -> Component:
    xs = [
        dcc.Input(id='echo_input', type='text',
                  value='type something in here to see it echoed...'),
        html.Div(id='echo_output')
    ]
    return html.Div(xs)


def _build_callbacks(app: Dash):
    app.callback(
        Output(component_id='echo_output', component_property='children'),
        [Input(component_id='echo_input', component_property='value')]
    )(echo_input)


def echo_input(input_value: str) -> str:
    return f"You typed: {input_value}"
