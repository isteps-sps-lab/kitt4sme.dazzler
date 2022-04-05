from uri import URI
from typing import Generator, List

from fipy.ngsi.headers import FiwareContext
from fipy.ngsi.quantumleap import QuantumLeapClient
from fipy.sim.generator import bool_attr, float_attr_close_to, \
    EntityFactory, entity_batch
from fipy.wait import wait_for_quantumleap

from dazzler.ngsy import RawMaterialInspectionEntity, RoughnessEstimateEntity


TENANT = 'demo'
QUANTUMLEAP_INTERNAL_BASE_URL = 'http://quantumleap:8668'
QUANTUMLEAP_EXTERNAL_BASE_URL = 'http://localhost:8668'


def quantumleap_client() -> QuantumLeapClient:
    base_url = URI(QUANTUMLEAP_EXTERNAL_BASE_URL)
    ctx = FiwareContext(service=TENANT, service_path='/')  # (*)
    return QuantumLeapClient(base_url, ctx)
# NOTE. Orion handling of empty service path. We send Orion entities w/ no
# service path in our tests. But when Orion notifies QL, it sends along a
# root service path. So we add it to the context to make queries work.


def wait_on_quantumleap():
    wait_for_quantumleap(quantumleap_client())


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


def mk_raw_material_inspection() -> RawMaterialInspectionEntity:
    return RawMaterialInspectionEntity(
        id = '',
        Inspection_Result=bool_attr(),
        Area=float_attr_close_to(36.1)
    )


def mk_raw_material_inspection_batches_stream() \
    -> Generator[List[RawMaterialInspectionEntity], None, None]:
    factory = EntityFactory.with_numeric_suffixes(
        how_many=2, generator=mk_raw_material_inspection
    )
    return entity_batch(factory)


raw_material_inspection_batches_stream = \
    mk_raw_material_inspection_batches_stream()
