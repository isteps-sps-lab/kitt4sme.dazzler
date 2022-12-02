# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.
import base64

import cv2
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template
from dash import Dash, html, dcc, Output, Input

THEME = [dbc.themes.SLATE]
load_figure_template("slate")

input_path = "assets/camera.png"


def _update_config(last_configuration):
    img = cv2.imread(input_path)

    # last_configuration = [1, 1, 0, 1, 1, 1, 1, 0, 1]

    positions = {tuple([15, 127, 47, 159]): 0,
                 tuple([126, 54, 158, 86]): 0,
                 tuple([323, 20, 355, 52]): 0,
                 tuple([538, 75, 570, 107]): 0,
                 tuple([355, 154, 387, 186]): 0,
                 tuple([210, 255, 242, 287]): 0,
                 tuple([485, 250, 517, 282]): 0,
                 tuple([150, 368, 182, 400]): 0,
                 tuple([345, 410, 377, 442]): 0}

    for _ in range(len(positions)):
        screw_present = last_configuration[_]
        position = list(positions)[_]
        positions[position] = screw_present
        if screw_present == 1:
            cv2.rectangle(img, (position[0], position[1]),
                          (position[2], position[3]), (0, 255, 0), 5)
        else:
            cv2.rectangle(img, (position[0], position[1]),
                          (position[2], position[3]), (0, 0, 255), 5)

    # cv2.imshow('image', img)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    # cv2.imwrite(output_path, img)

    # return base64.b64encode(open(input_path, 'rb').read()).decode('ascii')
    return base64.b64encode(cv2.imencode('.jpg', img)[1]).decode('ascii')


app = Dash(
    __name__,
    suppress_callback_exceptions=False,
    prevent_initial_callbacks=False,
    external_stylesheets=THEME
)

# assume you have a "long-form" data frame
# see https://plotly.com/python/px-arguments/ for more options
fatigue = pd.DataFrame({
    "Fatigue": [2, 4, 6, 8, 10, 1, 3, 0, 7, 9],
    "Date": ["2022-12-01 13:55:15.000000", "2022-12-01 13:55:18.000000", "2022-12-01 13:55:20.000000",
             "2022-12-01 13:55:22.000000", "2022-12-01 13:55:24.000000", "2022-12-01 13:55:26.000000",
             "2022-12-01 13:55:28.000000", "2022-12-01 13:55:30.000000", "2022-12-01 13:55:32.000000",
             "2022-12-01 13:55:35.000000"]
})

buffer = pd.DataFrame({
    "Buffer": [1, 2, 2, 1, 0, 2, 4],
    "Date": ["2022-12-01 13:55:15.000000", "2022-12-01 13:55:19.000000", "2022-12-01 13:55:21.000000",
             "2022-12-01 13:55:27.000000", "2022-12-01 13:55:29.000000", "2022-12-01 13:55:31.000000",
             "2022-12-01 13:55:33.000000"]
})

# scatters_figure = go.Figure()
# scatters_figure.add_trace(go.Scatter(x=fatigue["Date"], y=fatigue["Fatigue"],
#                                      mode='lines+markers',
#                                      name='Fatigue'))
#
# scatters_figure.add_trace(go.Scatter(x=buffer["Date"], y=buffer["Buffer"],
#                                      mode='lines+markers',
#                                      name='Buffer'))
fatigue_figure = px.line(fatigue, x="Date", y="Fatigue", markers=True, color_discrete_sequence=['coral'])
buffer_figure = px.line(buffer, x="Date", y="Buffer", markers=True, color_discrete_sequence=['silver'])

# fig = go.Figure()
# fig.add_layout_image(
#     dict(
#         source=output_path,
#         xref="x",
#         yref="y",
#         x=-1,
#         y=4,
#         sizex=7,
#         sizey=5,
#         sizing="stretch",
#         opacity=0.5,
#         layer="above")
# )

app.layout = dbc.Container(
    [
        # html.H1(children='KITT4SME Dashboard'),

        # html.Div(children='''
        #     Dash: A web application framework for your data.
        # '''),

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
                                    id='interval-component',
                                    interval=.1 * 1000,  # in milliseconds
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
                                        figure=fatigue_figure
                                    ),
                                    md=6),
                                dbc.Col(
                                    dcc.Graph(
                                        id='buffer',
                                        figure=buffer_figure
                                    ),
                                    md=6
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


@app.callback(Output('config', 'children'),
              Input('interval-component', 'n_intervals'))
def update_metrics(n):
    return [
        html.Img(src='data:image/png;base64,{}'.format(_update_config(np.random.randint(2, size=9)))),
    ]


if __name__ == '__main__':
    app.run_server(debug=True)
