from fipy.ngsi.entity import BaseEntity, BoolAttr, FloatAttr, TextAttr


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
