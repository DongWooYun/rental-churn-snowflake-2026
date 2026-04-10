import streamlit as st
from snowflake.snowpark.context import get_active_session
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import json

st.set_page_config(page_title="렌탈 고객 이탈 분석", layout="wide")
session = get_active_session()

# ── 사이드바 ──────────────────────────────────────────────
st.sidebar.markdown("## 💧 렌탈 이탈 분석")
st.sidebar.markdown("**Snowflake Hackathon 2026**")
st.sidebar.markdown("---")
page = st.sidebar.radio("페이지 선택", [
    "P1 · 문제 정의",
    "P2 · 변곡점 원인",
    "P3 · 상품 분석",
    "P4 · Cortex AI 전략",
    "P5 · 비즈니스 임팩트",
])

# ── 데이터 로드 ───────────────────────────────────────────
@st.cache_data
def load_funnel():
    return session.sql("""
        SELECT STAGE, STAGE_ORDER, CNT
        FROM RENTAL_CHURN.PUBLIC.V_FUNNEL_SUMMARY
        ORDER BY STAGE_ORDER
    """).to_pandas()

@st.cache_data
def load_monthly_cvr():
    return session.sql("""
        SELECT TO_CHAR(YEAR_MONTH, 'YYYY-MM') AS YM, CVR_3
        FROM RENTAL_CHURN.PUBLIC.V_MONTHLY_CVR
        ORDER BY YEAR_MONTH
    """).to_pandas()

@st.cache_data
def load_product_cvr():
    return session.sql("""
        SELECT RENTAL_SUB_CATEGORY, CONTRACT_CNT, OPEN_CNT, CVR_3_PCT
        FROM RENTAL_CHURN.PUBLIC.V_PRODUCT_CVR
        ORDER BY CONTRACT_CNT DESC
    """).to_pandas()

funnel  = load_funnel()
cvr_df  = load_monthly_cvr()
prod_df = load_product_cvr()

total_apply = funnel[funnel['STAGE_ORDER']==1]['CNT'].values[0]
total_reg   = funnel[funnel['STAGE_ORDER']==2]['CNT'].values[0]
total_open  = funnel[funnel['STAGE_ORDER']==3]['CNT'].values[0]

