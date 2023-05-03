from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, validator, root_validator
from datetime import date, timedelta
from typing import List
from io import open
import requests, yaml, os

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
        
    @root_validator
    def month_is_not_future(cls, values):
        if values['year'] == date.today().year:
            if values['month'] <= date.today().month:
                return values
            else:
                raise ValueError('Time period must not be in the future')
        elif values['year'] < date.today().year:
            return values
        else:
            raise ValueError('Time period must not be in the future')

class Month_Weather_Data(BaseModel):
    month_id: Month_Year
    weather_data: List[Day_Weather_Entry]


def none_check(value, default_value):
    if value == None:
        return default_value
    else:
        return value

def get_day_data(day: date, location: Location):
    api_call = f"{url}/{location.city},{location.state}/{day.strftime('%Y-%m-%d')}?key={key}&include=days"

    day_entry = requests.get(api_call, timeout=60).json()['days'][0]
    
    return Day_Weather_Entry(
        locationid=location.locationid,
                date=day_entry['datetime'],
                temp_max=day_entry['tempmax'],
                temp_min=day_entry['tempmin'],
                temp_feel_max=day_entry['feelslikemax'],
                temp_feel_min=day_entry['feelslikemin'],
                precipitation=day_entry['precip'],
                precip_type=";".join(none_check(day_entry['preciptype'], [])),
                snow=none_check(day_entry['snow'], 0.0),
                snow_depth=none_check(day_entry['snowdepth'], 0.0),
                pressure=day_entry['pressure'],
                dewpoint=day_entry['dew'],
                humidity=day_entry['humidity'],
                skycover=day_entry['cloudcover'],
                winddir=day_entry['winddir'],
                windspeed=day_entry['windspeed'],
                windgust=none_check(day_entry['windgust'], 0.0),
                uv_index=day_entry['uvindex']
    )
    
def call_month_data(month_id: Month_Year, location: Location):
    first_month_day = date(month_id.year, month_id.month, 1)
    next_month = first_month_day.replace(day=28) + timedelta(days=4)
    last_month_day = next_month-timedelta(days=next_month.day)
    
    api_call = f"{url}/{location.city},{location.state}/{first_month_day.strftime('%Y-%m-%d')}/{last_month_day.strftime('%Y-%m-%d')}?key={key}&include=days"

    return translate_month_data(month_id, requests.get(api_call, timeout=60).json(), location)

def translate_month_data(month_id, json_resp, location: Location):
    trimmed_data = Month_Weather_Data(month_id=month_id, weather_data=[])
    
    for entry in json_resp['days']:
        trimmed_data.weather_data.append(
            Day_Weather_Entry(
                locationid=location.locationid,
                date=entry['datetime'],
                temp_max=entry['tempmax'],
                temp_min=entry['tempmin'],
                temp_feel_max=entry['feelslikemax'],
                temp_feel_min=entry['feelslikemin'],
                precipitation=entry['precip'],
                precip_type=";".join(none_check(entry['preciptype'], [])),
                snow=none_check(entry['snow'], 0.0),
                snow_depth=none_check(entry['snowdepth'], 0.0),
                pressure=entry['pressure'],
                dewpoint=entry['dew'],
                humidity=entry['humidity'],
                skycover=entry['cloudcover'],
                winddir=entry['winddir'],
                windspeed=entry['windspeed'],
                windgust=none_check(entry['windgust'], 0.0),
                uv_index=entry['uvindex']
            )
        )
    
    return trimmed_data
    
app = FastAPI()

@app.get("/yesterday", response_model=Day_Weather_Entry)
async def get_yesterday_data():
    return get_day_data(date.today()-timedelta(days=1), Location(locationid=1, city='Minneapolis', state='MN', latitude=44.9778, longitude=93.2650))

@app.get("/monthly/{year}/{month}", response_model=Month_Weather_Data) #, response_model=Month_Weather_Data
async def get_month_data(year: int, month: int): #month_id: Month_Year
    try:
        month_id = Month_Year(year=year, month=month)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    return call_month_data(month_id, Location(locationid=1, city='Minneapolis', state='MN', latitude=44.9778, longitude=93.2650))

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(app, host='127.0.0.1', port=8000)