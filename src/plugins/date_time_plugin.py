from datetime import datetime
from pydantic import BaseModel, Field
from pytz import timezone
from langchain_core.tools import StructuredTool


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
            func=get_date_time_tool,
            args_schema=DateTimeArgSchema,
            return_direct=True,
        )

def get_date_time_tool(**kwargs) -> str:
    """
    Wrapper function to call get_date_time with keyword arguments.
    This is necessary to match the StructuredTool signature.
    """
    if 'time_zone' in kwargs and isinstance(kwargs['time_zone'], str):
        time_zone = kwargs['time_zone']
    elif 'time_zone' in kwargs and isinstance(kwargs['time_zone'], list):
        time_zone = kwargs['time_zone'][0]
    elif 'time_zone' in kwargs and isinstance(kwargs['time_zone'], dict):
        time_zone = kwargs['time_zone'].get('time_zone', "Europe/Rome")
    else:
        time_zone = "Europe/Rome"

    print("Calling get_date_time with time_zone:", time_zone)
    return get_date_time(time_zone)

def get_date_time(time_zone = "Europe/Rome") -> str:
    try:
        print("TimeZone:", time_zone)
        return datetime.now(timezone(time_zone)).strftime("%Y-%m-%d %H:%M:%S")
    except Exception as e:
        print("Error in get_date_time:", e)
        return "Error in getting date and time. Please check the time zone format."
