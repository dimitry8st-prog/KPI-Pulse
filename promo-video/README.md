# Рекламное видео KPI Pulse

Короткий ролик 35 секунд: «KPI Pulse превращает сложные таблицы в понятные бизнес-решения».

Стек: **Remotion 4**. Рабочая логика приложения (`app.py`, `src/`) не менялась.

## Что получится

| Файл | Назначение |
| --- | --- |
| `output/kpi-pulse-promo-ru.mp4` | Горизонталь 1920×1080, 30 fps, 35 с |
| `output/kpi-pulse-promo-vertical-ru.mp4` | Вертикаль 1080×1920 для Shorts / Reels / VK Клипов |
| `output/kpi-pulse-cover.png` | Обложка 1280×720 |
| `kpi-pulse-promo-ru.srt` | Субтитры |
| `voiceover-script-ru.md` | Сценарий и текст диктора |

## Установка

Нужны Node.js 18+ и Python 3.10+ (для музыки и опционального голоса).

```bash
cd promo-video
npm install
python scripts/generate_bgm.py
```

Музыка — оригинальный синтезированный фон без сторонних семплов (`assets/music/kpi-pulse-bed.wav`).

## Предпросмотр

```bash
npm run preview
```

Откроется Remotion Studio. Композиции:

- `KpiPulsePromo` — горизонталь
- `KpiPulsePromoVertical` — вертикаль
- `KpiPulseCover` — обложка

Проп `withVoiceover`: `false` по умолчанию. Видео читается по субтитрам без звука.

## Рендер

Без закадрового голоса (рекомендуется, субтитры несут смысл):

```bash
npm run build:silent
npm run build:vertical
npm run still:cover
```

С голосом (сначала синтез):

```bash
pip install edge-tts
python scripts/generate_voiceover.py
npm run build:vo
```

Все основные артефакты разом:

```bash
npm run all
```

## Данные в кадре

Показаны только реальные функции KPI Pulse и цифры из `data/sample_data.csv`:

- период **2026-06**
- MRR 345 000 ₽ (+2,07%), CAC 415,38 ₽, LTV 4 015,52 ₽ (−2,24%), Churn 2,18%, Conversion 54,63%
- загрузка CSV / Google Sheets
- дашборд из пяти карточек
- AI-аналитик обычным языком
- дайджест в Telegram

Технологии (Python, Streamlit, Claude, ChromaDB, SQLite) перечислены только мелкой строкой на финальном экране.

## Структура

```
promo-video/
├── src/                 # композиции и сцены
├── assets/              # музыка, голос, публичные файлы Remotion
├── scripts/             # генерация музыки и TTS
├── output/              # mp4 и обложка
├── props-silent.json    # рендер без голоса
└── props-voiceover.json # рендер с голосом
```
