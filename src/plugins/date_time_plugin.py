from datetime import datetime
from pydantic import BaseModel, Field
from pytz import timezone
from langchain_core.tools import Tool
from langchain import hub


class DateTimeArgSchema(BaseModel):
    time_zone: str = Field(
        default="Europe/Rome",
        description="The timezone to use for the date and time.",
        examples=["Europe/Rome", "America/New_York", "Asia/Tokyo"]
    )

class DateTimePlugin:

    def __init__(self):
        self.__name: str = "get_date_time"
        self.__description: str = "A plugin that returns the current date and time."

    def get_tool(self) -> Tool:
        return Tool(
            name=self.__name,
            description=self.__description,
            func=self.get_date_time,
        )

    @staticmethod
    def get_date_time(time_zone="Europe/Rome") -> str:
        return datetime.now(timezone(time_zone)).strftime("%Y-%m-%d %H:%M:%S")
