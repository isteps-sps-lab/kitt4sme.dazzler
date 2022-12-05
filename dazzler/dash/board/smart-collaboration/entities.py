from typing import Any, Optional

from fipy.ngsi.entity import BaseEntity, TextAttr, Attr
from pydantic import Field


class IntAttr(Attr):
    type = 'Integer'
    value: int


class StringAttr(Attr):
    type = 'String'
    value: dict
    metadata: Any


class MapAttr(Attr):
    type = 'Map'
    value: dict
    metadata: Any


class TaskExecutionEntity(BaseEntity):
    type = 'TaskExecution'
    # target_id: Optional[StringAttr] = Field(alias='targetId')
    creation_timestamp: Optional[TextAttr] = Field(alias='creationTimestamp')
    additional_parameters: Optional[MapAttr] = Field(alias='additionalParameters')
    task_name: Optional[TextAttr] = Field(alias='taskName')
    duration: Optional[IntAttr]
    iteration: Optional[IntAttr]

    class Config:
        allow_population_by_field_name = True


# class TaskExecutionProperties(BaseModel):
#     target_id: TextAttr = Field(alias='targetId')
#     creation_timestamp: TextAttr = Field(alias='creationTimestamp')
#     additional_parameters: MapAttr = Field(alias='additionalParameters')
#     task_name: TextAttr = Field(alias='taskName')
#     duration: IntAttr
#     iteration: IntAttr
#
#
# class TaskExecutionPropertiesAttribute(Attr):
#     type = "TaskExecutionProperties"
#     value: TaskExecutionProperties
#
#
# class TaskExecutionEntity(BaseEntity):
#     type = 'TaskExecution'
#     task_execution_properties: Optional[TaskExecutionPropertiesAttribute] = Field(alias='taskExecutionProperties')
#
#     class Config:
#         allow_population_by_field_name = True
