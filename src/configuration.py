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
    currency: str = Field(title="Select currency", default="All", enum=["All", "Selected currencies"])
    select_curr_AUD: Optional[bool] = Field(None, title="Austrálie (dolar)")
    select_curr_BRL: Optional[bool] = Field(None, title="Brazílie (real)")
    select_curr_BGN: Optional[bool] = Field(None, title="Bulharsko (lev)")
    select_curr_CNY: Optional[bool] = Field(None, title="Čína (žen-min-pi)")
    select_curr_DKK: Optional[bool] = Field(None, title="Dánsko (koruna)")
    select_curr_EUR: Optional[bool] = Field(None, title="EMU (euro)")
    select_curr_PHP: Optional[bool] = Field(None, title="Filipíny (peso)")
    select_curr_HKD: Optional[bool] = Field(None, title="Hongkong (dolar)")
    select_curr_HRK: Optional[bool] = Field(None, title="Chorvatsko (kuna)")
    select_curr_INR: Optional[bool] = Field(None, title="Indie (rupie)")
    select_curr_IDR: Optional[bool] = Field(None, title="Indonesie (rupie)")
    select_curr_ISK: Optional[bool] = Field(None, title="Island (koruna)")
    select_curr_ILS: Optional[bool] = Field(None, title="Izrael (nový šekel)")
    select_curr_JPY: Optional[bool] = Field(None, title="Japonsko (jen)")
    select_curr_ZAR: Optional[bool] = Field(None, title="Jižní Afrika (rand)")
    select_curr_CAD: Optional[bool] = Field(None, title="Kanada (dolar)")
    select_curr_KRW: Optional[bool] = Field(None, title="Korejská republika (won)")
    select_curr_HUF: Optional[bool] = Field(None, title="Maďarsko (forint)")
    select_curr_MYR: Optional[bool] = Field(None, title="Malajsie (ringgit)")
    select_curr_MXN: Optional[bool] = Field(None, title="Mexiko (peso)")
    select_curr_XDR: Optional[bool] = Field(None, title="MMF (ZPČ)")
    select_curr_NOK: Optional[bool] = Field(None, title="Norsko (koruna)")
    select_curr_NZD: Optional[bool] = Field(None, title="Nový Zéland (dolar)")
    select_curr_PLN: Optional[bool] = Field(None, title="Polsko (zlotý)")
    select_curr_RON: Optional[bool] = Field(None, title="Rumunsko (leu)")
    select_curr_SGD: Optional[bool] = Field(None, title="Singapur (dolar)")
    select_curr_SEK: Optional[bool] = Field(None, title="Švédsko (koruna)")
    select_curr_CHF: Optional[bool] = Field(None, title="Švýcarsko (frank)")
    select_curr_THB: Optional[bool] = Field(None, title="Thajsko (baht)")
    select_curr_TRY: Optional[bool] = Field(None, title="Turecko (lira)")
    select_curr_USD: Optional[bool] = Field(None, title="USA (dolar)")
    select_curr_GBP: Optional[bool] = Field(None, title="Velká Británie (libra)")
    dafault_timezone: str = Field(title="Default timezone", default="Europe/Prague")
    debug: bool = Field(title="Debug mode", default=False)

    def __init__(self, **data):
        try:
            super().__init__(**data)
        except ValidationError as e:
            error_messages = [f"{err['loc'][0]}: {err['msg']}" for err in e.errors()]
            raise ConfigurationException(f"Validation Error: {', '.join(error_messages)}")

        if self.debug:
            logging.debug("Component will run in Debug mode")
