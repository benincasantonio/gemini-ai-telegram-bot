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

def get_date_time_tool(*args, **kwargs) -> str:
    """
    Wrapper function to call get_date_time with keyword arguments.
    This is necessary to match the StructuredTool signature.
    """
    print("ARGS:", args)
    print("KWARGS:", kwargs)

    # Default fallback
    time_zone = "Europe/Rome"

    # Se è passato come argomento posizionale
    if args and isinstance(args[0], str):
        time_zone = args[0]
    # Se è passato come kwargs
    elif 'time_zone' in kwargs:
        tz = kwargs['time_zone']
        if isinstance(tz, str):
            time_zone = tz
        elif isinstance(tz, list):
            time_zone = tz[0]
        elif isinstance(tz, dict):
            time_zone = tz.get('time_zone', time_zone)

    print("Final timezone:", time_zone)
    return datetime.now(timezone(time_zone)).strftime("%Y-%m-%d %H:%M:%S")

def get_date_time(time_zone = "Europe/Rome") -> str:
    try:
        print("TimeZone:", time_zone)
        return datetime.now(timezone(time_zone)).strftime("%Y-%m-%d %H:%M:%S")
    except Exception as e:
        print("Error in get_date_time:", e)
        return "Error in getting date and time. Please check the time zone format."
