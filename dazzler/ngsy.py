from fipy.ngsi.entity import BaseEntity, BoolAttr, FloatAttr


class RoughnessEstimateEntity(BaseEntity):
    type = 'RoughnessEstimate'
    acceleration: FloatAttr
    roughness: FloatAttr


class RawMaterialInspectionEntity(BaseEntity):
    type = 'Raw_Material'
    Inspection_Result: BoolAttr
    Area: FloatAttr
