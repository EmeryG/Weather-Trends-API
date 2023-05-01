from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

app = FastAPI()

class Location(BaseModel):
    locationid: str
    locationname: str
    state: str
    data_start: str
    data_end: str
    
class Day_Weather_Entry(BaseModel):
    locationid: str
    high_temp: float
    low_temp: float
    precipitation: float
    snow: float
    humidity: float
    sunshine: float
    wind: float
    
class Day_Weather_Data(BaseModel):
    date: str
    entries: List[Day_Weather_Entry]

class Month(BaseModel):
    month: str
    year: int
    
class Month_Weather_Data(BaseModel):
    month: Month
    weather_data = List[Day_Weather_Data]

@app.get("/today", response_model=Day_Weather_Data)
async def main():
    return "test"

@app.get("/month", response_model=Month_Weather_Data)
async def get_month_data(month: Month):
    pass