from fipy.ngsi.entity import BaseEntity, BoolAttr, FloatAttr


ROUGHNESS_ESTIMATE_TYPE = 'RoughnessEstimate'

class RoughnessEstimateEntity(BaseEntity):
    type = ROUGHNESS_ESTIMATE_TYPE
    acceleration: FloatAttr
    roughness: FloatAttr


RAW_MATERIAL_INSPECTION_TYPE = 'Raw_Material'

class RawMaterialInspectionEntity(BaseEntity):
    type = RAW_MATERIAL_INSPECTION_TYPE
    Inspection_Result: BoolAttr
    Area: FloatAttr
