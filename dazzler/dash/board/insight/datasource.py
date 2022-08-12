from typing import List

from dash import Dash

from dazzler.dash.board.insight.model import *
from dazzler.dash.wiring import BasePath
from dazzler.dash.timeseries import QuantumLeapSource
from dazzler.ngsy import INSIGHT_TYPE


class IgDataSource:

    def __init__(self, app: Dash):
        self._base_path = BasePath.from_board_app(app)
        self._quantumleap = QuantumLeapSource(app)

    def tenant(self) -> str:
        return self._base_path.tenant()

    def service_path(self) -> str:
        return self._base_path.service_path()

    def load_insight_entity_ids(self) -> List[str]:
        ids = self._quantumleap.fetch_entity_ids(entity_type=INSIGHT_TYPE)
        return ids

    def load_analyses_for(self, entity_id: str) -> List[IgAnalysis]:
        df = self._quantumleap.fetch_entity_series(
            entity_id=entity_id, entity_type=INSIGHT_TYPE,
            entries_from_latest=1
        )
        ngsi_results = df.get('Results', {}).get(0, {})
        recos = IgRecommendationTable(ngsi_results).to_recommendations()
        kpis = []  # TODO where are the KPI datasets supposed to come from?!

        return [IgAnalysis(r, k) for (r, k) in zip(recos, kpis)]

# TODO. Clarify what data KPI graphs should plot. The CSIC mockup seem to
# plot the KPI best value as a constant function of time---i.e. k(t) = best.
# Not sure that's what they meant, so another possibility is that for each
# KPI listed in the Results structured value, there's a corresponding time
# series to fetch. This is what we do in the implementation of the demo
# datasource, but obviously, that's just my interpretation which could be
# wrong!


class IgDemoDataSource(IgDataSource):

    def __init__(self, app: Dash):
        super().__init__(app)
        self._data = {
            'urn:ngsi:IG:1': make_example_analyses(
                example_ngsi_structured_value_1()
            ),
            'urn:ngsi:IG:2': make_example_analyses(
                example_ngsi_structured_value_2()
            )
        }

    def load_insight_entity_ids(self) -> List[str]:
        return [entity_id for entity_id in self._data]

    def load_analyses_for(self, entity_id: str) -> List[IgAnalysis]:
        return self._data.get(entity_id, [])


def example_ngsi_structured_value_1() -> dict:
    return {
		"KPI_name": ["Throughput", "Scrap", "Roughness"],
		"features_names":[
            ["ae", "fz", "Diam"],
            ["Diam", "fz", "ae", "HB"],
            ["AcelR", "Ra"]
        ],
		"features_values":[
            [2.86, 0.102, 10.21],
            [14.46, 0.05, 1.36, 88.9],
            [1.0335, -2.75]
        ],
		"KPI_best": ["163.37", "2.0", "1.03"]
	}


def example_ngsi_structured_value_2() -> dict:
    return {
		"KPI_name": ["Throughput", "Scrap"],
		"features_names":[
            ["ae", "fz", "Diam"],
            ["Diam", "fz", "ae", "HB"]
        ],
		"features_values":[
            [2.86, 0.102, 10.21],
            [14.46, 0.05, 1.36, 88.9]
        ],
		"KPI_best": ["163.37", "0.0"]
	}


def make_example_kpi_over_time(kpi_name: str, kpi_best: float) -> pd.DataFrame:
    from datetime import datetime
    from random import uniform

    raw_tix = [
        "2022-03-28T18:03:18.923+00:00", "2022-03-28T18:03:20.458+00:00",
        "2022-03-28T18:03:22.011+00:00", "2022-03-28T18:03:24.011+00:00",
        "2022-03-28T18:03:26.011+00:00", "2022-03-28T18:03:28.011+00:00"
    ]
    data = {
        'index': [datetime.fromisoformat(t) for t in raw_tix],
        kpi_name: [uniform(kpi_best - 10, kpi_best + 10) for _ in raw_tix]
    }
    return pd.DataFrame(data=data).set_index('index')


def make_example_analyses(ngsi_results: dict) -> List[IgAnalysis]:
    recos = IgRecommendationTable(ngsi_results).to_recommendations()
    kpis = [make_example_kpi_over_time(r.kpi_name, r.kpi_best) for r in recos]

    return [IgAnalysis(r, k) for (r, k) in zip(recos, kpis)]
