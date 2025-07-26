import os
from dotenv import load_dotenv

load_dotenv()

email=os.getenv("EMAIL")
password=os.getenv("PASSWORD")
sheet=os.getenv("SPREAD_SHEET_ID")
print(email,password,sheet)
print(type(email))
