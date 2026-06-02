from supabase_client import supabase

def add_booking(guest_name, check_in, check_out, revenue, booking_source):
    supabase.table("bookings").insert({
        "guest_name": guest_name,
        "check_in": check_in,
        "check_out": check_out,
        "revenue": revenue,
        "booking_source": booking_source
    }).execute()


def get_bookings():
    res = supabase.table("bookings").select("*").execute()
    return res.data


def add_expense(date, category, amount, notes):
    supabase.table("expenses").insert({
        "date": date,
        "category": category,
        "amount": amount,
        "notes": notes
    }).execute()


def get_expenses():
    res = supabase.table("expenses").select("*").execute()
    return res.data