from fastapi import FastAPI
from pydantic import BaseModel, validator
from datetime import date, timedelta
from typing import List
from io import open
import requests, yaml, datetime, os

os.getcwd()
key = yaml.safe_load(open(f"{os.getcwd()}/.key", "r"))
url = "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline"

class Location(BaseModel):
    locationid: str
    city: str
    state: str
    latitude: float
    longitude: float
    
class Day_Weather_Entry(BaseModel):
    locationid: str
    date: date
    temp_max: float
    temp_min: float
    temp_feel_max: float
    temp_feel_min: float
    precipitation: float
    precip_type: str
    snow: float
    snow_depth: float
    pressure: float
    dewpoint: float
    humidity: float
    skycover: float
    winddir: float
    windspeed: float
    windgust: float
    uv_index: float
    
class Month_Year(BaseModel):
    month: int
    year: int
    
    @validator('month')
    def validate_month(cls, v):
        if v > 0 and v < 13:
            return v
        else:
            raise ValueError('month must be between 1 and 12')
    
    @validator('year')
    def validate_year(cls, v):    
        if v > 1965 and v <= date.today().year:
            return v
        else:
            raise ValueError('year must be between 1970 and present')

class Month_Weather_Data(BaseModel):
    month_id: Month_Year
    weather_data: List[Day_Weather_Entry]
    
    # @validator('weather_data')
    # def weather_data_validate_obj(cls, v):
    #     if len(v) == 0:
    #         raise ValueError('List must not be enpty')
    #     if v[0] is Day_Weather_Data:
    #         return v

def call_month_data(month_id: Month_Year, location: Location):
    first_month_day = date(month_id.year, month_id.month, 1)
    next_month = first_month_day.replace(day=28) + timedelta(days=4)
    last_month_day = next_month-timedelta(days=next_month.day)
    
    api_call = f"{url}/{location.city},{location.state}/{first_month_day.strftime('%Y-%m-%d')}/{last_month_day.strftime('%Y-%m-%d')}?key={key}&include=days"

    return translate_month_data(month_id, requests.get(api_call, timeout=60).json(), location)

def get_day_data(day: date, location: Location):
    api_call = f"{url}/{location.city},{location.state}/{day.strftime('%Y-%m-%d')}?key={key}&include=days"

    return requests.get(api_call, timeout=60).json()

def translate_month_data(month_id, json_data, location: Location):
    trimmed_data = Month_Weather_Data(month_id=month_id, weather_data=[])
    
    for entry in json_data['days']:
        trimmed_data.weather_data.append(
            Day_Weather_Entry(
                locationid=location.locationid,
                date=entry['datetime'],
                temp_max=entry['tempmax'],
                temp_min=entry['tempmin'],
                temp_feel_max=entry['feelslikemax'],
                temp_feel_min=entry['feelslikemin'],
                precipitation=entry['precip'],
                precip_type=";".join([] if entry['preciptype'] == None else entry['preciptype']),
                snow=entry['snow'],
                snow_depth=entry['snowdepth'],
                pressure=entry['pressure'],
                dewpoint=entry['dew'],
                humidity=entry['humidity'],
                skycover=entry['cloudcover'],
                winddir=entry['winddir'],
                windspeed=entry['windspeed'],
                windgust=entry['windgust'],
                uv_index=entry['uvindex']
            )
        )
    
    return trimmed_data
    
app = FastAPI()

# @app.get("/today") #, response_model=Day_Weather_Data
# async def get_today_data():
#     return "test"

@app.get("/month") #, response_model=Month_Weather_Data
async def get_month_data(): #month_id: Month_Year
    return call_month_data(Month_Year(month=3, year=2023), Location(locationid=1, city='Minneapolis', state='MN', latitude=44.9778, longitude=93.2650))

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(app, host='127.0.0.1', port=8000)