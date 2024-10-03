import logging

from typing import Optional
from datetime import date

from pydantic import BaseModel, Field, ValidationError


class ConfigurationException(Exception):
    pass


class Configuration(BaseModel):
    file_name: str = Field(
        title="Table name",
        description="Only alphanumeric characters, dash and underscores are allowed."
    )
    dates: str = Field(
        title="Range of dates",
        default="Current day and yesterday",
        enum=[
            "Current day (currently declared rates)",
            "Current day and yesterday",
            "Week",
            "Custom date range"
        ]
    )
    dependent_date_from: Optional[date] = Field(None, title="Date from")
    dependent_date_to: Optional[date] = Field(None, title="Date to")
    current_as_today: bool = Field(title="Current rates as today's rates", default=True)
    incremental: bool = Field(title="Incremental load", default=True)
    dafault_timezone: str = Field(title="Default timezone", default="Europe/Prague")
    debug: bool = Field(title="Debug mode", default=False)
    selected_currencies: Optional[list] = Field(None)

    def __init__(self, **data):
        try:
            super().__init__(**data)
        except ValidationError as e:
            error_messages = [f"{err['loc'][0]}: {err['msg']}" for err in e.errors()]
            raise ConfigurationException(f"Validation Error: {', '.join(error_messages)}")

        if self.debug:
            logging.debug("Component will run in Debug mode")
