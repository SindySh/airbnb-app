import streamlit as st
import pandas as pd
import database

st.set_page_config(
    page_title="Airbnb Analyzer",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
.block-container {padding-top: 1rem; padding-bottom: 2rem;}
</style>
""", unsafe_allow_html=True)

st.title("Airbnb Analytics")
st.markdown("Welcome to Airbnb Analyzer")
st.markdown("Track revenue, expenses, occupancy, and profit in one place.")
st.divider()
# ===================== NAVIGATION (MOBILE FRIENDLY) =====================

st.markdown("""
<div style="
    display:flex;
    justify-content:space-between;
    align-items:center;
    padding:10px 0;
    font-size:20px;
    font-weight:600;
">
    ☰ Airbnb Analytics
</div>
""", unsafe_allow_html=True)

page = st.selectbox(
    "Navigation",
    ["Dashboard", "Bookings", "Expenses", "Reports"]
)

bookings = database.get_bookings()
expenses = database.get_expenses()

df = pd.DataFrame(bookings)

if not df.empty:
    df["check_in"] = pd.to_datetime(df["check_in"], errors="coerce")
    df["check_out"] = pd.to_datetime(df["check_out"], errors="coerce")

    df["nights"] = (df["check_out"] - df["check_in"]).dt.days
    df["month"] = df["check_in"].dt.strftime("%Y-%m")
else:
    df = pd.DataFrame(columns=[
        "id", "guest_name", "check_in", "check_out",
        "revenue", "booking_source", "nights", "month"
    ])

# EXPENSES
exp_df = pd.DataFrame(expenses)

if not exp_df.empty:
    exp_df["date"] = pd.to_datetime(exp_df["date"], errors="coerce")
    exp_df["month"] = exp_df["date"].dt.strftime("%Y-%m")
else:
    exp_df = pd.DataFrame(columns=[
        "id", "date", "category", "amount", "notes", "month"
    ])

# ===================== GLOBAL METRICS =====================
total_revenue = df["revenue"].sum() if not df.empty else 0
total_expenses = exp_df["amount"].sum() if not exp_df.empty else 0
profit = total_revenue - total_expenses

occupancy = (df["nights"].sum() / 30 * 100) if not df.empty else 0

# ===================== DASHBOARD =====================
if page == "Dashboard":

    st.header("Dashboard")

    col1, col2, col3 = st.columns(3)
    col1.metric("Revenue", f"€{total_revenue}")
    col2.metric("Expenses", f"€{total_expenses}")
    col3.metric("Profit", f"€{profit}")

    st.bar_chart(pd.DataFrame({
        "Category": ["Revenue", "Expenses"],
        "Amount": [total_revenue, total_expenses]
    }).set_index("Category"))

# ===================== BOOKINGS =====================
elif page == "Bookings":

    st.header("Bookings")

    if df.empty:
        st.info("No bookings yet")
    else:
        st.dataframe(df, use_container_width=True, hide_index=True)

    st.subheader("Add New Booking")

    c1, c2, c3 = st.columns(3)

    with c1:
        guest = st.text_input("Guest Name")

    with c2:
        check_in = st.date_input("Check-in")

    with c3:
        check_out = st.date_input("Check-out")

    revenue = st.number_input("Revenue (€)")
    source = st.text_input("Source")

    if st.button("Save Booking"):
        if guest and source and revenue > 0:
            database.add_booking(
                guest, str(check_in), str(check_out), revenue, source
            )
            st.success("Booking saved!")
        else:
            st.error("Please fill all fields correctly")

# ===================== EXPENSES =====================
elif page == "Expenses":

    st.header("Expenses")

    exp_date = st.date_input("Date")
    category = st.text_input("Category")
    amount = st.number_input("Amount (€)")
    notes = st.text_input("Notes")

    if st.button("Save Expense"):
        if category and amount > 0:
            database.add_expense(str(exp_date), category, amount, notes)
            st.success("Expense saved!")
        else:
            st.error("Please fill all fields correctly")

# ===================== REPORTS =====================
elif page == "Reports":

    st.header("Monthly Report")

    current_month = pd.Timestamp.today().strftime("%Y-%m")

    month_revenue = df[df["month"] == current_month]["revenue"].sum() if not df.empty else 0
    month_expenses = exp_df[exp_df["month"] == current_month]["amount"].sum() if not exp_df.empty else 0
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
        st.info("High occupancy — consider increasing prices!")
    elif occupancy < 40:
        st.warning("Low occupancy — consider marketing or discounts.")
    else:
        st.success("Stable occupancy performance.")

    st.subheader("Forecast")

    if not df.empty:
        monthly = pd.DataFrame({
            "revenue": df.groupby("month")["revenue"].sum(),
            "expenses": exp_df.groupby("month")["amount"].sum()
        }).fillna(0)

        monthly["profit"] = monthly["revenue"] - monthly["expenses"]
        forecast_profit = monthly["profit"].mean()
    else:
        forecast_profit = 0

    st.metric("Next Month Forecast", f"€{round(forecast_profit, 2)}")
    st.info("Prediction is based on average monthly profit.")

    st.subheader("Pricing Engine")

    if not df.empty:

        total_nights = df["nights"].sum()
        base_price = df["revenue"].sum() / total_nights if total_nights > 0 else 0

        current_month_num = pd.Timestamp.today().month

        if current_month_num in [6, 7, 8, 12]:
            season_factor = 1.25
            season_label = "High Season"
        elif current_month_num in [4, 5, 9, 10]:
            season_factor = 1.0
            season_label = "Mid Season"
        else:
            season_factor = 0.85
            season_label = "Low Season"

        if occupancy > 80:
            demand_factor = 1.2
            demand_label = "High Demand"
        elif occupancy < 40:
            demand_factor = 0.85
            demand_label = "Low Demand"
        else:
            demand_factor = 1.0
            demand_label = "Normal Demand"

        suggested_price = base_price * season_factor * demand_factor

        st.write(f"Season: {season_label}")
        st.write(f"Demand: {demand_label}")
        st.write(f"Occupancy: {round(occupancy, 2)}%")

        st.metric("Dynamic Nightly Price", f"€{round(suggested_price, 2)}")

    else:
        st.warning("Not enough data for pricing engine.")