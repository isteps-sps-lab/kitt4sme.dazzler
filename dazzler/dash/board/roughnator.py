from typing import Any

from dash import Dash
import pandas as pd
import plotly.express as px

from dazzler.dash.entitymon import EntityMonitorDashboard
from dazzler.ngsy import ROUGHNESS_ESTIMATE_TYPE


def dash_builder(app: Dash) -> Dash:
    return RoughnatorDashboard(app).build_dash_app()


class RoughnatorDashboard(EntityMonitorDashboard):

    def __init__(self, app: Dash):
        super().__init__(
            app=app,
            title='Surface Roughness',
            entity_type=ROUGHNESS_ESTIMATE_TYPE
        )

    def empty_data_set(self) -> dict:
        return {
            'index': [0],
            'acceleration': [0],
            'roughness': [0]
        }

    def explanation(self) -> str:
        return \
        '''
        This graph shows how **acceleration** and **roughness** estimates
        for the selected milling machine vary over time. For each time point
        the graph plots the machine **acceleration** at that time and the
        corresponding **roughness** estimate the AI computed.

        The graph updates automatically every few seconds so you can monitor
        your machine in near real time. To start a monitoring session, load
        the IDs of the machines connected to the system, then select the ID
        of the machine you'd like to monitor. Optionally choose how many data
        points back in time to display from the latest received data point.
        '''

    def make_figure(self, df: pd.DataFrame) -> Any:
        color_map = {'roughness': 'coral', 'acceleration': 'silver'}
        return px.line(df, x=df.index, y=[df.acceleration, df.roughness],
                        color_discrete_map=color_map)
