import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

st.set_page_config(page_title="렌탈 고객 이탈 분석", layout="wide")

st.sidebar.markdown("## 💧 렌탈 이탈 분석")
st.sidebar.markdown("**Snowflake Hackathon 2026**")
st.sidebar.markdown("---")
page = st.sidebar.radio("페이지 선택", [
    "P1 · 문제 정의",
    "P2 · 변곡점 원인",
    "P3 · 상품 분석",
    "P4 · 전략 가이드",
    "P5 · 비즈니스 임팩트",
])
st.sidebar.markdown("---")
st.sidebar.caption("📂 데이터: South Korea Telecom Subscription Analytics (Snowflake Marketplace)")

@st.cache_data
def load_data():
    v03 = pd.read_csv("streamlit-cloud/data/v03_funnel.csv")
    v06 = pd.read_csv("streamlit-cloud/data/v06_category.csv")
    v04 = pd.read_csv("streamlit-cloud/data/v04_channel.csv")
    for df in [v03, v06, v04]:
        df.columns = df.columns.str.lower()
    v03["year_month"] = pd.to_datetime(v03["year_month"])
    v06["year_month"] = pd.to_datetime(v06["year_month"])
    v04["year_month"] = pd.to_datetime(v04["year_month"])
    v03["cvr_3"] = v03["open_count"] / v03["registend_count"].replace(0, float("nan"))
    v06["open_cvr"] = v06["open_count"] / v06["contract_count"].replace(0, float("nan"))
    return v03, v06, v04

v03, v06, v04 = load_data()

total_apply = v03["subscription_count"].sum()
total_reg   = v03["registend_count"].sum()
total_open  = v03["open_count"].sum()

funnel = pd.DataFrame({
    "STAGE":      ["1.신청", "2.등록완료", "3.개통완료"],
    "STAGE_ORDER":[1, 2, 3],
    "CNT":        [total_apply, total_reg, total_open],
})

cvr_df = v03.groupby("year_month").agg(
    reg=("registend_count","sum"),
    open=("open_count","sum"),
).reset_index()
cvr_df["cvr_3"] = cvr_df["open"] / cvr_df["reg"]
cvr_df["ym"]    = cvr_df["year_month"].dt.strftime("%Y-%m")
cvr_df["ma3"]   = cvr_df["cvr_3"].rolling(3, min_periods=1).mean()

prod_df = v06.groupby("rental_sub_category").agg(
    contract=("contract_count","sum"),
    open=("open_count","sum"),
).reset_index()
prod_df["cvr_pct"] = prod_df["open"] / prod_df["contract"] * 100
prod_df = prod_df.sort_values("contract", ascending=False)

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
            y=funnel["STAGE"], x=funnel["CNT"],
            textinfo="value+percent previous",
            marker=dict(color=["#2980b9","#f39c12","#e74c3c"]),
        ))
        fig.update_layout(title="고객 획득 퍼널", height=400, template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        churn_1 = total_apply - total_reg
        churn_2 = total_reg - total_open
        st.markdown("#### 📌 핵심 이탈 구간")
        st.markdown(f"""
        | 구간 | CVR | 이탈 규모 |
        |------|-----|---------|
        | 신청 → 등록 | {cvr_2:.1f}% | {churn_1:,.0f}건 |
        | 등록 → 개통 | **{cvr_3:.1f}%** | **{churn_2:,.0f}건** ⚠️ |
        | 전체 | {total_open/total_apply*100:.1f}% | {total_apply-total_open:,.0f}건 |
        """)
        st.error("💡 등록→개통 구간이 핵심 이탈 포인트")
        st.markdown("#### 💸 이중 손실 구조")
        st.markdown("""
        - **매출 손실**: 이탈 고객 × LTV
        - **정책금 낭비**: 이미 집행된 설치비·사은품
        - **손실 배율**: 매출 손실의 **1.3배** 실제 손실
        """)
        st.warning("이탈 1건 = 매출 손실 + 회수 불가 정책금")

elif page == "P2 · 변곡점 원인":
    st.title("P2 · 변곡점 원인")
    st.markdown("### 2023년 하반기, CVR이 왜 꺾였나?")
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=cvr_df["ym"], y=cvr_df["cvr_3"],
        mode="lines+markers", name="CVR_3",
        line=dict(color="#e74c3c", width=2),
        fill="tozeroy", fillcolor="rgba(231,76,60,0.1)",
    ))
    fig.add_trace(go.Scatter(
        x=cvr_df["ym"], y=cvr_df["ma3"],
        mode="lines", name="3개월 이동평균",
        line=dict(color="#f39c12", width=2, dash="dash"),
    ))
    fig.add_shape(type="line", x0="2023-08", x1="2023-08", y0=0, y1=1,
                  xref="x", yref="paper", line=dict(color="#4db8ff", dash="dash", width=2))
    fig.add_annotation(x="2023-08", y=0.97, xref="x", yref="paper",
                       text="📍 다품목 확장 시작", font=dict(color="#4db8ff", size=12), showarrow=False)
    fig.update_layout(title="월별 CVR_3 추이 (등록→개통)", height=430, template="plotly_dark",
                      xaxis=dict(tickangle=-45), yaxis=dict(title="CVR", tickformat=".0%"),
                      legend=dict(orientation="h", y=-0.15))
    st.plotly_chart(fig, use_container_width=True)
    col1, col2, col3 = st.columns(3)
    col1.error("**정수기 CVR**\n\n87.4% → 78.2%\n\n-9.3%p 꺾임")
    col2.warning("**원인 진단**\n\n2023-08 다품목 한꺼번에 추가\n\n운영 준비 미흡")
    col3.info("**영향**\n\n저CVR 상품 비중 증가\n\n전체 평균 CVR 하락")

