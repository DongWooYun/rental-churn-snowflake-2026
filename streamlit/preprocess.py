
from snowflake.snowpark import Session
import pandas as pd

connection_params = {
    "account": "ptrylrq-nm81160",
    "user": "DONGWOOYUN",
    "password": "YOUR_PASSWORD",  # 실제 비밀번호는 입력하지 말 것
    "warehouse": "COMPUTE_WH",
    "database": "SOUTH_KOREA_TELECOM_SUBSCRIPTION_ANALYTICS__CONTRACTS_MARKETING_AND_CALL_CENTER_INSIGHTS_BY_REGION",
    "schema": "TELECOM_INSIGHTS"
}

session = Session.builder.configs(connection_params).create()

DB = "SOUTH_KOREA_TELECOM_SUBSCRIPTION_ANALYTICS__CONTRACTS_MARKETING_AND_CALL_CENTER_INSIGHTS_BY_REGION.TELECOM_INSIGHTS"

# V03
df_v03 = session.sql(f"""
    SELECT YEAR_MONTH, MAIN_CATEGORY_NAME,
        CONSULT_REQUEST_COUNT, SUBSCRIPTION_COUNT,
        REGISTEND_COUNT, OPEN_COUNT, PAYEND_COUNT
    FROM {DB}.V03_CONTRACT_FUNNEL_CONVERSION
    WHERE MAIN_CATEGORY_NAME = '렌탈'
        AND YEAR_MONTH <= '2026-03-01'
    ORDER BY YEAR_MONTH
""").to_pandas()
df_v03.columns = df_v03.columns.str.lower()
df_v03['year_month'] = pd.to_datetime(df_v03['year_month'])
df_v03['cvr_2'] = df_v03['registend_count'] / df_v03['subscription_count'].replace(0, float('nan'))
df_v03['cvr_3'] = df_v03['open_count'] / df_v03['registend_count'].replace(0, float('nan'))
df_v03['cvr_4'] = df_v03['payend_count'] / df_v03['open_count'].replace(0, float('nan'))

# V06
df_v06 = session.sql(f"""
    SELECT YEAR_MONTH, INSTALL_STATE,
        RENTAL_MAIN_CATEGORY, RENTAL_SUB_CATEGORY,
        CONTRACT_COUNT, OPEN_COUNT, PAYEND_COUNT
    FROM {DB}.V06_RENTAL_CATEGORY_TRENDS
    WHERE YEAR_MONTH <= '2026-03-01'
    ORDER BY YEAR_MONTH
""").to_pandas()
df_v06.columns = df_v06.columns.str.lower()
df_v06['year_month'] = pd.to_datetime(df_v06['year_month'])
df_v06['open_cvr'] = df_v06['open_count'] / df_v06['contract_count'].replace(0, float('nan'))
df_v06['payend_cvr'] = df_v06['payend_count'] / df_v06['contract_count'].replace(0, float('nan'))

# V04
df_v04 = session.sql(f"""
    SELECT YEAR_MONTH, RECEIVE_PATH_NAME, INFLOW_PATH_NAME,
        CONTRACT_COUNT, OPEN_COUNT, PAYEND_COUNT, AVG_NET_SALES
    FROM {DB}.V04_CHANNEL_CONTRACT_PERFORMANCE
    WHERE MAIN_CATEGORY_NAME = '렌탈'
        AND YEAR_MONTH <= '2026-03-01'
    ORDER BY YEAR_MONTH
""").to_pandas()
df_v04.columns = df_v04.columns.str.lower()
df_v04['year_month'] = pd.to_datetime(df_v04['year_month'])
df_v04['open_cvr'] = df_v04['open_count'] / df_v04['contract_count'].replace(0, float('nan'))
df_v04['payend_cvr'] = df_v04['payend_count'] / df_v04['contract_count'].replace(0, float('nan'))

print("✅ 전처리 완료")
print(f"V03: {df_v03.shape}, V06: {df_v06.shape}, V04: {df_v04.shape}")
