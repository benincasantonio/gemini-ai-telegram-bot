from datetime import datetime
from pydantic import BaseModel, Field
from pytz import timezone
from langchain_core.tools import StructuredTool


class DateTimeArgSchema(BaseModel):
    time_zone: str = Field(
        default="Europe/Rome",
        description="The timezone to use for the date and time. E.g. Europe/Rome, America/New_York, Asia/Tokyo.",
        examples=["Europe/Rome", "America/New_York", "Asia/Tokyo"]
    )

class DateTimePlugin:

    def __init__(self):
        self.__name: str = "get_date_time"
        self.__description: str = "A plugin that returns the current date and time."

    def get_tool(self) -> StructuredTool:
        return StructuredTool(
            name=self.__name,
            description=self.__description,
            func=get_date_time,
            return_direct=True,
        )



def get_date_time(time_zone: str = "Europe/Rome") -> str:
    print("TimeZone:", time_zone)
    return datetime.now(timezone(time_zone)).strftime("%Y-%m-%d %H:%M:%S")
