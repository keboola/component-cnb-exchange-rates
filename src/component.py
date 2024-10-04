'''
Template Component main class.

'''
import csv
import logging
from datetime import datetime, timedelta, date
import pytz
from typing import List, Dict

from keboola.component.base import ComponentBase
from keboola.component.exceptions import UserException

from client.client import CNBRatesClient, CNBRatesClientException
from configuration import OldConfiguration, NewConfiguration, ConfigurationException


class Component(ComponentBase):
    def __init__(self):
        super().__init__()
        self.client = None

    def run(self):
        logging.info('Running...')
        self.client = CNBRatesClient()
        today: date = datetime.now(pytz.timezone('Europe/Prague')).date()
        dates_list = []
        incr: bool = True
        out: str = ""

        if all(
            k in self.configuration.parameters for k in ('currencies', 'destination', 'date_settings')
        ):
            logging.info('New version of configuration detected. Running new logic...')

            params = NewConfiguration(**self.configuration.parameters)
            dates_list = self._run_with_new_config(params, today)
            incr = params.destination.incremental
            out = params.destination.file_name
            currencies = params.currencies.selected_currencies

            logging.info(f'Currency data: {currencies}')
            logging.info(f'{len(dates_list)} dates added')

            rates = self.client.get_rates(
                dates_list,
                today,
                params.date_settings.current_as_today,
                currencies
            )

            logging.info(f'{len(rates)} rates fetched')

        else:
            logging.info('Old version of configuration detected. Running old logic...')

            params = OldConfiguration(**self.configuration.parameters)
            dates_list, currencies = self._run_with_old_config(params, today)
            incr = params.incremental
            out = params.file_name

            logging.info(f'Currency data: {currencies}')
            logging.info(f'{len(dates_list)} dates added')

            rates = self.client.get_rates(
                dates_list,
                today,
                params.current_as_today,
                currencies
            )

            logging.info(f'{len(rates)} rates fetched')

        file_header = ['date', 'country', 'currency', 'amount', 'code', 'rate']

        table = self.create_out_table_definition(
            name=f"{out}.csv",
            incremental=incr,
            primary_key=['date', 'code']
        )

        if rates:
            with open(table.full_path, mode='wt', encoding='utf-8', newline='') as out_file:
                writer = csv.writer(out_file)
                writer.writerow(file_header)
                writer.writerows(rates)
        else:
            raise UserException("Data were not fetched!")

        # Save table manifest (output.csv.manifest) from the table definition
        self.write_manifest(table)

    def _run_with_new_config(self, params: NewConfiguration, today: date):
        dates_list = []
        date_action = self._get_dates_setters.get(params.date_settings.dates)

        if not date_action:
            raise UserException(f"No valid date action found for {params.date_settings.dates}")

        if date_action:
            if params.date_settings.dates == "Custom date range":
                try:
                    date_from: date = datetime.strptime(
                        str(params.date_settings.dependent_date_from), '%Y-%m-%d'
                    ).date()
                    date_to: date = datetime.strptime(
                        str(params.date_settings.dependent_date_to), '%Y-%m-%d'
                    ).date()
                    dates_list = date_action(dates_list, today, date_from, date_to)

                except ValueError:
                    raise UserException('Dates not specified correctly for custom date range!')
            else:
                dates_list = date_action(dates_list, today)

        return dates_list

    def _run_with_old_config(self, params: OldConfiguration, today: date):
        dates_list = []
        currencies = []
        date_action = self._get_dates_setters.get(params.dates)
        params_dict = params.model_dump()
        selected_currencies = {key: value for key, value in params_dict.items() if key.startswith("select_curr")}

        if not date_action:
            raise UserException(f"No valid date action found for {params.dates}")

        if params.currency == "Selected currencies":
            currencies = [attr[12:] for attr, value in selected_currencies.items() if value]

        else:
            currencies = [attr[12:] for attr in selected_currencies.keys()]

        logging.info(f"Params dates: {params.dates}")
        if date_action:
            if params.dates == "Custom date range":
                try:
                    date_from: date = datetime.strptime(str(params.dependent_date_from), '%Y-%m-%d').date()
                    date_to: date = datetime.strptime(str(params.dependent_date_to), '%Y-%m-%d').date()
                    dates_list = date_action(dates_list, today, date_from, date_to)
                except ValueError:
                    raise UserException('Dates not specified correctly for custom date range!')
            else:
                dates_list = date_action(dates_list, today)

        return dates_list, currencies

    # Date setters
    @staticmethod
    def _set_date_range(dates_list: List, day: date, days: int) -> List:
        if days <= 0:
            logging.error(f"Invalid number of days: {days}. Must be positive.")
            raise UserException(f"Invalid number of days: {days}.")

        for i in range(days):
            date_to_add = day - timedelta(days=i)
            dates_list.append(date_to_add)
            logging.info(f"Added date: {date_to_add}")
        return dates_list

    def _set_today(self, dates_list: List, today: date) -> List:
        logging.info(f"Setting today: {today}")
        data = self._set_date_range(dates_list, today, 1)
        return data

    def _set_today_and_yesterday(self, dates_list: List, today: date) -> List:
        logging.info(f"Setting today ({today}) and yesterday.")
        data = self._set_date_range(dates_list, today, 2)
        logging.info(f"Dates list after setting today and yesterday: {data}")
        return data

    def _set_week(self, dates_list: List, today: date) -> List:
        logging.info(f"Setting week from {today}")
        data = self._set_date_range(dates_list, today, 7)
        return data

    @staticmethod
    def _set_custom_date_range(
        dates_list: List[None],
        today: date,
        date_from: date,
        date_to: date
    ) -> List:
        logging.info(f"Setting custom date range from {date_from} to {date_to} (today is {today})")

        if date_from >= date_to:
            raise UserException('\"Date from\" is higher or equal to date to!')

        if date_from > today:
            raise UserException('\"Date from\" is in the future!')

        if date_to > today:
            logging.warning(
                'For "Date to" you selected a day in the future! Therefore, '
                '"Date to" was set to today\'s day.'
            )
            date_to = today

        for i in range((date_to - date_from).days + 1):
            date_to_add = date_from + timedelta(days=i)
            dates_list.append(date_to_add)
            logging.info(f"Added date: {date_to_add}")

        return dates_list

    # Date setters dictionary
    # Keys represents values of "dates" option in the config.json
    @property
    def _get_dates_setters(self) -> Dict[str, callable]:

        setters = {
            'Current day (currently declared rates)': self._set_today,
            'Current day and yesterday': self._set_today_and_yesterday,
            'Week': self._set_week,
            'Custom date range': self._set_custom_date_range
        }
        return setters


if __name__ == "__main__":
    try:
        comp = Component()
        # this triggers the run method by default and is controlled by the configuration.action parameter
        comp.execute_action()

    except (CNBRatesClientException, ConfigurationException) as exc:
        raise UserException(exc)

    except UserException as exc:
        logging.exception(exc)
        exit(1)

    except Exception as exc:
        logging.exception(exc)
        exit(2)
