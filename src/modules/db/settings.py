from dataclasses import dataclass

import config


@dataclass(frozen=True)
class DBSettings:
    uri: str = config.MONGODB_URI
    db_name: str = config.MONGODB_DB_NAME
    collection_name: str = config.MONGODB_COLLECTION_NAME


def get_db_settings() -> DBSettings:
    return DBSettings()
