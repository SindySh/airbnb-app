import streamlit as st
import pandas as pd
from database import (
    create_tables,
    add_booking,
    get_bookings,
    add_expense,
    get_expenses
)

st.markdown("""
<link rel="manifest" href="./static/manifest.json">
<meta name="theme-color" content="#0e1117">
""", unsafe_allow_html=True)

page = st.radio(
    "",
    ["🏠 Dashboard", "📅 Bookings", "💸 Expenses", "📊 Reports"],
    horizontal=True
)

st.set_page_config(
    page_title="Airbnb Analyzer",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

.block-container {
    padding-top: 1rem;
    padding-bottom: 2rem;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div style="
    font-size:24px;
    font-weight:600;
    padding:10px 0;
">
Airbnb Analytics
</div>
""", unsafe_allow_html=True)

def card(title, value, icon="📊"):
    st.markdown(f"""
    <div style="
        padding:16px;
        border-radius:12px;
        background-color:#111;
        color:white;
        margin-bottom:10px;
        border:1px solid #333;
    ">
        <h4 style="margin:0;">{icon} {title}</h4>
        <h2 style="margin:0;">{value}</h2>
    </div>
    """, unsafe_allow_html=True)

create_tables()

st.title("Welcome to Airbnb Analyzer")
st.markdown("Track revenue, expenses, occupancy, and profit in one place.")
st.divider()

bookings = get_bookings()
expenses = get_expenses()

# ---------------- DATA ----------------
if len(bookings) > 0:
    df = pd.DataFrame(bookings, columns=[
        "id", "guest_name", "check_in", "check_out",
        "revenue", "booking_source"
    ])
    df["check_in"] = pd.to_datetime(df["check_in"])
    df["month"] = df["check_in"].dt.to_period("M").astype(str)
else:
    df = pd.DataFrame(columns=[
        "id", "guest_name", "check_in", "check_out",
        "revenue", "booking_source", "month"
    ])

if len(expenses) > 0:
    exp_df = pd.DataFrame(expenses, columns=[
        "id", "date", "category", "amount", "notes"
    ])
    exp_df["date"] = pd.to_datetime(exp_df["date"])
    exp_df["month"] = exp_df["date"].dt.to_period("M").astype(str)
else:
    exp_df = pd.DataFrame(columns=[
        "id", "date", "category", "amount", "notes", "month"
    ])

# Calculate occupancy
if not df.empty:
    df["check_out"] = pd.to_datetime(df["check_out"])
    df["nights"] = (df["check_out"] - df["check_in"]).dt.days
    occupancy = (df["nights"].sum() / 30) * 100
else:
    occupancy = 0

# ======================================================
# DASHBOARD
# ======================================================
if page == "🏠 Dashboard":

    st.header("🏠 Dashboard")

    total_revenue = df["revenue"].sum()
    total_expenses = exp_df["amount"].sum()
    profit = total_revenue - total_expenses

    col1, col2, col3 = st.columns(3)
    col1.metric("Revenue", f"€{total_revenue}")
    col2.metric("Expenses", f"€{total_expenses}")
    col3.metric("Profit", f"€{profit}")

    st.bar_chart(pd.DataFrame({
        "Category": ["Revenue", "Expenses"],
        "Amount": [total_revenue, total_expenses]
    }).set_index("Category"))

# ======================================================
# BOOKINGS
# ======================================================
elif page == "📅 Bookings":

    st.header("📅 Bookings")
    if not df.empty:
        st.dataframe(df, use_container_width=True, hide_index=True)

        booked_dates = []
        for _, row in df.iterrows():
            dates = pd.date_range(row["check_in"], row["check_out"])
            booked_dates.extend(dates)

        booked_df = pd.DataFrame(booked_dates, columns=["date"])
        booked_df["count"] = 1

        df["check_out"] = pd.to_datetime(df["check_out"])
        df["nights"] = (df["check_out"] - df["check_in"]).dt.days

        occupancy_df = pd.DataFrame({
            "Metric": ["Booked Nights", "Total Days (30)"],
            "Value": [df["nights"].sum(), 30]
        })

        st.subheader("Occupancy Overview")
        st.bar_chart(occupancy_df.set_index("Metric"))

        occupancy = (df["nights"].sum() / 30) * 100
        st.metric("Occupancy (%)", round(occupancy, 2))

    else:
        st.info("No bookings yet")
        occupancy = 0

    # ---------------- ADD BOOKING SECTION ----------------
    with st.expander("Add New Booking"):

        c1, c2, c3 = st.columns(3)

        with c1:
            guest = st.text_input("Guest Name", key="guest")

        with c2:
            check_in = st.date_input("Check-in", key="checkin")

        with c3:
            check_out = st.date_input("Check-out", key="checkout")

        revenue = st.number_input("Revenue (€)")
        source = st.text_input("Source")

        if st.button("Save Booking"):
            add_booking(guest, str(check_in), str(check_out), revenue, source)
            st.success("Booking saved!")

# ======================================================
# EXPENSES
# ======================================================
elif page == "💸 Expenses":

    st.header("Add Expense")

    exp_date = st.date_input("Date", key="exp_date")

    category = st.selectbox(
        "Category",
        ["Rent", "Utilities", "WiFi", "Taxes", "Supplies", "Repairs", "Other"]
    )

    if category == "Other":
        category = st.text_input("Custom Category")

    amount = st.number_input("Amount (€)")
    notes = st.text_input("Notes")

    if st.button("Save Expense"):
        add_expense(str(exp_date), category, amount, notes)
        st.success("Expense saved!")

# ======================================================
# REPORTS
# ======================================================
elif page == "📊 Reports":

    st.header("Monthly Report")

    current_month = str(pd.Timestamp.today().to_period("M"))

    month_revenue = df[df["month"] == current_month]["revenue"].sum()
    month_expenses = exp_df[exp_df["month"] == current_month]["amount"].sum()
    month_profit = month_revenue - month_expenses

    st.write(f"Revenue: €{month_revenue}")
    st.write(f"Expenses: €{month_expenses}")
    st.write(f"Profit: €{month_profit}")

    st.subheader("Insights")

    if month_profit > 0:
        st.success("Your Airbnb is profitable this month.")
    else:
        st.error("Your expenses are higher than revenue!")

    if occupancy > 70:
        st.success("High occupancy — consider increasing prices!")
    elif occupancy < 40:
        st.warning("Low occupancy — consider marketing or discounts.")
    else:
        st.info("Stable occupancy performance.")

    st.subheader("Forecast")

    monthly = pd.DataFrame({
    "revenue": df.groupby("month")["revenue"].sum(),
    "expenses": exp_df.groupby("month")["amount"].sum()
    }).fillna(0)

    monthly["profit"] = monthly["revenue"] - monthly["expenses"]

    if len(monthly) > 0:
        forecast_profit = monthly["profit"].mean()
    else:
        forecast_profit = 0

    st.metric("Next Month Forecast", f"€{round(forecast_profit, 2)}")
    st.info("Prediction is based on average monthly profit (simple trend model).")

# ---------------- DYNAMIC PRICING SYSTEM ----------------

    st.subheader("Pricing Engine")

    if not df.empty:

        df["check_in"] = pd.to_datetime(df["check_in"])
        df["check_out"] = pd.to_datetime(df["check_out"])
        df["month_num"] = df["check_in"].dt.month

        df["nights"] = (df["check_out"] - df["check_in"]).dt.days

        total_nights = df["nights"].sum()
        occupancy = (total_nights / 30) * 100

        base_price = df["revenue"].sum() / total_nights if total_nights > 0 else 0

    # ---------------- SEASON FACTOR ----------------
        current_month = pd.Timestamp.today().month

        if current_month in [6, 7, 8, 12]:  # summer + holidays
            season_factor = 1.25
            season_label = "High Season (Summer/Holidays)"
        elif current_month in [4, 5, 9, 10]:
            season_factor = 1.0
            season_label = "Mid Season"
        else:
            season_factor = 0.85
            season_label = "Low Season (Winter)"

    # ---------------- DEMAND FACTOR ----------------
        if occupancy > 80:
            demand_factor = 1.2
            demand_label = "High Demand"
        elif occupancy < 40:
            demand_factor = 0.85
            demand_label = "Low Demand"
        else:
            demand_factor = 1.0
            demand_label = "Normal Demand"

    # ---------------- FINAL PRICE ----------------
        suggested_price = base_price * season_factor * demand_factor

        st.write(f"Season: {season_label}")
        st.write(f"Demand: {demand_label}")
        st.write(f"Occupancy: {round(occupancy, 2)}%")

        st.metric("Dynamic Nightly Price", f"€{round(suggested_price, 2)}")

    else:
        st.warning("Not enough data for dynamic pricing.")