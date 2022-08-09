from abc import abstractmethod
from typing import Any, Dict, List

from dash import Dash
import pandas as pd
import plotly.express as px
from pydantic import BaseModel

from dazzler.dash.entitiesframe import EntitiesFrameDashboard
from dazzler.ngsy import RAW_MATERIAL_INSPECTION_TYPE, TWEEZERS_INSPECTION_TYPE


class InspectionReport(BaseModel):
    """Holds the data to visualise a VIQE inspection report.
    There's two types of VIQE reports, raw materials and tweezers, and an
    NGSI entity type for each one. But this class collapses the two types
    into one, more convenient representation for plotting data.
    """
    id: str
    conformance: float
    scrap: bool
    spec: str

    @staticmethod
    def empty() -> 'InspectionReport':
        return InspectionReport(
            id='', conformance=0, scrap=False, spec=''
        )


class ReportFrame:
    """Converts the entity type series dictionary retrieved from Quantum
    Leap to a Pandas data frame we can plot.
    """

    def __init__(self, entity_type_series: Dict[str, pd.DataFrame]):
        self._frames = entity_type_series

    @staticmethod
    def _most_recent_row(entity_series: pd.DataFrame) -> pd.Series:
        max_time_index = entity_series['index'].idxmax()
        return entity_series.iloc[max_time_index]

# NOTE. Paranoia. There should always be exactly one inspection for each
# entity ID since the inspection is a one-off kind of thing done on one
# item and item ID == entity ID. But we do this just in case sometime
# down the line someone decided to have multiple reports for one item,
# e.g. think doing an inspection on the same item again b/c instruments
# were out of whack during the first inspection.

    @staticmethod
    def _from_entity_series(entity_id: str, frame: pd.DataFrame) \
                            -> InspectionReport:
        report = InspectionReport.empty()
        report.id = entity_id

        payload = ReportFrame._most_recent_row(frame)
        report.conformance = payload.get('conformance_indicator', 1)
        report.scrap = not payload.get('okay', False)
        report.spec = payload.get('spec', '')

        return report

    def build(self) -> pd.DataFrame:
        rows = [self._from_entity_series(entity_id, frame).dict()
                for (entity_id, frame) in self._frames.items()]
        return pd.DataFrame(rows)


class InspectionDashboard(EntitiesFrameDashboard):

    def empty_data_frame(self) -> pd.DataFrame:
        rows = [InspectionReport.empty().dict()]
        return pd.DataFrame(rows)

    def entity_type_series_to_data_frame(self,
                                         frames: Dict[str, pd.DataFrame]) \
                                        -> pd.DataFrame:
        if frames:
            return ReportFrame(frames).build()
        return self.empty_data_frame()  # no data, draw empty plot

    def make_figure(self, frames: Dict[str, pd.DataFrame]) -> Any:
        df = self.entity_type_series_to_data_frame(frames)
        color_map = {True: 'coral', False: 'silver'}
        fig = px.bar(df, x=df.id, y=df.conformance,
                        color='scrap',
                        color_discrete_map=color_map,
                        hover_data=self._bar_hover_extra_fields())
        fig.update_layout(legend_title_text='Scrap?')
        return fig

    @abstractmethod
    def _bar_hover_extra_fields(self) -> List[str]:
        pass


class RawMaterialInspectionDashboard(InspectionDashboard):

    def __init__(self, app: Dash):
        super().__init__(
            app=app,
            title='Raw Materials Inspection',
            entity_type=RAW_MATERIAL_INSPECTION_TYPE
        )

    def _bar_hover_extra_fields(self) -> List[str]:
        return []

    def explanation(self) -> str:
        return \
        '''
        This graph visualises raw material inspections VIQE did in the
        selected time interval.
        Each inspection refers to a specific raw material item which is
        identified by an ID label. There's a bar on the graph for each
        ID. The bar indicates the degree to which the inspected item conforms
        to the spec. Zero means no significant deviations from the spec,
        one means the item is probably to be scrapped. The spec determines
        a conformance threshold `t` in `(0, 1)` so items with a value less
        or equal to `t` conform to the spec whereas values greater than
        `t` do not. Accordingly, a grey bar means "below or equal to the
        threshold", whereas orange means "above the threshold".

        To plot inspections, select a time interval and then click on
        the "Load Entities" button.
        '''


class TweezersInspectionDashboard(InspectionDashboard):

    def __init__(self, app: Dash):
        super().__init__(
            app=app,
            title='Tweezers Inspection',
            entity_type=TWEEZERS_INSPECTION_TYPE
        )

    def _bar_hover_extra_fields(self) -> List[str]:
        return ['spec']

    def explanation(self) -> str:
        return \
        '''
        This graph visualises tweezers inspections VIQE did in the selected
        time interval.
        Each inspection refers to a specific tweezers which is identified by
        an ID label. There's a bar on the graph for each ID. The bar indicates
        the degree to which the inspected item conforms to the spec. Zero means
        no significant deviations from the spec, one means the item is probably
        to be scrapped. The spec determines a conformance threshold `t` in
        `(0, 1)` so items with a value less or equal to `t` conform to the spec
        whereas values greater than `t` do not. Accordingly, a grey bar means
        "below or equal to the threshold", whereas orange means "above the
        threshold". To see which spec VIQE checked a pair of tweezers against,
        just hover over the corresponding bar in the graph with the mouse.

        To plot inspections, select a time interval and then click on the
        "Load Entities" button.
        '''

def raw_material_dash_builder(app: Dash) -> Dash:
    return RawMaterialInspectionDashboard(app).build_dash_app()


def tweezers_dash_builder(app: Dash) -> Dash:
    return TweezersInspectionDashboard(app).build_dash_app()
