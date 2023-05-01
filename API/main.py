from fastapi import FastAPI
from pydantic import BaseModel
from datetime import date, timedelta
from typing import List
from io import open
import requests, yaml, datetime

# app = FastAPI()

key = yaml.safe_load(open("../.key", "r"))
url = "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline"

# class Location(BaseModel):
#     locationid: str
#     locationname: str
#     state: str
#     zip: str
#     latitude: float
#     longitude: float
    
# class Day_Weather_Entry(BaseModel):
#     locationid: str
#     temp: float
#     temp_max: float
#     temp_min: float
#     temp_feel_max: float
#     temp_feel_min: float
#     precipitation: float
#     precip_type: str
#     snow_depth: float
#     pressure: float
#     dewpoint: float
#     humidity: float
#     skycover: float
#     windspeed: float
#     windspeedmax: float
#     uv_index: float
    
# class Day_Weather_Data(BaseModel):
#     date: date
#     entries: List[Day_Weather_Entry]

class Month_Year(BaseModel):
    month: int
    year: int
    
# class Month_Weather_Data(BaseModel):
#     month_id: Month_Year
#     weather_data = List[Day_Weather_Data]

def get_month_data(month_id: Month_Year, zip=55105):
    first_month_day = date(month_id.year, month_id.month, 1)
    next_month = first_month_day.replace(day=28) + timedelta(days=4)
    last_month_day = next_month-timedelta(days=next_month.day)
    
    api_call = f"{url}/{zip}/{first_month_day.strftime('%Y-%m-%d')}/{last_month_day.strftime('%Y-%m-%d')}?key={key}&include=days"

    return requests.get(api_call, timeout=60).json()

def get_day_data(day: date, zip=55105):
    api_call = f"{url}/{zip}/{day.strftime('%Y-%m-%d')}?key={key}&include=days"

    return requests.get(api_call, timeout=60).json()
    
# @app.get("/today") #, response_model=Day_Weather_Data
# async def get_today_data():
#     return "test"

# @app.get("/month") #, response_model=Month_Weather_Data
# async def get_month_data(month_id: Month_Year):
#     pass

print(get_month_data(Month_Year(month=3, year=2023)))