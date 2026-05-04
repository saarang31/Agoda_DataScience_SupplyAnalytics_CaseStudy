# Agoda Supply Analytics — Urgency Messaging Strategy

**Take-home case study** for Agoda's Supply Analytics team.

Analyses how hotel prices move as the check-in date approaches across 5 anonymous cities, and identifies business opportunities for urgency messaging to improve conversion.

---

## Overview

| Metric | Value |
|---|---|
| Total bookings | 49,061 |
| Cities analysed | 5 |
| Unique properties | 880 |
| Check-in date range | Oct–Dec 2016 |
| Average ADR drop (31–60d → same-day) | −22.7% |

**Key finding:** Same-day bookers pay less in every market. Urgency messaging type should be calibrated per city cluster and per season — scarcity framing works best in December (holiday period), earn-sooner framing works best in October/November.

---

## Deliverables

Two presentation formats are provided in `outputs/`:

| File | Description |
|---|---|
| `Agoda_CrossType_Format.pptx` | **Cross-city format** — 16 slides organised by graph type (all 5 cities compared simultaneously per analysis dimension) |
| `Agoda_Urgency_Messaging_Analysis.pptx` | **Per-city format** — 17 slides organised by city (deep-dive per market) |

---

## Project Structure

```
.
├── README.md
├── requirements.txt
├── data/                          # Place city Excel files here (not tracked)
│   ├── City_A.xlsx
│   ├── City_B.xlsx
│   ├── City_C.xlsx
│   ├── City_D.xlsx
│   └── City_E.xlsx
├── src/
│   ├── generate_eda_figures.py          # Step 1 — per-city EDA + cross-city overview figures
│   ├── generate_city_price_seg_figures.py  # Step 2 — per-city price movement + segmentation figures
│   ├── generate_cross_type_slides.py    # Step 3 — cross-city-by-graph-type figures (8 slides)
│   ├── generate_updates.py              # Step 4 — individual slide updates (monthly, star trend, etc.)
│   └── build_crosstype_deck.js          # Step 5 — assembles all figures into the final PPTX
└── outputs/
    ├── Agoda_CrossType_Format.pptx
    └── Agoda_Urgency_Messaging_Analysis.pptx
```

---

## How to Run

### Prerequisites

**Python 3.9+**
```bash
pip install -r requirements.txt
```

**Node.js 16+**
```bash
npm install pptxgenjs
```

### Steps

Place the five city Excel files in `data/`, then run in order:

```bash
# Step 1 — Generate EDA and cross-city overview figures
python src/generate_eda_figures.py

# Step 2 — Generate per-city price movement and segmentation figures
python src/generate_city_price_seg_figures.py

# Step 3 — Generate cross-city-by-graph-type figures (8 comparison slides)
python src/generate_cross_type_slides.py

# Step 4 — Apply individual slide updates (monthly analysis, star trend fixes)
python src/generate_updates.py

# Step 5 — Assemble everything into the final PPTX
node src/build_crosstype_deck.js
```

The final deck is written to the working directory as `Agoda_CrossType_Format.pptx`.

---

## Analysis Structure (Cross-City Format)

| Slide | Content |
|---|---|
| 1 | Title |
| 2 | Business question, dataset limitations, methodology |
| 3 | Executive summary — key findings and recommendations |
| 4 | Cross-city EDA overview (price ranges, urgency tiers, revenue by star band, accommodation mix) |
| 5 | Monthly booking patterns — Oct, Nov, Dec across all 5 cities |
| 6 | Lead time distribution by urgency tier — all cities |
| 7 | Revenue vs booking share by star band — all cities |
| 8 | Accommodation type mix — all cities |
| 9 | ADR scatter vs lead time — all cities |
| 10 | ADR by lead time bucket — all cities |
| 11 | ADR by star band and lead time (grouped bars) — all cities |
| 12 | ADR trend by star band with upsell windows — all cities |
| 13 | Cross-city: price trends, urgency profile, revenue by segment, price direction |
| 14 | Recommendations |
| 15 | Next steps |
| 16 | Closing |

---

## Key Findings

1. **ADR falls last-minute in all 5 cities** — average −22.7% from 31–60 days ahead to same-day
2. **34% of bookings happen within 3 days of check-in** — City E peaks at 44%, City C is lowest at 18%
3. **456 of 880 properties confirmed to price same or lower last-minute** — only 109 genuinely raise prices
4. **Two market clusters identified:**
   - Budget/last-minute (Cities A, B, E): median ADR $79–$94, High-Urgency share 38–44%
   - Premium (Cities C, D): median ADR $190–$192, predominantly planned bookings
5. **December shifts urgency strategy** — last-minute rate drops in Dec as people plan ahead for holidays; scarcity framing outperforms earn-sooner messaging in this period

---

## Recommendations

| # | Recommendation |
|---|---|
| 1 | Avoid blanket "prices rising" claims — only truthful for 109 of 880 properties |
| 2 | Use earn-sooner / loyalty points framing for budget/mid-range properties in Oct–Nov |
| 3 | Switch to scarcity / "holiday rooms filling up" framing in December |
| 4 | Prioritise 4★ properties — revenue share exceeds booking share in all 5 cities |
| 5 | A/B test urgency message types per city before full rollout |

---

## Notes

- City identities are anonymised (City A–E) as provided in the original dataset
- All figures are generated as PNG images embedded in the PPTX — charts are not native PowerPoint chart objects
- The per-city deck (`Agoda_Urgency_Messaging_Analysis.pptx`) was built using a separate build script (`build_full_deck_v2.js`) retained in the session but not included here as it was superseded by the cross-city format