elif page == "P3 · 상품 분석":
    st.title("P3 · 상품 분석")
    st.markdown("### 어떤 상품이 CVR을 끌어내리나?")

    top15 = prod_df.head(15).copy()
    total_contract = top15["contract"].sum()
    top15["volume_share"] = top15["contract"] / total_contract * 100

    def cvr_color(v):
        if v >= 65:   return "#27ae60"
        elif v >= 40: return "#f39c12"
        else:         return "#e74c3c"

    # 버블차트
    st.markdown("#### 📊 CVR × 볼륨 비중 매트릭스 (버블 크기 = 계약건수 비중)")
    fig = go.Figure()
    for _, row in top15.iterrows():
        fig.add_trace(go.Scatter(
            x=[row["cvr_pct"]],
            y=[row["volume_share"]],
            mode="markers+text",
            name=row["rental_sub_category"],
            text=[row["rental_sub_category"]],
            textposition="top center",
            textfont=dict(size=10),
            marker=dict(
                size=row["volume_share"] * 4 + 10,
                color=cvr_color(row["cvr_pct"]),
                opacity=0.8,
                line=dict(color="white", width=1.5),
            ),
            hovertemplate=(
                f"<b>{row['rental_sub_category']}</b><br>"
                f"CVR: {row['cvr_pct']:.1f}%<br>"
                f"볼륨 비중: {row['volume_share']:.1f}%<br>"
                f"계약건수: {row['contract']:,.0f}건"
                "<extra></extra>"
            ),
        ))
    fig.add_vline(x=65, line_dash="dot", line_color="#27ae60",
                  annotation_text="우수 기준 65%", annotation_font_color="#27ae60")
    fig.add_vline(x=40, line_dash="dot", line_color="#f39c12",
                  annotation_text="위험 기준 40%", annotation_font_color="#f39c12")
    fig.update_layout(
        height=520, template="plotly_dark",
        xaxis=dict(title="CVR_3 (%)", range=[0, 105], gridcolor="#1e3a5f"),
        yaxis=dict(title="볼륨 비중 (%)", gridcolor="#1e3a5f"),
        showlegend=False, margin=dict(t=20),
    )
    st.plotly_chart(fig, use_container_width=True)

    # 바차트 2개
    st.markdown("#### 📋 상품별 CVR + 볼륨 비중 상세")
    col1, col2 = st.columns(2)
    with col1:
        fig2 = go.Figure(go.Bar(
            x=top15["rental_sub_category"], y=top15["cvr_pct"],
            marker_color=[cvr_color(v) for v in top15["cvr_pct"]],
            text=[f"{v:.1f}%" for v in top15["cvr_pct"]],
            textposition="outside",
        ))
        fig2.add_hline(y=65, line_dash="dot", line_color="#27ae60")
        fig2.add_hline(y=40, line_dash="dot", line_color="#f39c12")
        fig2.update_layout(title="CVR_3 (%)", height=380, template="plotly_dark",
                           xaxis=dict(tickangle=-30), yaxis=dict(range=[0, 110]),
                           showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)
    with col2:
        fig3 = go.Figure(go.Bar(
            x=top15["rental_sub_category"], y=top15["volume_share"],
            marker_color=[cvr_color(v) for v in top15["cvr_pct"]],
            text=[f"{v:.1f}%" for v in top15["volume_share"]],
            textposition="outside",
        ))
        fig3.update_layout(title="볼륨 비중 (%)", height=380, template="plotly_dark",
                           xaxis=dict(tickangle=-30),
                           yaxis=dict(range=[0, top15["volume_share"].max()*1.3]),
                           showlegend=False)
        st.plotly_chart(fig3, use_container_width=True)

    # 전략 분류
    st.markdown("#### 🎯 전략 분류")
    c1, c2, c3 = st.columns(3)
    good = top15[top15["cvr_pct"] >= 65]["rental_sub_category"].tolist()
    warn = top15[(top15["cvr_pct"] >= 40) & (top15["cvr_pct"] < 65)]["rental_sub_category"].tolist()
    bad  = top15[top15["cvr_pct"] < 40]["rental_sub_category"].tolist()
    c1.success("✅ **Defense/Leverage** (65%+)\n\n" + ", ".join(good))
    if warn: c2.warning("⚠️ **개선 필요** (40~65%)\n\n" + ", ".join(warn))
    c3.error("❌ **Recovery 필요** (~40%)\n\n" + ", ".join(bad))

