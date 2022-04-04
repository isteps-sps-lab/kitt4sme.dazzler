from pydantic import BaseSettings, AnyHttpUrl


class Settings(BaseSettings):
    quantumleap_base_url: AnyHttpUrl = 'http://quantumleap:8668'


dazzler_config = Settings()
