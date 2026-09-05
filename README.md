# Telegram Relay

GitHub Actions автоматически скачивает посты из 4 Telegram-каналов каждые 30 минут.

## Каналы
- `geranium_chronicles` — Удары по Украине
- `LPRalarm` — Предупреждения о пусках
- `vrv_radar` — Фиксации БПЛА
- `locatorru` — Направления полётов

## JSON файлы
`data/*.json` — формат совместим с парсером MailCloudParser:
```json
{"channel":"name","title":"Title","posts":[{"id":"123","text":"...","datetime":"...","url":"..."}]}
```
