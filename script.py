import requests
from bs4 import BeautifulSoup
from dateutil import parser
import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

url = "https://www.aqi.in/dashboard/india/maharashtra/mumbai/mahape"
page = requests.get(url)
soup = BeautifulSoup(page.content, "html.parser")

td_list = soup.find_all("td", class_="rdp-day my p-[0.5rem_0.3rem] sm:min-w-[6.5rem]")

data_list = []

for td in td_list:
    aqi_val = td.find("div", class_="value").text.strip()
    if aqi_val != "-":
        date_val = td.get("aria-label")
        data_list.append([date_val, aqi_val])

for row in data_list:
    row[0] = parser.parse(row[0])

max_date_row = max(data_list, key=lambda x: x[0])  
max_date_str = max_date_row[0].strftime("%Y-%m-%d")
max_aqi_val = int(max_date_row[1])  
max_aqi_record = {"aqi_date": max_date_str, "aqi_val": max_aqi_val}

def insert_max_date_aqi(data):
    """
    Inserts only the row with the max date into supa_aqi_table.
    - `data`: A dictionary with 'aqi_data' and 'aqi_val'
    """
    response = supabase.table("supa_aqi_table").insert(data).execute()
    print("Response:", response)

    if response.data:  
        print(f"Successfully inserted: {data}")
    else:  
        print(f"Error inserting {data}: {response.error}")

insert_max_date_aqi(max_aqi_record)