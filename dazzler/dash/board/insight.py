from curses import raw
from typing import Any, List

from pydantic import BaseModel


class IgFeature(BaseModel):
    """A named float value in a result matrix produced by Insight Generator.
    Notice the data that makes up a named float is stored in matrix form
    inside the NGSI structured value. This class represents that information
    in a format that's best for displaying in our dashboard.
    """
    name: str
    value: float


class IgRecommendation(BaseModel):
    """A recommendation in a result matrix produced by Insight Generator.
    Notice the data that makes up a recommendation is stored in matrix
    form inside the NGSI structured value. This class represents that
    information in a format that's best for displaying in our dashboard.
    """
    kpi_name: str
    features: List[IgFeature]
    kpi_best: float


class IgRecommendationMatrix:
    """Converts a result matrix produced by Insight Generator to a format
    that's best for displaying in our dashboard.
    """

    def __init__(self, results: dict):
        """Create a new instance to convert the input matrix data.

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
