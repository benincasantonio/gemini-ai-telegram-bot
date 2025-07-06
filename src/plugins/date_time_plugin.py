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
            func=self.get_date_time,
            args_schema=DateTimeArgSchema,
            return_direct=True,
        )

    @staticmethod
    def get_date_time(time_zone="Europe/Rome") -> str:
        return datetime.now(timezone(time_zone)).strftime("%Y-%m-%d %H:%M:%S")
