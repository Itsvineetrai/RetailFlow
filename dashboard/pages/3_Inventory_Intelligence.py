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


st.title("Inventory Intelligence")
st.caption(
    "Current inventory, demand coverage, stock risk, and replenishment"
)


try:
    inventory = get_gold("inventory_current")
    inventory_risk = get_gold("inventory_risk")

    # --------------------------------------------------
    # KPI CALCULATIONS
    # --------------------------------------------------

    total_inventory = int(
        inventory["inventory_quantity"].sum()
    )

    stockout_risk = int(
        (
            inventory_risk["inventory_risk"]
            == "STOCKOUT_RISK"
        ).sum()
    )

    high_risk = int(
        (
            inventory_risk["inventory_risk"]
            == "HIGH_RISK"
        ).sum()
    )

    watch = int(
        (
            inventory_risk["inventory_risk"]
            == "WATCH"
        ).sum()
    )

    reorder_units = int(
        inventory_risk[
            "recommended_reorder_quantity"
        ].sum()
    )

    # --------------------------------------------------
    # KPI CARDS
    # --------------------------------------------------

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Inventory Units",
            f"{total_inventory:,}",
        )

    with col2:
        st.metric(
            "Stockout Risk",
            stockout_risk,
        )

    with col3:
        st.metric(
            "High Risk",
            high_risk,
        )

    with col4:
        st.metric(
            "Recommended Reorder",
            f"{reorder_units:,} units",
        )

    st.divider()

    # --------------------------------------------------
    # RISK DISTRIBUTION
    # --------------------------------------------------

    st.subheader("Inventory Risk Distribution")

    risk_distribution = (
        inventory_risk[
            "inventory_risk"
        ]
        .value_counts()
        .rename_axis("inventory_risk")
        .reset_index(name="store_product_pairs")
    )

    risk_chart = px.bar(
        risk_distribution,
        x="inventory_risk",
        y="store_product_pairs",
        labels={
            "inventory_risk": "Risk",
            "store_product_pairs": "Store-Product Pairs",
        },
    )

    st.plotly_chart(
        risk_chart,
        use_container_width=True,
    )

    # --------------------------------------------------
    # CRITICAL INVENTORY
    # --------------------------------------------------

    st.subheader("Replenishment Alerts")

    reorder_alerts = inventory_risk[
        inventory_risk[
            "recommended_reorder_quantity"
        ] > 0
    ].copy()

    if reorder_alerts.empty:
        st.success(
            "No products currently require replenishment."
        )
    else:
        alert_display = reorder_alerts[
            [
                "store_name",
                "product_name",
                "inventory_quantity",
                "forecast_7d_demand",
                "days_of_inventory",
                "projected_inventory_7d",
                "inventory_risk",
                "recommended_reorder_quantity",
            ]
        ].sort_values(
            "recommended_reorder_quantity",
            ascending=False,
        )

        st.dataframe(
            alert_display,
            use_container_width=True,
            hide_index=True,
        )

    # --------------------------------------------------
    # INVENTORY COVERAGE
    # --------------------------------------------------

    st.subheader("Inventory Coverage")

    coverage_chart = px.scatter(
        inventory_risk,
        x="average_daily_demand",
        y="inventory_quantity",
        size="forecast_7d_demand",
        color="inventory_risk",
        hover_name="product_name",
        hover_data=[
            "store_name",
            "product_id",
            "days_of_inventory",
            "projected_inventory_7d",
        ],
        labels={
            "average_daily_demand": "Average Daily Demand",
            "inventory_quantity": "Current Inventory",
            "inventory_risk": "Risk",
        },
    )

    st.plotly_chart(
        coverage_chart,
        use_container_width=True,
    )

    # --------------------------------------------------
    # FULL INVENTORY RISK TABLE
    # --------------------------------------------------

    st.divider()

    st.subheader("Inventory Risk Detail")

    risk_display = inventory_risk[
        [
            "store_id",
            "store_name",
            "product_id",
            "product_name",
            "inventory_quantity",
            "forecast_7d_demand",
            "average_daily_demand",
            "days_of_inventory",
            "projected_inventory_7d",
            "inventory_risk",
            "recommended_reorder_quantity",
        ]
    ].sort_values(
        "days_of_inventory"
    )

    st.dataframe(
        risk_display,
        use_container_width=True,
        hide_index=True,
    )

    st.success(
        "Inventory Intelligence loaded successfully."
    )

except Exception as exc:
    st.error(
        "Unable to load Inventory Intelligence."
    )
    st.exception(exc)