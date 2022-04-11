from dazzler.config import CONFIG_FILE_ENV_VAR_NAME, dazzler_config, Settings
from pathlib import Path


def get_config_path(file_name: str) -> str:
    enclosing_dir = Path(__file__).parent.resolve()
    target = enclosing_dir / 'config' / file_name
    return str(target)


BOARDS_YAML_PATH = get_config_path('boards.yaml')
EMPTY_YAML_PATH = get_config_path('empty.yaml')
QL_URL_YAML_PATH = get_config_path('ql-url.yaml')


def builder_1() -> int:
    return 1


def builder_2() -> int:
    return 2


def test_from_empty_file(monkeypatch):
    monkeypatch.setenv(CONFIG_FILE_ENV_VAR_NAME, EMPTY_YAML_PATH)
    got = Settings.load()

    assert got == dazzler_config()


def test_from_ql_url_file(monkeypatch):
    monkeypatch.setenv(CONFIG_FILE_ENV_VAR_NAME, QL_URL_YAML_PATH)
    got = Settings.load()

    assert got.quantumleap_base_url == 'http://ql/'
    assert got.boards == dazzler_config().boards


def test_from_boards_file(monkeypatch):
    monkeypatch.setenv(CONFIG_FILE_ENV_VAR_NAME, BOARDS_YAML_PATH)
    got = Settings.load()

    assert got.quantumleap_base_url == dazzler_config().quantumleap_base_url
    assert len(got.boards) == 2

    t1_boards = got.boards['t1']
    assert len(t1_boards) == 2

    t1_b1, t1_b2 = t1_boards[0], t1_boards[1]

    assert t1_b1.builder() == 1
    assert t1_b1.service_path is None
    assert t1_b1.board_path is None

    assert t1_b2.builder() == 2
    assert t1_b2.service_path is None
    assert t1_b2.board_path == 'b2'

    t2_boards = got.boards['t2']
    assert len(t2_boards) == 1

    t2_b = t2_boards[0]

    assert t2_b.builder() == 1
    assert t2_b.service_path == '/sp'
    assert t2_b.board_path == '/b1'
