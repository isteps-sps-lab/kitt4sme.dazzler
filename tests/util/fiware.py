import datetime
import random

from uri import URI
from typing import Generator, List

from fipy.ngsi.entity import StructuredValueAttr, FloatAttr
from fipy.ngsi.headers import FiwareContext
from fipy.ngsi.orion import OrionClient
from fipy.ngsi.quantumleap import QuantumLeapClient
from fipy.sim.generator import BoolAttr, float_attr_close_to, \
    EntityFactory, entity_batch

from dazzler.dash.board.insight.datasource import \
    example_ngsi_structured_value_1, example_ngsi_structured_value_2
from dazzler.ngsy import InsightEntity, InspectionDemoEntity, \
    RoughnessEstimateEntity, WorkerEntity, WorkerStatesAttr, Datetime, Fatigue, WorkerStates

TENANT = 'demo'
QUANTUMLEAP_INTERNAL_BASE_URL = 'http://quantumleap:8668'
QUANTUMLEAP_EXTERNAL_BASE_URL = 'http://localhost:8668'
ORION_EXTERNAL_BASE_URL = 'http://localhost:1026'


def quantumleap_client() -> QuantumLeapClient:
    base_url = URI(QUANTUMLEAP_EXTERNAL_BASE_URL)
    ctx = FiwareContext(service=TENANT, service_path='/')  # (*)
    return QuantumLeapClient(base_url, ctx)
# NOTE. Orion handling of empty service path. We send Orion entities w/ no
# service path in our tests. But when Orion notifies QL, it sends along a
# root service path. So we add it to the context to make queries work.

def orion_client() -> OrionClient:
    base_url = URI(ORION_EXTERNAL_BASE_URL)
    ctx = FiwareContext(service=TENANT, service_path='/')
    return OrionClient(base_url, ctx)


def mk_roughness_estimate() -> RoughnessEstimateEntity:
    return RoughnessEstimateEntity(
        id = '',
        acceleration=float_attr_close_to(5.07),
        roughness=float_attr_close_to(1.25),
    )


def mk_roughness_estimate_batches_stream() \
    -> Generator[List[RoughnessEstimateEntity], None, None]:
    factory = EntityFactory.with_numeric_suffixes(
        how_many=2, generator=mk_roughness_estimate
    )
    return entity_batch(factory)


roughness_estimate_batches_stream = mk_roughness_estimate_batches_stream()


def mk_inspection_demo() -> InspectionDemoEntity:
    area = float_attr_close_to(0)
    okay = BoolAttr.new(area.value >= 0.4)
    return InspectionDemoEntity(
        id = '',
        okay=okay,
        area=area
    )


def mk_inspection_demo_batches_stream() \
    -> Generator[List[InspectionDemoEntity], None, None]:
    factory = EntityFactory.with_numeric_suffixes(
        how_many=2, generator=mk_inspection_demo
    )
    return entity_batch(factory)


inspection_demo_batches_stream = mk_inspection_demo_batches_stream()


class InsightEntityGenerator:

    def __init__(self):
        self.count = -1
        self.payload = [ example_ngsi_structured_value_1(),
                         example_ngsi_structured_value_2() ]

    def mk_demo(self) -> InsightEntity:
        self.count = self.count + 1
        value = self.payload[self.count % 2]
        return InsightEntity(
            id='',
            Results=StructuredValueAttr.new(value)
        )


def mk_insight_demo_batches_stream() \
    -> Generator[List[InsightEntity], None, None]:
    factory = EntityFactory.with_numeric_suffixes(
        how_many=2, generator=InsightEntityGenerator().mk_demo
    )
    return entity_batch(factory)


insight_demo_batches_stream = mk_insight_demo_batches_stream()


def mk_fams_worker_demo() -> WorkerEntity:
    return WorkerEntity(
        id='',
        workerStates=WorkerStatesAttr.new(
            WorkerStates(
                fatigue=Fatigue(
                    level=FloatAttr.new(random.randint(0, 10)),
                    timestamp=Datetime(
                        dateTime=datetime.datetime.now().isoformat(),
                        format="ISO",
                        timezoneId="UTC"
                    )
                )
            )
        ),
    )


def mk_fams_demo_worker_batches_stream() -> Generator[List[WorkerEntity], None, None]:
    factory = EntityFactory.with_numeric_suffixes(
        how_many=6, generator=mk_fams_worker_demo
    )
    return entity_batch(factory)


fams_demo_worker_batches_stream = mk_fams_demo_worker_batches_stream()
