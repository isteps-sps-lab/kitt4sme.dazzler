from typing import Dict, List, Optional

from fipy.cfg.reader import YamlReader
from pydantic import AnyHttpUrl, BaseModel, BaseSettings, PyObject


TenantName = str


class BoardAssembly(BaseModel):
    """Specifies how to assemble a Dash dashboard for a tenant.

    The builder field is a mandatory Python path to the factory function to
    be used to instantiate the dashboard whereas the service and board paths
    are optional params for tweaking the URL at which the dashboard gets
    mounted as a FastAPI sub-app. See `BasePath` for the details of how the
    mount URL gets generated.
    """
    builder: PyObject
    service_path: Optional[str]
    board_path: Optional[str]


def demo_boards() -> List[BoardAssembly]:
    bootstrap_demo_board = BoardAssembly(
        builder='dazzler.dash.board.dbc_demo.dash_builder')
    return [bootstrap_demo_board]


DEMO_TENANT_NAME = 'demo'

CONFIG_FILE_ENV_VAR_NAME = 'DAZZLER_CONFIG'


class Settings(BaseSettings):
    quantumleap_base_url: AnyHttpUrl = 'http://quantumleap:8668'
    boards: Dict[TenantName, List[BoardAssembly]] = {}

    @staticmethod
    def demo_config() -> 'Settings':
        cfg = Settings()
        cfg.boards = {
            DEMO_TENANT_NAME: demo_boards()
        }
        return cfg

    @staticmethod
    def load() -> 'Settings':
        reader = YamlReader()
        raw_settings = reader.from_env_file(
            env_var_name=CONFIG_FILE_ENV_VAR_NAME, defaults={})
        if raw_settings:
            return Settings(**raw_settings)

        return Settings.demo_config()


def dazzler_config() -> Settings:
    return Settings.load()