elif page == "P4 · 전략 가이드":
    st.title("P4 · Retention 전략 가이드")
    st.markdown("### 상품별 맞춤 전략 — 비데 성공사례 기반")
    st.info("💡 Snowflake 버전에서는 Cortex AI가 상품별 전략을 자동 생성합니다.")
    STRATEGIES = {
        "🔴 Defense — 정수기": {
            "cvr": "76.9%", "zone": "Defense",
            "desc": "볼륨 1위 상품. 절대 손실 최대 → 지키는 전략 최우선",
            "actions": [
                ("개통 전 리마인더 강화", "등록 완료 후 D-3, D-1 자동 문자 발송", "CVR +3~5%p 예상"),
                ("설치 일정 즉시 확정", "계약 후 24시간 내 설치 날짜 확정 안내", "고객 불안감 해소"),
                ("필터 교체 사전 안내", "개통 전 필터 관리 가이드 제공", "장기 유지율 향상"),
            ]
        },
        "🟠 Recovery — 세탁기": {
            "cvr": "33.4%", "zone": "Recovery",
            "desc": "대형가전 설치 복잡도 높음 → 프로세스 개선 필요",
            "actions": [
                ("전담 설치기사 배정", "세탁기 특화 기사 풀 구성, 계약 즉시 배정", "설치 취소율 -20% 예상"),
                ("설치 전 사전 점검", "배수구/전용 콘센트 사전 확인 서비스", "당일 설치 실패 방지"),
                ("비데 넛지 전략 적용", "D-7, D-3, D-1 단계별 맞춤 메시지", "비데 +12.3%p 동일 적용"),
            ]
        },
        "🟠 Recovery — 에어컨": {
            "cvr": "31.7%", "zone": "Recovery",
            "desc": "계절성 상품 → 시즌 전 사전 예약 전환 전략",
            "actions": [
                ("시즌 전 사전 예약", "3~4월 계약 → 5월 설치 사전 예약 시스템", "성수기 이탈 방지"),
                ("설치 일정 우선 배정", "사전 예약자 설치 일정 우선권 부여", "CVR +5%p 예상"),
                ("설치 복잡도 안내", "계약 전 설치 조건 사전 체크리스트 제공", "계약 취소 방지"),
            ]
        },
        "🟢 Leverage — 비데": {
            "cvr": "77.1%", "zone": "Leverage",
            "desc": "+12.3%p 이미 달성한 성공 모델 → 타 상품 전파",
            "actions": [
                ("성공 프로세스 문서화", "비데 넛지 전략 SOP 작성", "타 상품 적용 가이드"),
                ("세탁기·에어컨 적용", "동일 D-7, D-3, D-1 리마인더 적용", "CVR +6~10%p 예상"),
                ("담당자 교육", "비데 성공사례 전사 공유 및 교육", "전사 CVR 개선"),
            ]
        },
    }
    selected = st.selectbox("전략 선택", list(STRATEGIES.keys()))
    s = STRATEGIES[selected]
    col1, col2 = st.columns([1, 3])
    with col1:
        st.metric("CVR", s["cvr"])
        st.markdown(f"**Zone:** {s['zone']}")
        st.markdown(s["desc"])
    with col2:
        for i, (title, detail, impact) in enumerate(s["actions"]):
            with st.expander(f"Action {i+1}: {title}"):
                st.markdown(f"**실행방법:** {detail}")
                st.success(f"**예상효과:** {impact}")

