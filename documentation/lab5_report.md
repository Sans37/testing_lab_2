# Лабораторная работа №5 — Трассировка и мониторинг

## Цель
Интегрировать трассировку и мониторинг, сравнить потребление ресурсов:
- при включенной трассировке и без неё;
- при логировании по умолчанию и при расширенном логировании.

## Средства
- OpenTelemetry (трассировка)
- Docker + docker stats (сбор CPU/RAM по контейнерам)
- Benchmark-скрипт `scripts/benchmark_lab3.py`

## Внесённые изменения
1. Добавлена трассировка OpenTelemetry:
   - `src/observability/tracing.py`
   - включение через `ENABLE_TRACING=true`
   - экспорт в файл через `OTEL_EXPORTER_FILE`
2. Логирование управляется переменной `LOG_LEVEL` (INFO/DEBUG):
   - `src/api/main.py`
   - `src/infrastructure/database/database.py`
3. Конфигурация benchmark-контейнера:
   - `docker/docker-compose.benchmark.yml` (переменные ENABLE_TRACING, LOG_LEVEL, OTEL_EXPORTER_FILE)
4. CI/CD сохраняет артефакты трассировки:
   - `.github/workflows/tests.yml`

## Где сохраняются данные
- `observability/otel_traces.jsonl` — трассы локальных/benchmark запусков
- `observability/otel_traces_ci.jsonl` — трассы CI/CD
- `benchmarks/run-.../resources_summary.json` — CPU/RAM по контейнерам

## Эксперименты
### Эксперимент A — Базовый (tracing OFF, log INFO)
Команда: см. `lab5_run.txt` (п.1)
Результаты:
- resources_summary.json: ______________________

### Эксперимент B — Tracing ON
Команда: см. `lab5_run.txt` (п.2)
Результаты:
- resources_summary.json: ______________________

### Эксперимент C — Log DEBUG
Команда: см. `lab5_run.txt` (п.3)
Результаты:
- resources_summary.json: ______________________

## Сравнение ресурсов
- Сравнение A vs B (tracing OFF/ON):
  CPU (avg): ______________________
  RAM (avg): ______________________

- Сравнение A vs C (INFO/DEBUG):
  CPU (avg): ______________________
  RAM (avg): ______________________

## Вывод
- Включение трассировки увеличивает расход ресурсов на ___%
- Расширенное логирование увеличивает расход ресурсов на ___%

