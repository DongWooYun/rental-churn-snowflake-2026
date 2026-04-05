# 렌탈 고객 이탈 예측 분석 - WBS
## Snowflake Hackathon 2026 | 제출 마감: 2026.04.12

---

## ✅ 완료

### 4/4 (토) 빅분기 필기 시험
### 4/5 (일) 휴식

### 4/6 (월) 데이터 탐색 + 전처리 + 시각화 + 분석
| 작업 | 산출물 | 상태 |
|---|---|---|
| V03 퍼널 구조 파악 | 이탈 구간 확정 (CVR_3) | ✅ |
| V06 상품별 CVR 분석 | 소분류별 전환율 | ✅ |
| V04 채널별 CVR 분석 | 채널 볼륨×CVR 매트릭스 | ✅ |
| V11 리드타임 확인 | 신뢰도 낮음 확정 | ✅ |
| Snowpark 연결 + 전처리 | preprocess.py | ✅ |
| Plotly 차트 7개 완성 | chart1~7.html | ✅ |
| Cohort 분석 (연도×월 히트맵) | chart4_cohort_heatmap.html | ✅ |
| 상품별 Cohort (연도별 CVR) | chart5_product_cohort.html | ✅ |
| 채널별 매출 점유율 | chart6_sales_share.html | ✅ |
| 버블 매트릭스 (이탈률×볼륨×손실) | chart7_bubble_matrix.html | ✅ |
| net_sales vs policy_amount 구조 파악 | 이중 손실 프레임 확정 | ✅ |
| Q4 변곡점 원인 확정 | 상품 믹스 변화 (2023 하반기) | ✅ |
| GitHub + Drive 정리 | 쿼리/차트/코드 업로드 | ✅ |

---

## 🔑 핵심 인사이트 요약

| 구분 | 내용 |
|---|---|
| 이탈 구간 | 등록→개통 (CVR_3 평균 73%, -27% 이탈) |
| 변곡점 | 2023년 하반기 (92% → 71% 급락) |
| 변곡점 원인 | 다품목 확장으로 저CVR 상품군 유입 |
| 이탈 상품 | 세탁기(-10%p), 에어컨(-6.7%p) 악화 |
| 성공 사례 | 비데 +12%p 개선 |
| 이탈 채널 | 플랫폼 (매출 38%, CVR 30%) |
| 손실 구조 | 매출 손실 + 정책금 낭비 이중 손실 |
| 전략 프레임 | Defense(정수기) / Recovery(세탁기·에어컨) |

---

## 📋 남은 일정

| 날짜 | 작업 | 산출물 | 상태 |
|---|---|---|---|
| 4/7 (화) | 이중 손실 재계산 + GitHub 정리 | loss_revised.csv | 🔲 |
| 4/8 (수) | Streamlit in Snowflake 대시보드 | 대시보드 URL | 🔲 |
| 4/9 (목) | Cortex AI 인사이트 텍스트 연동 | AI 인사이트 | 🔲 |
| 4/10 (금) | 대시보드 완성 + 스토리 검증 | 최종 대시보드 | 🔲 |
| 4/11 (토) | Gamma.app PPT 제작 | PPT 완성 | 🔲 |
| 4/12 (일) | Loom 영상 녹화 + 최종 제출 | 제출 완료 | 🔲 |

---

## 📁 파일 구조
rental-churn-snowflake-2026/
├── README.md
├── queries/
│   ├── 01_v03_funnel.sql
│   ├── 02_v06_category.sql
│   ├── 03_v06_trend.sql
│   ├── 04_v06_region.sql
│   ├── 05_v04_channel_detail.sql
│   ├── 06_v04_channel_summary.sql
│   └── 07_v11_leadtime.sql
├── data/
│   ├── v03_funnel.csv
│   ├── v06_category.csv
│   ├── v04_channel.csv
│   ├── chart1_cvr3_trend.html
│   ├── chart2_subcategory_cvr.html
│   ├── chart3_channel_scatter.html
│   ├── chart4_cohort_heatmap.html
│   ├── chart5_product_cohort.html
│   ├── chart6_sales_share.html
│   └── chart7_bubble_matrix.html
├── streamlit/
│   └── preprocess.py
└── docs/
├── insight_summary.md
└── WBS.md
