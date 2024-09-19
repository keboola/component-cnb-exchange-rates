'''
Template Component main class.

'''
import csv
import logging
from datetime import datetime, timedelta
import pytz
import time
import requests
from typing import List, Dict

from keboola.component.base import ComponentBase
from keboola.component.exceptions import UserException

# configuration variables
KEY_API_TOKEN = '#api_token'
KEY_PRINT_HELLO = 'print_hello'

# cnb endpoint and request tries variables
REQUEST_TRIES = 10
TARGET = 'https://www.cnb.cz/cs/financni-trhy/devizovy-trh/kurzy-devizoveho-trhu/kurzy-devizoveho-trhu/denni_kurz.txt'

# list of mandatory parameters => if some is missing,
# component will fail with readable message on initialization.
REQUIRED_PARAMETERS = [KEY_PRINT_HELLO]
REQUIRED_IMAGE_PARS = []


class Component(ComponentBase):
    def __init__(self):
        super().__init__()

    # Main API call method
    def _call_cnb_api(
            self,
            target: str,
            dates: List[datetime],
            today: datetime,
            curr_flag: bool,
            currency: List[str]
    ) -> List[str]:

        data = []
        for d in dates:
            date_param = d.strftime('%d.%m.%Y')
            for request_try in range(REQUEST_TRIES):
                try:
                    r = requests.get(url=target + '?date=' + date_param, timeout=15)
                    r.raise_for_status()
                except (
                    requests.exceptions.RequestException,
                    requests.exceptions.HTTPError,
                    requests.exceptions.ConnectionError,
                    requests.exceptions.Timeout
                ) as err:
                    if request_try == REQUEST_TRIES - 1:
                        raise UserException(f'Request error occurred: {err}')
                    logging.info('Request was not successful. Making another try.')
                    continue

                if 200 <= r.status_code <= 400:
                    temp_date = self._parse_date(r, d, today, curr_flag)
                    self._parse_response(data, r, temp_date, currency)
                    break
                else:
                    logging.info('Request was not successful. Making another try.')
                    time.sleep(1)
        return data

    # Parsers
    @staticmethod
    def _parse_response(
        data: List,
        response: requests.Response,
        temp_date: str,
        currency: List[str]
    ) -> None:
        for line in response.text.split('\n')[2:]:
            line_split = line.split('|')
            if len(line_split) == 5 and (currency is None or line_split[3] in currency):
                data.append([temp_date] + line_split[:4] + [line_split[4].replace(',', '.')])

    @staticmethod
    def _parse_date(response, date: datetime, today: datetime, curr_flag: bool) -> str:
        if date == today and not curr_flag:
            parse_date = response.text[:response.text.find('#')].strip().split('.')
            return f"{parse_date[2]}-{parse_date[1]}-{parse_date[0]}"
        return date.strftime('%Y-%m-%d')

    # Date range setters
    @staticmethod
    def _set_date_range(dates_list: List, day: datetime, days: int) -> None:
        for i in range(days):
            dates_list.append(day - timedelta(days=i))

    def _set_today(self, dates_list: List, today: datetime) -> None:
        self._set_date_range(dates_list, today, 1)

    def _set_today_and_yesterday(self, dates_list: List, today: datetime) -> None:
        self._set_date_range(dates_list, today, 2)

    def _set_week(self, dates_list: List, today: datetime) -> None:
        self._set_date_range(dates_list, today, 7)

    @staticmethod
    def _set_custom_date_range(
        dates_list: list,
        today: datetime,
        date_from: datetime,
        date_to: datetime
    ) -> None:

        if date_from >= date_to:
            raise UserException('\"Date from\" is higher or equal to date to!')

        if date_from > today:
            raise UserException('\"Date from\" is in the future!')

        for i in range((min(date_to, today) - date_from).days + 1):
            dates_list.append(date_from + timedelta(days=i))

        if date_to > today:
            logging.warning(
                'For "Date to" you selected a day in the future! Therefore, '
                '"Date to" was set to today\'s day.'
            )

    # Date setters dictionary
    # Keys represents values of "dates" option in the config.json
    @property
    def _get_dates_setters(self) -> Dict[str, callable]:
        return {
            'Current day (currently declared rates)': self._set_today,
            'Current day and yesterday': self._set_today_and_yesterday,
            'Week': self._set_week,
            'Custom date range': self._set_custom_date_range
        }

    def run(self):
        logging.info('Running...')

        start_time = time.time()
        # config.json parameters
        params = self.configuration.parameters

        out_table_name = params.get('file_name')
        if not out_table_name:
            raise UserException('You have to specify a name for the output table!')

        out_storage_path = 'in.c-cnb-extractor.' + out_table_name
        out_incremental = params['incremental']

        # output file definition - use if output mapping is enabled
        # kbc_out_path = self.configuration.config_data["storage"]["output"]["tables"][0]["destination"]
        # out_file_name = self.configuration.config_data["storage"]["output"]["tables"][0]["source"]
        # out_incremental = self.configuration.config_data["storage"]["output"]["tables"][0]["incremental"]

        dates_list = []
        today = datetime.now(pytz.timezone('Europe/Prague')).date()

        date_action = self._get_dates_setters.get(params['dates'])
        if date_action:
            if params['dates'] == "Custom date range":
                try:
                    date_from = datetime.strptime(params['dependent_date_from'], '%Y-%m-%d').date()
                    date_to = datetime.strptime(params['dependent_date_to'], '%Y-%m-%d').date()
                    date_action(dates_list, today, date_from, date_to)
                except ValueError:
                    raise UserException('Dates not specified correctly for custom date range!')
            else:
                date_action(dates_list, today)

        selected_currency = None if params['currency'] == 'All' else [
            p.split('_')[2] for p in params if p.startswith("select_curr") and params[p]
        ]

        if selected_currency == []:
            raise UserException('No currency was selected!')

        file_header = ['date', 'country', 'currency', 'amount', 'code', 'rate']

        rates = self._call_cnb_api(
            TARGET,
            dates_list,
            today,
            params['current_as_today'],
            selected_currency
        )

        table = self.create_out_table_definition(
            name='output.csv',
            destination=out_storage_path,
            incremental=out_incremental,
            primary_key=['date', 'code']
        )

        if rates:
            with open(table.full_path, mode='wt', encoding='utf-8', newline='') as out_file:
                writer = csv.writer(out_file)
                writer.writerow(file_header)
                writer.writerows(rates)
        else:
            raise UserException("Data were not fetched!")

        # Save table manifest (output.csv.manifest) from the tabledefinition
        self.write_manifest(table)

        # Write new state - will be available next run
        self.write_state_file({"some_state_parameter": "value"})
        end_time = time.time()
        logging.info(f'Execution time: {end_time - start_time} seconds')


if __name__ == "__main__":
    try:
        comp = Component()
        # this triggers the run method by default and is controlled by the configuration.action parameter
        comp.execute_action()
    except UserException as exc:
        logging.exception(exc)
        exit(1)
    except Exception as exc:
        logging.exception(exc)
        exit(2)
