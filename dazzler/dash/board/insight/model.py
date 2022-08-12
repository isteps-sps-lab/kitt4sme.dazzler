from typing import Any, List

import pandas as pd
from pydantic import BaseModel


class IgFeature(BaseModel):
    """A named float value in a result matrix produced by Insight Generator.
    Notice the data that makes up a named float is stored in columnar format
    inside the NGSI structured value. This class represents that information
    in a format that's best for displaying in our dashboard.
    """
    name: str
    value: float


class IgRecommendation(BaseModel):
    """A recommendation in a result matrix produced by Insight Generator.
    Notice the data that makes up a recommendation is stored in columnar
    format inside the NGSI structured value. This class represents that
    information in a format that's best for displaying in our dashboard.
    """
    kpi_name: str
    features: List[IgFeature]
    kpi_best: float


class IgRecommendationTable:
    """Converts a result table produced by Insight Generator to a format
    that's best for displaying in our dashboard.
    """

    def __init__(self, results: dict):
        """Create a new instance to convert the input table.

        Args:
            results: the value of the `Results` attribute of an NGSI
                `Insights` entity produced by Insight Generator.
        """
        self._results = results

    def _extract(self, field: str) -> List[Any]:
        return self._results.get(field, [])

    @staticmethod
    def _to_features(names: List[str], values: List[float]) -> List[IgFeature]:
        arg_tuples = zip(names, values)
        features = [IgFeature(name=n, value=v) for (n, v) in arg_tuples]
        return features

    def to_recommendations(self) -> List[IgRecommendation]:
        """Convert the payload of the given `Results` NGSI attribute to
        a list of `IgRecommendation`.

        Returns:
            the list of recommendations extracted from the NGSI
            `StructuredValue`.
        """
        raw_features = zip(self._extract('features_names'),
                           self._extract('features_values'))
        features = [self._to_features(ns, vs) for (ns, vs) in raw_features]

        arg_tuples = zip(
            self._extract('KPI_name'),
            features,
            self._extract('KPI_best')
        )
        rs = [IgRecommendation(kpi_name=n, features=fs, kpi_best=float(b))
              for (n, fs, b) in arg_tuples]

        return rs


class IgAnalysis:
    """Holds an Insight Generator recommendation for a KPI as well as
    a data frame containing the evolution of that KPI value over time.
    """

    def __init__(self, recommendation: IgRecommendation,
                 kpi_over_time: pd.DataFrame):
        """Create a new instance to hold a KPI recommendation and the KPI
        evolution over time.

        Notice for the dashboard to be able to plot the KPI over time, the
        Pandas data frame must have the following structure:
            * it holds data for a function `k(t)`---KPI value of time
            * the `t` is the 'index' column which also has to be the Pandas
              index
            * `k(t)` is a column whose name is the same as
              `recommendation.kpi_name`

        Args:
            recommendation: the Insight Generator recommendation for a KPI.
            kpi_over_time: the latest KPI values recorded, usually for the
                last 100 time points.
        """
        self._reco = recommendation
        self._kpi = kpi_over_time

    def recommendation(self) -> IgRecommendation:
        return self._reco

    def kpi_over_time(self) -> pd.DataFrame:
        return self._kpi
