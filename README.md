# 렌탈 고객 이탈 예측 분석
**Snowflake Hackathon 2026 - 비즈니스 트랙**

## Problem Statement
렌탈 계약 규모는 19배 성장했지만 지급 전환율은 40%p 하락(100%→60%).
퍼널 어느 단계에서 이탈이 집중되는가?

## 핵심 인사이트
- 이탈 구간: 등록→개통 (CVR 73%, -27% 이탈)
- 이탈 상품: 가구/TV디지털 (CVR < 15%)
- 이탈 채널: 플랫폼 계열 (CVR 25~30%)
- 트렌드: 2023→2026 개통CVR -26%p 지속 하락

## 기술 스택
- Snowpark (Python)
- Streamlit in Snowflake
- Plotly / Altair
- Snowflake Cortex AI
