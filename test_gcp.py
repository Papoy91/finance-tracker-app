import gspread
from oauth2client.service_account import ServiceAccountCredentials

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("personal_gcp_creds.json", scope)
client = gspread.authorize(creds)

sheet = client.open("finance_tracker").worksheet("data")
sheet.append_row(["Test Date", "Test Section", "Test Cat", "Test Sub", 123, "Test Note"])
print("✅ Data written successfully.")
