import logging

from typing import Optional
from datetime import date

from pydantic import BaseModel, Field, ValidationError


class ConfigurationException(Exception):
    pass


class DestinationConfig(BaseModel):
    file_name: str = Field(
        title="Table name",
        description="Only alphanumeric characters, dash and underscores are allowed."
    )
    incremental: bool = Field(title="Incremental load", default=True)


class DateSettingsConfig(BaseModel):
    dates: str = Field(
        title="Range of dates",
        default="Current day and yesterday",
    )
    dependent_date_from: Optional[date] = Field(None, title="Date from")
    dependent_date_to: Optional[date] = Field(None, title="Date to")
    current_as_today: bool = Field(title="Current rates as today's rates", default=True)
    default_timezone: str = Field(title="Default timezone", default="Europe/Prague")


class CurrenciesConfig(BaseModel):
    selected_currencies: Optional[list] = Field(None)


# Main classes
# Automatically set in component class run method
class NewConfiguration(BaseModel):
    debug: bool = Field(title="Debug mode", default=False)
    currencies: CurrenciesConfig
    destination: DestinationConfig
    date_settings: DateSettingsConfig

    def __init__(self, **data):
        try:
            super().__init__(**data)
        except ValidationError as e:
            error_messages = [f"{err['loc'][0]}: {err['msg']}" for err in e.errors()]
            raise ConfigurationException(f"Validation Error: {', '.join(error_messages)}")

        if self.debug:
            logging.debug("Component will run in Debug mode")


# Old configuration class for backward compatibility
class OldConfiguration(BaseModel):
    file_name: str = Field(
        description="Only alphanumeric characters, dash and underscores are allowed. Your data will be extracted to in.c-cnb-extractor.{your table name}" # noqa E501
    )
    incremental: bool = Field(
        description="By checking this box newly extracted data will be loaded incrementally to the Storage." # noqa E501
    )
    dates: str = Field(
        description="Range of dates",
        default="Current day and yesterday",
        enum=[
            "Current day (currently declared rates)",
            "Current day and yesterday",
            "Week",
            "Custom date range"
        ]
    )
    dependent_date_from: Optional[str] = Field(None, description="Date from (format: date)")
    dependent_date_to: Optional[str] = Field(None, description="Date to (format: date)")
    current_as_today: bool = Field(True, description="Current rates as today's rates")
    currency: str = Field(description="Select currency", default="All", enum=[
        "All",
        "Selected currencies"
    ])
    select_curr_AUD: Optional[bool] = Field(None, description="Austrálie (dolar)")
    select_curr_BRL: Optional[bool] = Field(None, description="Brazílie (real)")
    select_curr_BGN: Optional[bool] = Field(None, description="Bulharsko (lev)")
    select_curr_CNY: Optional[bool] = Field(None, description="Čína (žen-min-pi)")
    select_curr_DKK: Optional[bool] = Field(None, description="Dánsko (koruna)")
    select_curr_EUR: Optional[bool] = Field(None, description="EMU (euro)")
    select_curr_PHP: Optional[bool] = Field(None, description="Filipíny (peso)")
    select_curr_HKD: Optional[bool] = Field(None, description="Hongkong (dolar)")
    select_curr_HRK: Optional[bool] = Field(None, description="Chorvatsko (kuna)")
    select_curr_INR: Optional[bool] = Field(None, description="Indie (rupie)")
    select_curr_IDR: Optional[bool] = Field(None, description="Indonesie (rupie)")
    select_curr_ISK: Optional[bool] = Field(None, description="Island (koruna)")
    select_curr_ILS: Optional[bool] = Field(None, description="Izrael (nový šekel)")
    select_curr_JPY: Optional[bool] = Field(None, description="Japonsko (jen)")
    select_curr_ZAR: Optional[bool] = Field(None, description="Jižní Afrika (rand)")
    select_curr_CAD: Optional[bool] = Field(None, description="Kanada (dolar)")
    select_curr_KRW: Optional[bool] = Field(None, description="Korejská republika (won)")
    select_curr_HUF: Optional[bool] = Field(None, description="Maďarsko (forint)")
    select_curr_MYR: Optional[bool] = Field(None, description="Malajsie (ringgit)")
    select_curr_MXN: Optional[bool] = Field(None, description="Mexiko (peso)")
    select_curr_XDR: Optional[bool] = Field(None, description="MMF (ZPČ)")
    select_curr_NOK: Optional[bool] = Field(None, description="Norsko (koruna)")
    select_curr_NZD: Optional[bool] = Field(None, description="Nový Zéland (dolar)")
    select_curr_PLN: Optional[bool] = Field(None, description="Polsko (zlotý)")
    select_curr_RON: Optional[bool] = Field(None, description="Rumunsko (leu)")
    select_curr_SGD: Optional[bool] = Field(None, description="Singapur (dolar)")
    select_curr_SEK: Optional[bool] = Field(None, description="Švédsko (koruna)")
    select_curr_CHF: Optional[bool] = Field(None, description="Švýcarsko (frank)")
    select_curr_THB: Optional[bool] = Field(None, description="Thajsko (baht)")
    select_curr_TRY: Optional[bool] = Field(None, description="Turecko (lira)")
    select_curr_USD: Optional[bool] = Field(None, description="USA (dolar)")
    select_curr_GBP: Optional[bool] = Field(None, description="Velká Británie (libra)")
    default_timezone: Optional[str] = Field(
        description="Default timezone",
        default="Europe/Prague"
    )
    debug: bool = Field(False, description="Debug mode")

    def __init__(self, **data):
        try:
            super().__init__(**data)
        except ValidationError as e:
            error_messages = [f"{err['loc'][0]}: {err['msg']}" for err in e.errors()]
            raise ConfigurationException(f"Validation Error: {', '.join(error_messages)}")

        if self.debug:
            logging.debug("Component will run in Debug mode")
