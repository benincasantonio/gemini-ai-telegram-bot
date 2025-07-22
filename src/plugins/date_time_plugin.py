from datetime import datetime

import pytz
from pydantic import BaseModel, Field
from pytz import timezone
from langchain_core.tools import StructuredTool
import ast


class DateTimeArgSchema(BaseModel):
    """Schema for the arguments of the get_date_time function. Should not be passed as dictionary, but as keyword arguments."""
    time_zone: str = Field(
        default="Europe/Rome",
        description="The timezone to use for the date and time. E.g. Europe/Rome, America/New_York, Asia/Tokyo.",
        examples=["Europe/Rome", "America/New_York", "Asia/Tokyo"],
        title="Time Zone",
    )

class DateTimePlugin:

    def __init__(self):
        self.__name: str = "get_date_time"
        self.__description: str = "A plugin that returns the current date and time. Pass the data as keyword arguments, not as a dictionary. The time zone can be specified using the 'time_zone' argument. If not specified, the default time zone is Europe/Rome. The time zone should be in the format 'Region/City', e.g. 'Europe/Rome', 'America/New_York', 'Asia/Tokyo'."

    def get_tool(self) -> StructuredTool:
        return StructuredTool(
            name=self.__name,
            description=self.__description,
            func=get_date_time,
            args_schema=DateTimeArgSchema,
            return_direct=True,
        )

def sanitize_time_zone(time_zone: str) -> str:
    """Since gemini sends the timezone with other characters, we need to sanitize it."""
    #sometimes it is returned as python dict in a string format, so we need to parse it
    try:
        parsed = ast.literal_eval(time_zone)
        return parsed.get('time_zone', 'Europe/Rome')
    except (ValueError, SyntaxError):
        raise ValueError(f"Invalid time zone format. For {time_zone}")




def get_date_time(time_zone: str) -> str:
    try:
        print("TimeZone:", time_zone)
        time_zone = sanitize_time_zone(time_zone)

        if not time_zone:
            time_zone = "Europe/Rome"



        return datetime.now(timezone(time_zone)).strftime("%Y-%m-%d %H:%M:%S")
    except Exception as e:
        print("Error in get_date_time:", e)
        return "Error in getting date and time. Please check the time zone format."
