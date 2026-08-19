import streamlit as st


st.set_page_config(
    page_title="RetailFlow Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


st.sidebar.title("RetailFlow")
st.sidebar.caption(
    "Scalable Retail Data Platform"
)

st.sidebar.divider()

st.sidebar.markdown(
    """
    **Data Platform**

    Kafka → Spark → Silver → Gold

    **Analytics**

    Financials · Inventory · Forecasting
    """
)

st.sidebar.divider()

st.sidebar.caption(
    "Gold-layer analytics dashboard"
)

pages = [
    st.Page(
        "pages/1_Executive_Overview.py",
        title="Executive Overview",
        icon="📊",
    ),
    st.Page(
        "pages/2_Sales_and_Finance.py",
        title="Sales & Finance",
        icon="💰",
    ),
    st.Page(
        "pages/3_Inventory_Intelligence.py",
        title="Inventory Intelligence",
        icon="📦",
    ),
    st.Page(
        "pages/4_Demand_Forecast.py",
        title="Demand Forecast",
        icon="📈",
    ),
]

navigation = st.navigation(pages)

navigation.run()