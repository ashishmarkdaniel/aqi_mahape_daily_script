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

#fetch max date from scraped data
max_date_row = max(data_list, key=lambda x: x[0])  
max_date_scraped = max_date_row[0]

#fetch max available date in supa db
fetch_supa_db = supabase.table("supa_aqi_table") \
    .select("aqi_date") \
    .order("aqi_date", desc=True) \
    .limit(1) \
    .execute()
# max_date_supa = fetch_supa_db.data[0]['aqi_date']
print(fetch_supa_db)
filtered_data_list = [
    (date, aqi_value)
    for date, aqi_value in data_list
    if max_date_supa is None or (date > parser.parse(max_date_supa) and date <= max_date_scraped)
]

final_data_list = [{"aqi_date" : date.strftime("%Y-%m-%d"), "aqi_val" : aqi_val} for date, aqi_val in filtered_data_list]

def insert_data_aqi(data):
    """
    Inserts only the row with the max date into supa_aqi_table.
    - `data`: A dictionary with 'aqi_data' and 'aqi_val'
    """
    response_data, _ = supabase.table("supa_aqi_table").insert(data).execute()
    print("Response:", response_data)

    if response_data:  
        print(f"Successfully inserted: {data}")
    else:  
        print(f"Error inserting {data}")

# insert_data_aqi(final_data_list)