elif page == "P5 · 비즈니스 임팩트":
    st.title("P5 · 비즈니스 임팩트")
    st.markdown("### CVR 개선 시나리오 — 얼마나 회복할 수 있나?")
    col1, col2, col3 = st.columns(3)
    with col1:
        cvr_delta = st.slider("CVR_3 개선폭 (%p)", 1.0, 20.0, 5.0, 0.5)
    with col2:
        months = st.slider("분석 기간 (개월)", 3, 24, 12, 3)
    with col3:
        monthly_apply = st.number_input("월 신청 건수", value=15000, step=1000)
    current_cvr  = 0.795
    improved_cvr = current_cvr + cvr_delta / 100
    ltv          = 35000 * 36
    policy_cost  = 180000
    incremental  = monthly_apply * (improved_cvr - current_cvr)
    rev_total    = incremental * ltv * months
    policy_save  = incremental * policy_cost * 1.3 * months
    total_effect = rev_total + policy_save
    roi          = (total_effect - 50_000_000) / 50_000_000 * 100
    st.markdown("---")
    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("CVR 개선",    f"{cvr_delta:+.1f}%p", f"{current_cvr*100:.1f}% → {improved_cvr*100:.1f}%")
    k2.metric("월 추가 개통", f"+{incremental:,.0f}건")
    k3.metric("매출 증가",    f"{rev_total/1e8:.1f}억", f"{months}개월")
    k4.metric("정책금 절감",  f"{policy_save/1e6:.0f}M")
    k5.metric("ROI",         f"{roi:+.0f}%", "투자 5천만원 기준")
    st.markdown("---")
    months_axis = list(range(1, months + 1))
    scenarios = {"보수적 (+3%p)": 3.0, f"선택 (+{cvr_delta}%p)": cvr_delta, "적극적 (+10%p)": 10.0}
    colors_sc = ["#8cb8d8", "#4db8ff", "#27ae60"]
    fig = go.Figure()
    for (label, delta), color in zip(scenarios.items(), colors_sc):
        incr  = monthly_apply * (delta / 100)
        cumul = [incr * ltv * m / 1e8 for m in months_axis]
        fig.add_trace(go.Scatter(x=months_axis, y=cumul, name=label, mode="lines",
                                 line=dict(color=color, width=3 if delta==cvr_delta else 1.5,
                                           dash="solid" if delta==cvr_delta else "dot")))
    fig.add_hline(y=0.05, line_dash="dash", line_color="#f39c12",
                  annotation_text="투자 회수선 (5천만원)", annotation_font_color="#f39c12")
    fig.update_layout(title="누적 매출 회복 곡선", height=380, template="plotly_dark",
                      xaxis=dict(title="경과 월"), yaxis=dict(title="누적 매출 증가 (억원)"),
                      legend=dict(orientation="h", y=-0.15))
    st.plotly_chart(fig, use_container_width=True)
    st.info(f"💡 CVR {cvr_delta}%p 개선 시 {months}개월간 총 **{total_effect/1e8:.1f}억원** 효과")
