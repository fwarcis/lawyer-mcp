# Следующие шаги

Текущий MCP намеренно ограничен read-only. Перед продолжением записи в Teable нужны
решения владельца домена, а не технические догадки.

1. Предоставить `TEABLE_TOKEN` только в development-среде для read-only integration
   smoke test. Сейчас локальный `.env` содержит лишь IDs пространства и базы.
2. Утвердить или изменить предложение минимальных полей из
   `docs/minimum-create-fields.md` для каждой из пяти сущностей.
3. Принять `[U]`-политики, от которых зависит запись: conflict check и lifecycle
   переходы; согласованность клиента дела и дочерних записей; связь task status с
   checkbox; закрытие дела; деньги; вложения; delete/retention/cascade.
4. До включения любой записи найти и подтвердить по официальной документации
   runtime schema metadata endpoint. Реализация должна сверять fingerprint, choices,
   writable/computed поля, Link cardinality/targets и User targets перед каждым write.
5. Реализовать по одному domain tool за раз: create с persistent idempotency key,
   затем partial update с expected revision и record-level serialization. Не включать
   delete до реализации impact plan, короткого TTL и plan-bound confirmation.
6. Добавить SQLite audit/idempotency store без значений чувствительных полей; для
   demo — отдельные OS-user, credentials, runtime directory и MCP configuration.
7. После появления development-token выполнить integration tests против test base:
   read pagination/projection, schema drift, enum/type/link/user rejection,
   idempotency, stale update, timeout semantics, delete plan/confirmation и отсутствие
   sensitive data в логах.

Все пункты 2–3 требуют явного решения владельца. До этого write-операции должны
оставаться выключенными.
