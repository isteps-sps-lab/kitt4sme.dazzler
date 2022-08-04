from time import sleep

from fipy.docker import DockerCompose
from fipy.ngsi.quantumleap import QuantumLeapClient

from tests.util.fiware import quantumleap_client, \
    inspection_demo_batches_stream, roughness_estimate_batches_stream


docker = DockerCompose(__file__)


def bootstrap():
    docker.build_images()
    docker.start()


def send_entities(quantumleap: QuantumLeapClient):
    try:
        batch = next(roughness_estimate_batches_stream) + \
                next(inspection_demo_batches_stream)
        quantumleap.insert_entities(batch)
    except Exception as e:
        print(e)


def run():
    services_running = False
    quantumleap = quantumleap_client()
    sampling_rate = 5.0
    try:
        bootstrap()
        services_running = True

        print('>>> sending entities to Quantum Leap...')
        while True:
            sleep(sampling_rate)
            send_entities(quantumleap)

    except KeyboardInterrupt:
        if services_running:
            docker.stop()
