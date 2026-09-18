from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from json import dumps
from typing import Final


@dataclass(frozen=True)
class Field:
    id: str
    label: str
    sensitive: bool = False


@dataclass(frozen=True)
class Table:
    id: str
    label: str
    fields: tuple[Field, ...]

    def field(self, field_id: str) -> Field:
        for field in self.fields:
            if field.id == field_id:
                return field
        raise KeyError(field_id)


CLIENTS: Final = Table(
    id="tblnRVk5GfCN2JNEovH",
    label="Клиенты",
    fields=(
        Field("fldYoptHjzf9ctp9hLW", "Клиент"),
        Field("fldn5GZY4t6unLruZaz", "Статус клиента"),
        Field("fldvkg3IjsSMBxlvKEF", "Тип клиента"),
        Field("fldKwAUrUPkOHgQjIWx", "Проверка конфликта"),
        Field("fldThxhxNmnp2YFhr9O", "Телефон", sensitive=True),
        Field("fldlV8CAprAzKFsFtdD", "Email", sensitive=True),
        Field("fldflp73HIEBdozZ2q8", "ИИН / БИН", sensitive=True),
        Field("fldcBX4HV59tcwi17ye", "Адрес", sensitive=True),
        Field("fldCrFhoBxh5wMA547h", "Заметки", sensitive=True),
    ),
)

TABLES: Final = {CLIENTS.id: CLIENTS}
DIRECTORY_FIELDS: Final = tuple(field.id for field in CLIENTS.fields[:4])
SENSITIVE_CLIENT_FIELDS: Final = tuple(field.id for field in CLIENTS.fields if field.sensitive)

MINIMUM_FIELD_PROPOSAL: Final = {
    "Клиенты": ["Клиент", "Тип клиента", "Проверка конфликта"],
    "Дела": ["Дело", "Клиент"],
    "Задачи": ["Задача"],
    "Взаимодействия": ["Взаимодействие", "Дата"],
    "Документы": ["Документ"],
}


def schema_fingerprint() -> str:
    """Fingerprint of the contract snapshot, not a claim about live metadata."""
    snapshot = [{"table": table.id, "fields": [field.id for field in table.fields]} for table in TABLES.values()]
    return sha256(dumps(snapshot, separators=(",", ":"), sort_keys=True).encode()).hexdigest()
