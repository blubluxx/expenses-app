# The reason to ignore "assignment" https://github.com/pydantic/pydantic/issues/3143
# mypy: disable-error-code="assignment"
from functools import lru_cache
from typing import List, Optional, Union

from pydantic import field_validator, AnyHttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    API_V1_STR: str
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []
    VERSION: str = "9.9.9.9"

    @field_validator("BACKEND_CORS_ORIGINS", check_fields=False)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        else:
            return v

    PROJECT_NAME: str = "expenses-app"

    PYDEVD: bool = False
    PYDEVD_PORT: Optional[int] = None
    PYDEVD_HOST: Optional[str] = None

    # class Config:
    #     case_sensitive = True
    #     allow_extra = True

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache()
def get_settings() -> Settings:
    return Settings()
