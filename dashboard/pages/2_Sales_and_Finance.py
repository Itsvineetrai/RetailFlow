import streamlit as st
import plotly.express as px

from dashboard.config import get_storage_options
from dashboard.data_loader import load_dataset


st.set_page_config(
    page_title="Sales & Finance",
    page_icon="Sales",
    layout="wide",
)


@st.cache_data(ttl=300)
def get_gold(dataset):
    storage_options = get_storage_options()

    return load_dataset(
        dataset,
        storage_options,
    )


st.title("Sales & Finance")
st.caption("Financial performance from the validated Gold layer")


try:
    daily_sales = get_gold("daily_sales")
    payment_summary = get_gold("payment_summary")
    payment_finance = get_gold("payment_finance")
    top_products = get_gold("top_products")
    city_sales = get_gold("city_sales")

    daily_sales["date"] = daily_sales["date"].astype(str)

    min_date = daily_sales["date"].min()
    max_date = daily_sales["date"].max()

    st.info(
        f"Available sales period: {min_date} to {max_date}"
    )

    st.subheader("Daily Revenue")

    revenue_chart = px.line(
        daily_sales,
        x="date",
        y="revenue",
        labels={
            "date": "Date",
            "revenue": "Revenue",
        },
    )

    revenue_chart.update_layout(
        hovermode="x unified",
    )

    st.plotly_chart(
        revenue_chart,
        use_container_width=True,
    )

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Payment Method Revenue")

        payment_chart = px.bar(
            payment_summary.sort_values(
                "revenue",
                ascending=False,
            ),
            x="payment_method",
            y="revenue",
            labels={
                "payment_method": "Payment Method",
                "revenue": "Revenue",
            },
        )

        st.plotly_chart(
            payment_chart,
            use_container_width=True,
        )

    with col2:
        st.subheader("City Revenue")

        city_chart = px.bar(
            city_sales.sort_values(
                "revenue",
                ascending=False,
            ),
            x="city",
            y="revenue",
            labels={
                "city": "City",
                "revenue": "Revenue",
            },
        )

        st.plotly_chart(
            city_chart,
            use_container_width=True,
        )

    st.divider()

    st.subheader("Top Products")

    product_chart = px.bar(
        top_products.sort_values(
            "revenue",
            ascending=False,
        ),
        x="revenue",
        y="product_name",
        orientation="h",
        labels={
            "revenue": "Revenue",
            "product_name": "Product",
        },
    )

    st.plotly_chart(
        product_chart,
        use_container_width=True,
    )

    st.subheader("Payment Finance")

    payment_finance_display = payment_finance.copy()

    for column in [
        "revenue",
        "tax",
        "discount",
    ]:
        payment_finance_display[column] = (
            payment_finance_display[column]
            .map(lambda value: f"₹{value:,.0f}")
        )

    st.dataframe(
        payment_finance_display,
        use_container_width=True,
        hide_index=True,
    )

    st.success(
        "Sales & Finance loaded successfully."
    )

except Exception as exc:
    st.error(
        "Unable to load Sales & Finance."
    )
    st.exception(exc)