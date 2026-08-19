import streamlit as st
import plotly.express as px

from dashboard.config import get_storage_options
from dashboard.data_loader import load_dataset


@st.cache_data(ttl=300)
def get_gold(dataset):
    storage_options = get_storage_options()
    return load_dataset(
        dataset,
        storage_options,
    )


st.title("RetailFlow Analytics")
st.caption("Executive Overview")


try:
    financial_summary = get_gold("financial_summary")
    daily_sales = get_gold("daily_sales")
    store_sales = get_gold("store_sales")
    category_sales = get_gold("category_sales")

    summary = financial_summary.iloc[0]

    # -----------------------------
    # KPI CARDS
    # -----------------------------

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Total Revenue",
            f"₹{summary['total_revenue']:,.0f}",
        )

    with col2:
        st.metric(
            "Transactions",
            f"{daily_sales['transactions'].sum():,.0f}",
        )

    with col3:
        st.metric(
            "Average Transaction",
            f"₹{summary['average_transaction_value']:,.2f}",
        )

    with col4:
        st.metric(
            "Total Discount",
            f"₹{summary['total_discount']:,.0f}",
        )

    st.divider()

    # -----------------------------
    # REVENUE TREND
    # -----------------------------

    st.subheader("Revenue Trend")

    daily_sales = daily_sales.copy()
    daily_sales["date"] = daily_sales["date"].astype(str)

    revenue_chart = px.line(
        daily_sales,
        x="date",
        y="revenue",
        markers=True,
        labels={
            "date": "Date",
            "revenue": "Revenue",
        },
    )

    revenue_chart.update_layout(
        xaxis_title="Date",
        yaxis_title="Revenue",
        hovermode="x unified",
    )

    st.plotly_chart(
        revenue_chart,
        use_container_width=True,
    )

    # -----------------------------
    # STORE + CATEGORY
    # -----------------------------

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Revenue by Store")

        store_chart = px.bar(
            store_sales.sort_values(
                "revenue",
                ascending=False,
            ),
            x="store_name",
            y="revenue",
            labels={
                "store_name": "Store",
                "revenue": "Revenue",
            },
        )

        store_chart.update_layout(
            xaxis_title=None,
            yaxis_title="Revenue",
        )

        st.plotly_chart(
            store_chart,
            use_container_width=True,
        )

    with col2:
        st.subheader("Revenue by Category")

        category_chart = px.pie(
            category_sales,
            names="category",
            values="revenue",
            hole=0.45,
        )

        st.plotly_chart(
            category_chart,
            use_container_width=True,
        )

    # -----------------------------
    # STORE TABLE
    # -----------------------------

    st.divider()

    st.subheader("Store Performance")

    store_display = store_sales.copy()

    store_display["revenue"] = store_display[
        "revenue"
    ].map(
        lambda value: f"₹{value:,.0f}"
    )

    store_display["average_sale"] = store_display[
        "average_sale"
    ].map(
        lambda value: f"₹{value:,.2f}"
    )

    st.dataframe(
        store_display,
        use_container_width=True,
        hide_index=True,
    )

    st.success(
        "Executive Overview loaded from Gold successfully."
    )

except Exception as exc:
    st.error("Unable to load Executive Overview.")
    st.exception(exc)