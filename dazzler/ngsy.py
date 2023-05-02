from typing import Optional

from fipy.ngsi.entity import BaseEntity, BoolAttr, FloatAttr, \
    StructuredValueAttr, Attr
from pydantic import BaseModel


ROUGHNESS_ESTIMATE_TYPE = 'RoughnessEstimate'

class RoughnessEstimateEntity(BaseEntity):
    type = ROUGHNESS_ESTIMATE_TYPE
    acceleration: FloatAttr
    roughness: FloatAttr


INSPECTION_DEMO_TYPE = 'inspection_demo'

class InspectionDemoEntity(BaseEntity):
    type = INSPECTION_DEMO_TYPE
    okay: BoolAttr
    area: FloatAttr


RAW_MATERIAL_INSPECTION_TYPE = 'raw_material'

# class RawMaterialInspectionEntity(BaseEntity):
#     type = RAW_MATERIAL_INSPECTION_TYPE
#     # Inspection_Result: BoolAttr
#     # Area: FloatAttr
#     okay: BoolAttr
#     conformance_indicator: FloatAttr


TWEEZERS_INSPECTION_TYPE = 'tweezers_measurement'

# class TweezersInspectionEntity(BaseEntity):
#     type = TWEEZERS_INSPECTION_TYPE
#     okay: BoolAttr
#     conformance_indicator: FloatAttr
#     spec: TextAttr


INSIGHT_TYPE = 'Insights'

class InsightEntity(BaseEntity):
    type = INSIGHT_TYPE
    Results: Optional[StructuredValueAttr]


WORKER_TYPE = 'Worker'


class Datetime(BaseModel):
    dateTime: str
    format: str
    timezoneId: str


class Fatigue(BaseModel):
    level: FloatAttr
    timestamp: Datetime


class WorkerStates(BaseModel):
    fatigue: Optional[Fatigue]


class WorkerStatesAttr(Attr):
    type = "WorkerStatesProperties"
    value: WorkerStates


class WorkerEntity(BaseEntity):
    type = WORKER_TYPE
    workerStates: Optional[StructuredValueAttr]
