from typing import Any

from dash import Dash
import pandas as pd
import plotly.express as px

from dazzler.dash.entitymon import EntityMonitorDashboard
from dazzler.ngsy import RAW_MATERIAL_INSPECTION_TYPE


def dash_builder(app: Dash) -> Dash:
    return ViqeDashboard(app).build_dash_app()


class ViqeDashboard(EntityMonitorDashboard):

    def __init__(self, app: Dash):
        super().__init__(
            app=app,
            title='Defect Size',
            entity_type=RAW_MATERIAL_INSPECTION_TYPE
        )

    def empty_data_set(self) -> dict:
        return {
            'index': [0],
            'Area': [0],
            'Inspection_Result': [False]
        }

    def explanation(self) -> str:
        return \
        '''
        This graph visualises VIQE inspection reports as they come in.
        Each report is for a part being machined and is made up by a
        sequence of part surface areas where defects are likely to be.
        There's a bubble on the graph for each surface area where VIQE
        thinks there could be a defect, each bubble size is proportional
        to the corresponding real-world size of the area inspected on the
        part and orange bubbles indicate highly likely defects.

        The graph updates automatically every few seconds so you can monitor
        your machining process in near real time. To start a monitoring
        session, load the IDs of the available VIQE reports, then pick the
        one you're interested in. Optionally choose how many data points
        back in time to display from the latest received data point.
        '''

    def make_figure(self, df: pd.DataFrame) -> Any:
        color_map = {True: 'coral', False: 'silver'}
        fig = px.scatter(df, x=df.index, y=df.Area, size=df.Area,
                            color='Inspection_Result',
                            color_discrete_map=color_map)
        fig.update_layout(legend_title_text='Defect?')
        return fig
