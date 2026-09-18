# Решения

## Python-MCP стек и транспорт

**Контекст.** Нужен небольшой, типизированный MCP-сервер для одного демонстрационного
пользователя; реализация ещё не начата.

**Решение.** Использовать Python 3.14, официальный пакет `mcp` v2 (зафиксированный
в lock-файле при реализации) и его `MCPServer`. Начальный транспорт — только локальный
`stdio`; HTTP/SSE не включать. Для доменных входов использовать Pydantic v2, для
Teable HTTP API — `httpx`, для повторов — `tenacity`, для постоянного журнала операций,
идемпотентности и plans — локальную SQLite БД, принадлежащую отдельному runtime-пользователю.
Проверки: `pytest`, `pyright --strict`, `ruff` и `uv` для управляемых зависимостей.

**Почему.** Официальный Python SDK MCP v2 — текущая стабильная линия, поддерживает
stdio, Streamable HTTP и SSE и требует Python 3.10+. `stdio` не открывает сетевой
слушатель и позволяет запускать сервер в изолированной среде адвоката с отдельными
credentials и правами файлов. У Teable нет документированного официального Python SDK;
его официальные API-страницы приводят HTTP/Python-примеры, поэтому небольшой явный
адаптер к REST API безопаснее неподтверждённого стороннего клиента.

**Ограничение.** `stdio` сам по себе не аутентифицирует человека. В demo actor должен
задаваться доверенной конфигурацией отдельной среды/OS-учётной записи, а не аргументом
MCP tool. Удалённый transport и многопользовательская аутентификация потребуют
отдельного решения.

**Источники.** [Официальный MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk),
[Teable API overview](https://help.teable.ai/en/api-doc/overview),
[Teable create records](https://help.teable.ai/en/api-doc/record/create).

## Граница Teable-интеграции

**Решение.** Выполнять record API только с `fieldKeyType: "id"` и `typecast: false`.
Перед каждым write получать и сверять runtime metadata/fingerprint; использовать
постраничное чтение с `take <= 100`, projection и field allowlist. Ограничить клиент
10 запросами в секунду, с ограниченной параллельностью и обработкой `Retry-After`.
Не предоставлять операции schema или View.

**Почему.** Field IDs стабильнее имён. Документация Teable определяет строгую
валидацию при выключенном `typecast`; включённый режим способен преобразовать вход,
что не подходит для защитного слоя. Актуальная документация Cloud ограничивает
новые personal API keys 100 записями на страницу, а pricing устанавливает 10 API
запросов в секунду.

**Источники.** [Teable get records](https://help.teable.ai/en/api-doc/record/get),
[Teable create records](https://help.teable.ai/en/api-doc/record/create),
[Teable pricing](https://teable.ai/pricing).

## Неподтверждённые upstream-гарантии

**Решение.** Не заявлять и не моделировать как подтверждённые: межтабличную
транзакцию, атомарность batch-запроса, compare-and-swap по revision/lastModifiedTime
или upstream idempotency key. Начальная write-поверхность должна состоять из
однозаписных операций; составные изменения — только через сохраняемую saga с явными
состояниями. После тайм-аута неидемпотентного запроса возвращать `indeterminate` и
не повторять POST/PATCH/DELETE автоматически.

**Почему.** В опубликованных контрактах record create/update/delete отсутствуют
идемпотентный ключ, условный заголовок/версия и гарантия batch/cross-table atomicity.
Повтор POST после неизвестного результата может создать дубль; локальная таблица
идемпотентности не может доказать, был ли upstream write принят.

**Источники.** [Teable create records](https://help.teable.ai/en/api-doc/record/create),
[Teable update record](https://help.teable.ai/en/api-doc/record/update),
[Teable delete records](https://help.teable.ai/en/api-doc/record/delete).

## Начальная capability-поверхность и режимы

**Решение.** До утверждения владельцем минимальных обязательных полей и остальных
`[U]`-правил MCP остаётся read-only: поиск клиентов и чтение карточки по `rec...`.
Запись, удаление, вложения и schema/View operations отсутствуют. Имена и
нечувствительные статусы возвращаются по явному allowlist; PII-поля требуют
`DOSSIER_ALLOW_PII_READ=1`. `DOSSIER_MODE` обязателен (`development|demo`), а demo
должен работать от отдельного OS-пользователя с отдельными credentials и runtime-dir.

**Почему.** Контракт прямо помечает минимальную бизнес-обязательность полей как `[U]`
и требует fail-closed writes. Read API Teable документирует `fieldKeyType=id`, projection
и pagination; это достаточно для узкой безопасной демонстрации без недокументированных
