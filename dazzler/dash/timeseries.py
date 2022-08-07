from datetime import datetime
from typing import Dict, List, Optional

from dash import Dash
from fipy.ngsi.headers import FiwareContext
from fipy.ngsi.entity import BaseEntity
from fipy.ngsi.quantumleap import QuantumLeapClient
import pandas as pd
from uri import URI

from dazzler.config import dazzler_config
from dazzler.dash.wiring import BasePath


def fiware_context_for(app: Dash) -> FiwareContext:
    base_path = BasePath.from_board_app(app)
    return FiwareContext(
        service=base_path.tenant(),
        service_path=base_path.service_path()
    )


class QuantumLeapSource:

    def __init__(self, app: Dash):
        cfg = dazzler_config()
        self._client = QuantumLeapClient(
            base_url=URI(str(cfg.quantumleap_base_url)),
            ctx=fiware_context_for(app)
        )

    def fetch_entity_series(self,
            entity_id: str, entity_type: str,
            entries_from_latest: Optional[int] = None,
            from_timepoint: Optional[datetime] = None,
            to_timepoint: Optional[datetime] = None) -> pd.DataFrame:
        r = self._client.entity_series(
            entity_id=entity_id, entity_type=entity_type,
            entries_from_latest=entries_from_latest,
            from_timepoint=from_timepoint, to_timepoint=to_timepoint
        )
        time_indexed_df = pd.DataFrame(r.dict()).set_index('index')
        return time_indexed_df

    def fetch_entity_type_series(self,
            entity_type: str,
            entries_from_latest: Optional[int] = None,
            from_timepoint: Optional[datetime] = None,
            to_timepoint: Optional[datetime] = None) -> Dict[str, pd.DataFrame]:
        rs = self._client.entity_type_series(
            entity_type=entity_type,
            entries_from_latest=entries_from_latest,
            from_timepoint=from_timepoint, to_timepoint=to_timepoint
        )
        frames = {
            entity_id : (pd.DataFrame(series.dict()))
            for (entity_id, series) in rs.items()
        }
        return frames

    def fetch_entity_summaries(self, entity_type: Optional[str] = None) \
        -> List[BaseEntity]:
        return self._client.list_entities(entity_type=entity_type)

    def fetch_entity_ids(self, entity_type: str) -> List[str]:
        xs = self.fetch_entity_summaries(entity_type=entity_type)
        return [x.id for x in xs]
