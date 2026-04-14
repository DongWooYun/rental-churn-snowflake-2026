# 💧 렌탈 고객 이탈 예측 및 Retention 전략 도출

> **Snowflake Hackathon 2026 — 비즈니스 트랙**  
> South Korea Telecom Subscription Analytics 데이터 기반 렌탈 고객 이탈 분석

---

## 🔗 데모

| 버전 | 링크 | 설명 |
|------|------|------|
| 🌐 Streamlit Cloud | [rental-churn-app-2026-dongwooyun.streamlit.app](https://rental-churn-app-2026-dongwooyun.streamlit.app/) | 누구나 접속 가능한 공개 버전 |
| ❄️ Snowflake Streamlit | Snowflake 계정 필요 | Cortex AI 전략 생성 포함 |

---

## 📌 Problem Statement

렌탈 시장은 2023년 이후 다품목으로 빠르게 확장됐지만,  
**등록→개통 구간에서 20.5%의 고객이 이탈**하고 있습니다.

더 큰 문제는 **이중 손실 구조**입니다.
- 이탈 고객의 LTV(매출) 손실
- 이미 집행된 설치비·사은품(정책금) 회수 불가
- **실질 손실 = 매출 손실 × 1.3배**

---

## 💡 핵심 인사이트

### 1. 이탈 구간 특정
| 구간 | CVR | 이탈 규모 |
|------|-----|---------|
| 신청 → 등록 | 91.4% | 46,594건 |
| **등록 → 개통** | **79.5%** | **102,191건 ⚠️** |
| 전체 | 72.7% | 148,785건 |

### 2. 변곡점 — 2023년 8월
- 정수기 단일 상품 → 세탁기·에어컨·TV 등 다품목 한꺼번에 확장
- 정수기 CVR도 동시에 -9.3%p 하락 → **제품 문제 아닌 전사 프로세스 문제**

### 3. 상품별 CVR 양극화
| 전략존 | 상품 | CVR |
|--------|------|-----|
| ✅ Defense/Leverage | 정수기, 비데, 공기청정기 | 65%+ |
| ⚠️ 개선 필요 | 침대/매트리스, 안마의자 | 40~65% |
| ❌ Recovery 필요 | 세탁기, 에어컨, TV, 노트북 | ~40% |

### 4. 성공 사례 — 비데 +12.3%p
- 개통 전 단계별 넛지 메시지 도입
- 설치 일정 즉시 확정 시스템
- → **세탁기·에어컨에 동일 적용 시 CVR +6~10%p 예상**

---

## 📊 대시보드 구성 (5페이지)

| 페이지 | 내용 |
|--------|------|
| P1 · 문제 정의 | 고객 획득 퍼널 + 이중 손실 KPI |
| P2 · 변곡점 원인 | 월별 CVR 추이 + 2023-08 변곡점 분석 |
| P3 · 상품 분석 | 상품별 CVR × 볼륨 매트릭스 |
| P4 · 전략 가이드 | 상품별 Retention 전략 (Snowflake 버전: Cortex AI 자동 생성) |
| P5 · 비즈니스 임팩트 | CVR 개선 시나리오 슬라이더 + ROI 계산 |

---

## 🏗️ 브랜치 구조
main                  ← Snowflake 버전 (분석 코드 + 쿼리)
└── streamlit-cloud   ← 공개 포트폴리오 버전 (CSV 기반)

---

## 🛠️ 기술 스택

| 구분 | 기술 |
|------|------|
| 데이터 | Snowflake Marketplace — South Korea Telecom Subscription Analytics |
| 분석 | Python (Pandas, Plotly) |
| 대시보드 | Streamlit in Snowflake / Streamlit Cloud |
| AI | Snowflake Cortex (mistral-large2, snowflake-arctic) |
| 개발 환경 | Google Colab |

---

## 📁 프로젝트 구조
rental-churn-snowflake-2026/
├── data/                    # 차트 HTML 파일
├── docs/
│   ├── insight_summary.md   # 핵심 인사이트 정리
│   └── WBS.md               # 작업 분해 구조
├── queries/                 # Snowflake SQL 쿼리
│   ├── 01_v03_funnel.sql
│   ├── 02_v06_category.sql
│   └── ...
├── streamlit/
│   ├── preprocess.py        # Snowflake 데이터 전처리
│   └── requirements.txt
└── README.md

---

## 📈 비즈니스 임팩트 (시나리오)

CVR_3 **+5%p 개선** 시 12개월간:

| 항목 | 효과 |
|------|------|
| 월 추가 개통 | +750건 |
| 매출 증가 | 9.45억원 |
| 정책금 절감 | 1.76억원 |
| **총 효과** | **11.2억원** |
| ROI | +2,140% (투자 5천만원 기준) |

---

## 📜 데이터 출처

- **South Korea Telecom Subscription Analytics** — Snowflake Marketplace
- 본 레포지토리에는 집계/가공된 데이터만 포함되며, RAW 데이터는 포함되지 않습니다.

---

## 👤 Author

**DongWoo Yun** | [GitHub](https://github.com/DongWooYun)
