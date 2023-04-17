from time import sleep

from fipy.docker import DockerCompose
from fipy.ngsi.orion import OrionClient
from fipy.ngsi.quantumleap import QuantumLeapClient

from tests.util.fiware import quantumleap_client, \
    inspection_demo_batches_stream, roughness_estimate_batches_stream, \
    orion_client, insight_demo_batches_stream, fams_demo_worker_batches_stream

docker = DockerCompose(__file__)


def bootstrap():
    docker.build_images()
    docker.start()


def send_entities(quantumleap: QuantumLeapClient, orion: OrionClient):
    try:
        batch = next(insight_demo_batches_stream)
        orion.upsert_entities(batch)

        batch = next(roughness_estimate_batches_stream) + \
                next(inspection_demo_batches_stream) + \
                next(fams_demo_worker_batches_stream)
        quantumleap.insert_entities(batch)
    except Exception as e:
        print(e)


def run():
    services_running = False
    quantumleap = quantumleap_client()
    orion = orion_client()
    sampling_rate = 5.0
    try:
        bootstrap()
        services_running = True

        print('>>> sending entities to Quantum Leap and Orion...')
        while True:
            sleep(sampling_rate)
            send_entities(quantumleap, orion)

    except KeyboardInterrupt:
        if services_running:
            docker.stop()
