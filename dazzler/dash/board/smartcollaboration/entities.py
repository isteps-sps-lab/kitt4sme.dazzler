import datetime
import random
from typing import Optional, Generator, List

import numpy as np
from fipy.ngsi.entity import BaseEntity, TextAttr, FloatAttr, StructuredValueAttr
from fipy.sim.generator import EntityFactory, entity_batch
from pydantic import Field


class TaskExecutionEntity(BaseEntity):
    type = 'TaskExecution'
    # target_id: Optional[StringAttr] = Field(alias='targetId')
    creationTimestamp: Optional[TextAttr]
    additionalParameters: Optional[StructuredValueAttr]
    taskName: Optional[TextAttr]
    duration: Optional[FloatAttr]
    iteration: Optional[FloatAttr]


class WorkerEntity(BaseEntity):
    type = 'Worker'
    workerStates: Optional[StructuredValueAttr]


class EquipmentIoTMeasurementEntity(BaseEntity):
    type = 'EquipmentIoTMeasurement'
    fields: Optional[StructuredValueAttr]


def mk_smart_collaboration_task_demo() -> TaskExecutionEntity:
    return TaskExecutionEntity(
        id='',
        creationTimestamp=TextAttr.new(datetime.datetime.now().isoformat()),
        additionalParameters=StructuredValueAttr.new({"sequence": np.random.randint(2, size=9).tolist()}),
        taskName=TextAttr.new("ScrewAssignment"),
        duration=FloatAttr.new(0),
        iteration=FloatAttr.new(1),
    )


def mk_smart_collaboration_worker_demo() -> WorkerEntity:
    return WorkerEntity(
        id='',
        workerStates=StructuredValueAttr.new({"fatigue": {"level": FloatAttr.new(random.randint(0, 10))}}),
    )


def mk_smart_collaboration_iot_demo() -> EquipmentIoTMeasurementEntity:
    return EquipmentIoTMeasurementEntity(
        id='',
        fields=StructuredValueAttr.new({"bufferLevel": {"t1": "NUMBER", "t2": random.randint(0, 4)}}),
    )


def mk_smart_collaboration_demo_task_batches_stream() -> Generator[List[TaskExecutionEntity], None, None]:
    factory = EntityFactory.with_numeric_suffixes(
        how_many=2, generator=mk_smart_collaboration_task_demo
    )
    return entity_batch(factory)


def mk_smart_collaboration_demo_worker_batches_stream() -> Generator[List[WorkerEntity], None, None]:
    factory = EntityFactory.with_numeric_suffixes(
        how_many=2, generator=mk_smart_collaboration_worker_demo
    )
    return entity_batch(factory)


def mk_smart_collaboration_demo_iot_batches_stream() -> Generator[List[EquipmentIoTMeasurementEntity], None, None]:
    factory = EntityFactory.with_numeric_suffixes(
        how_many=2, generator=mk_smart_collaboration_iot_demo
    )
    return entity_batch(factory)


smart_collaboration_demo_task_batches_stream = mk_smart_collaboration_demo_task_batches_stream()
smart_collaboration_demo_worker_batches_stream = mk_smart_collaboration_demo_worker_batches_stream()
smart_collaboration_demo_iot_batches_stream = mk_smart_collaboration_demo_iot_batches_stream()
