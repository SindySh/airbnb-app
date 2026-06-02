from supabase import create_client

SUPABASE_URL = "https://zodooclczfytefkmwrxx.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InpvZG9vY2xjemZ5dGVma213cnh4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODA0MTE3ODUsImV4cCI6MjA5NTk4Nzc4NX0.skTA6-nEym6jictPi1r_AobrMR3vR6AVMQlik00bpMw"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)