# ═════════════════════════════════════════════════════════
# P1 · 문제 정의
# ═════════════════════════════════════════════════════════
if page == "P1 · 문제 정의":
    st.title("P1 · 문제 정의")
    st.markdown("### 렌탈 고객 이탈, 어디서 얼마나 빠져나가나?")

    cvr_2 = total_reg  / total_apply * 100
    cvr_3 = total_open / total_reg   * 100

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("전체 신청",  f"{total_apply:,.0f}건")
    k2.metric("등록완료",   f"{total_reg:,.0f}건",  delta=f"CVR {cvr_2:.1f}%")
    k3.metric("개통완료",   f"{total_open:,.0f}건", delta=f"CVR {cvr_3:.1f}%")
    k4.metric("전체 CVR",  f"{total_open/total_apply*100:.1f}%")

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        fig = go.Figure(go.Funnel(
            y=funnel['STAGE'], x=funnel['CNT'],
            textinfo="value+percent previous",
            marker=dict(color=["#2980b9","#f39c12","#e74c3c"]),
        ))
        fig.update_layout(title="고객 획득 퍼널", height=400, template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("#### 📌 핵심 이탈 구간")
        st.markdown("""
        | 구간 | CVR | 이탈 규모 |
        |------|-----|---------|
        | 신청 → 등록 | 91.4% | 46,594건 |
        | 등록 → 개통 | **79.5%** | **102,191건** ⚠️ |
        | 전체 | 72.7% | 148,785건 |
        """)
        st.error("💡 등록→개통 구간에서 10만건 이탈 — 핵심 개선 포인트")
        st.markdown("#### 💸 이중 손실 구조")
        st.markdown("""
        - **매출 손실**: 이탈 고객 × LTV
        - **정책금 낭비**: 이미 집행된 설치비·사은품
        - **손실 배율**: 매출 손실의 **1.3배** 실제 손실
        """)
        st.warning("이탈 1건 = 매출 손실 + 회수 불가 정책금")

# ═════════════════════════════════════════════════════════
# P2 · 변곡점 원인
# ═════════════════════════════════════════════════════════
elif page == "P2 · 변곡점 원인":
    st.title("P2 · 변곡점 원인")
    st.markdown("### 2023년 하반기, CVR이 왜 꺾였나?")

    fig = make_subplots(rows=1, cols=1)
    fig.add_trace(go.Scatter(
        x=cvr_df['YM'], y=cvr_df['CVR_3'],
        mode="lines+markers", name="CVR_3",
        line=dict(color="#e74c3c", width=2),
        fill="tozeroy", fillcolor="rgba(231,76,60,0.1)",
    ))
    # 이동평균
    cvr_df['MA3'] = cvr_df['CVR_3'].rolling(3, min_periods=1).mean()
    fig.add_trace(go.Scatter(
        x=cvr_df['YM'], y=cvr_df['MA3'],
        mode="lines", name="3개월 이동평균",
        line=dict(color="#f39c12", width=2, dash="dash"),
    ))
    fig.add_shape(type="line",
                  x0="2023-08", x1="2023-08", y0=0, y1=1,
                  xref="x", yref="paper",
                  line=dict(color="#4db8ff", dash="dash", width=2))
    fig.add_annotation(x="2023-08", y=0.97, xref="x", yref="paper",
                       text="📍 다품목 확장 시작", font=dict(color="#4db8ff", size=12),
                       showarrow=False)
    fig.update_layout(
        title="월별 CVR_3 추이 (등록→개통)",
        height=430, template="plotly_dark",
        xaxis=dict(tickangle=-45),
        yaxis=dict(title="CVR", tickformat=".0%"),
        legend=dict(orientation="h", y=-0.15),
    )
    st.plotly_chart(fig, use_container_width=True)

    col1, col2, col3 = st.columns(3)
    col1.error("**정수기 CVR**\n\n87.4% → 78.2%\n\n-9.3%p 꺾임")
    col2.warning("**원인 진단**\n\n2023-08 다품목 한꺼번에 추가\n\n운영 준비 미흡")
    col3.info("**영향**\n\n저CVR 상품 비중 증가\n\n전체 평균 CVR 하락")

# ═════════════════════════════════════════════════════════
# P3 · 상품 분석
# ═════════════════════════════════════════════════════════
elif page == "P3 · 상품 분석":
    st.title("P3 · 상품 분석")
    st.markdown("### 어떤 상품이 CVR을 끌어내리나?")

    top15 = prod_df.sort_values('CONTRACT_CNT', ascending=False).head(15)

    def cvr_color(v):
        if v >= 65:  return "#27ae60"
        elif v >= 40: return "#f39c12"
        else:         return "#e74c3c"

    colors = [cvr_color(v) for v in top15['CVR_3_PCT']]

    col1, col2 = st.columns([2, 1])

    with col1:
        fig = go.Figure(go.Bar(
            x=top15['RENTAL_SUB_CATEGORY'],
            y=top15['CVR_3_PCT'],
            marker_color=colors,
            text=[f"{v:.1f}%" for v in top15['CVR_3_PCT']],
            textposition="outside",
        ))
        fig.add_hline(y=65, line_dash="dot", line_color="#27ae60",
                      annotation_text="우수 65%", annotation_font_color="#27ae60")
        fig.add_hline(y=40, line_dash="dot", line_color="#f39c12",
                      annotation_text="위험 40%", annotation_font_color="#f39c12")
        fig.update_layout(
            title="상품별 CVR_3 — 계약건수 TOP 15",
            height=450, template="plotly_dark",
            xaxis=dict(tickangle=-30),
            yaxis=dict(title="CVR (%)", range=[0, 110]),
            showlegend=False,
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("#### 전략 분류")
        good = top15[top15['CVR_3_PCT'] >= 65]['RENTAL_SUB_CATEGORY'].tolist()
        warn = top15[(top15['CVR_3_PCT'] >= 40) & (top15['CVR_3_PCT'] < 65)]['RENTAL_SUB_CATEGORY'].tolist()
        bad  = top15[top15['CVR_3_PCT'] < 40]['RENTAL_SUB_CATEGORY'].tolist()

        st.success(f"✅ **Defense/Leverage** (65%+)\n\n" + ", ".join(good))
        st.warning(f"⚠️ **개선 필요** (40~65%)\n\n" + ", ".join(warn))
        st.error(f"❌ **Recovery 필요** (~40%)\n\n" + ", ".join(bad))

# ═════════════════════════════════════════════════════════
# P4 · Cortex AI 전략
# ═════════════════════════════════════════════════════════
elif page == "P4 · Cortex AI 전략":
    st.title("P4 · Cortex AI — Retention 전략 생성기")
    st.markdown("### 상품을 선택하면 AI가 맞춤 전략을 자동 생성합니다")

    PRODUCT_CONTEXT = {
        "정수기":  {"cvr": 76.9, "zone": "Defense",  "issue": "볼륨 1위, CVR -9.3%p 하락"},
        "세탁기":  {"cvr": 33.4, "zone": "Recovery", "issue": "대형가전, CVR 33% 위험"},
        "에어컨":  {"cvr": 31.7, "zone": "Recovery", "issue": "계절성 상품, CVR 32% 위험"},
        "비데":    {"cvr": 77.1, "zone": "Leverage",  "issue": "CVR 77%, 성공 모델"},
        "공기청정기": {"cvr": 68.5, "zone": "Leverage", "issue": "CVR 68%, 안정적"},
        "냉장고":  {"cvr": 33.0, "zone": "Recovery", "issue": "대형가전, CVR 33% 위험"},
        "TV":     {"cvr": 24.7, "zone": "Recovery", "issue": "CVR 25%, 최하위권"},
        "노트북":  {"cvr": 7.1,  "zone": "Watch",    "issue": "CVR 7%, 렌탈 부적합 의심"},
    }

    col1, col2 = st.columns([1, 2])
    with col1:
        product = st.selectbox("📦 상품 선택", list(PRODUCT_CONTEXT.keys()))
        focus   = st.selectbox("🎯 전략 방향", [
            "단기 퀵윈 (1개월)",
            "중기 프로세스 개선 (3개월)",
            "장기 구조적 전략 (6개월+)",
        ])
        ctx = PRODUCT_CONTEXT[product]
        zone_color = {"Defense":"🔴","Recovery":"🟠","Leverage":"🟢","Watch":"🔵"}.get(ctx['zone'],'⚪')
        st.markdown(f"""
        **{zone_color} {ctx['zone']} Zone**
        - CVR: **{ctx['cvr']}%**
        - 현황: {ctx['issue']}
        """)
        btn = st.button("🤖 AI 전략 생성", use_container_width=True)

    with col2:
        if btn:
            with st.spinner("Cortex AI 분석 중..."):
                prompt = f"""당신은 렌탈 산업 고객 이탈 방지 전문 컨설턴트입니다.
아래 데이터를 바탕으로 {product} 상품의 {focus} Retention 전략을 제안하세요.

데이터:
- 상품: {product}
- CVR_3 (등록→개통): {ctx['cvr']}%
- 전략존: {ctx['zone']}
- 현황: {ctx['issue']}
- 이중손실 배율: 1.3x

반드시 JSON 형식으로만 답하세요 (다른 텍스트 없이):
{{"summary":"전략요약 1문장","root_cause":"원인분석 2줄","actions":[{{"title":"액션1","detail":"실행방법","impact":"예상효과"}},{{"title":"액션2","detail":"실행방법","impact":"예상효과"}},{{"title":"액션3","detail":"실행방법","impact":"예상효과"}}],"kpi":"측정지표"}}"""

                try:
                    result = session.sql(f"""
                        SELECT SNOWFLAKE.CORTEX.COMPLETE(
                            'mistral-large2',
                            '{prompt.replace("'", "''")}'
                        ) AS response
                    """).collect()[0]['RESPONSE']

                    clean = result.strip()
                    if '```json' in clean:
                        clean = clean.split('```json')[1].split('```')[0].strip()
                    elif '```' in clean:
                        clean = clean.split('```')[1].split('```')[0].strip()

                    parsed = json.loads(clean)

                    st.success(f"✅ {parsed['summary']}")
                    st.markdown(f"**🔍 원인 분석:** {parsed['root_cause']}")
                    st.markdown("---")
                    st.markdown("**🚀 액션 플랜**")
                    for i, action in enumerate(parsed['actions']):
                        with st.expander(f"Action {i+1}: {action['title']}"):
                            st.markdown(f"**실행방법:** {action['detail']}")
                            st.markdown(f"**예상효과:** {action['impact']}")
                    st.markdown(f"**📊 KPI:** {parsed['kpi']}")

                except Exception as e:
                    st.error(f"오류: {e}")
                    st.code(result if 'result' in dir() else "응답 없음")
        else:
            st.markdown("""
            <div style="text-align:center; padding:60px; color:#8cb8d8;">
            <div style="font-size:3rem;">🤖</div>
            <div style="font-size:1.2rem; margin-top:16px;">
            상품과 전략 방향을 선택 후<br>버튼을 눌러주세요
            </div>
            </div>
            """, unsafe_allow_html=True)

# ═════════════════════════════════════════════════════════
# P5 · 비즈니스 임팩트
# ═════════════════════════════════════════════════════════
elif page == "P5 · 비즈니스 임팩트":
    st.title("P5 · 비즈니스 임팩트")
    st.markdown("### CVR 개선 시나리오 — 얼마나 회복할 수 있나?")

    st.markdown("#### 🎛️ 시나리오 설정")
    col1, col2, col3 = st.columns(3)
    with col1:
        cvr_delta = st.slider("CVR_3 개선폭 (%p)", 1.0, 20.0, 5.0, 0.5)
    with col2:
        months = st.slider("분석 기간 (개월)", 3, 24, 12, 3)
    with col3:
        monthly_apply = st.number_input("월 신청 건수", value=15000, step=1000)

    # 계산
    current_cvr  = 0.795
    improved_cvr = current_cvr + cvr_delta / 100
    ltv          = 35000 * 36          # 월렌탈료 × 계약기간
    policy_cost  = 180000              # 정책금/건

    current_open  = monthly_apply * current_cvr
    improved_open = monthly_apply * improved_cvr
    incremental   = improved_open - current_open

    rev_month  = incremental * ltv
    rev_total  = rev_month * months
    policy_save= incremental * policy_cost * 1.3 * months
    total_effect = rev_total + policy_save
    roi        = (total_effect - 50_000_000) / 50_000_000 * 100

    st.markdown("---")
    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("CVR 개선",    f"{cvr_delta:+.1f}%p",  f"{current_cvr*100:.1f}% → {improved_cvr*100:.1f}%")
    k2.metric("월 추가 개통", f"+{incremental:,.0f}건")
    k3.metric("매출 증가",    f"{rev_total/1e8:.1f}억", f"{months}개월")
    k4.metric("정책금 절감",  f"{policy_save/1e6:.0f}M")
    k5.metric("ROI",         f"{roi:+.0f}%", "투자 5천만원 기준")

    st.markdown("---")

    # 누적 곡선
    months_axis = list(range(1, months + 1))
    scenarios = {
        "보수적 (+3%p)":         3.0,
        f"선택 (+{cvr_delta}%p)": cvr_delta,
        "적극적 (+10%p)":        10.0,
    }
    colors_sc = ["#8cb8d8", "#4db8ff", "#27ae60"]

    fig = go.Figure()
    for (label, delta), color in zip(scenarios.items(), colors_sc):
        incr = monthly_apply * (current_cvr + delta/100 - current_cvr)
        cumul = [incr * ltv * m / 1e8 for m in months_axis]
        width = 3 if delta == cvr_delta else 1.5
        dash  = "solid" if delta == cvr_delta else "dot"
        fig.add_trace(go.Scatter(
            x=months_axis, y=cumul,
            name=label, mode="lines",
            line=dict(color=color, width=width, dash=dash),
        ))
    fig.add_hline(y=0.05, line_dash="dash", line_color="#f39c12",
                  annotation_text="투자 회수선 (5천만원)",
                  annotation_font_color="#f39c12")
    fig.update_layout(
        title="누적 매출 회복 곡선",
        height=380, template="plotly_dark",
        xaxis=dict(title="경과 월"),
        yaxis=dict(title="누적 매출 증가 (억원)"),
        legend=dict(orientation="h", y=-0.15),
    )
    st.plotly_chart(fig, use_container_width=True)

    st.info(f"💡 CVR {cvr_delta}%p 개선 시 {months}개월간 총 **{total_effect/1e8:.1f}억원** 효과 (매출+정책금절감)")
