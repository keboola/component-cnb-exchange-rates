import logging
import requests
import time

from datetime import datetime
from typing import List

from backoff import on_exception, expo

from keboola.http_client import HttpClient


class CNBRatesClientException(requests.exceptions.Exception):
    pass


class CNBRatesClient(HttpClient):
    base_url = 'https://www.cnb.cz/cs/financni-trhy/devizovy-trh/kurzy-devizoveho-trhu/kurzy-devizoveho-trhu/denni_kurz.txt' # noqa E501

    def __init__(self):
        super().__init__(base_url=self.base_url)

    # Parsers
    @staticmethod
    def _parse_response(response: requests.Response, temp_date: str, currency: List[str]) -> None:
        data = []
        for line in response.text.split('\n')[2:]:
            line_split = line.split('|')
            if len(line_split) == 5 and (currency is None or line_split[3] in currency):
                data.append([temp_date] + line_split[:4] + [line_split[4].replace(',', '.')])

    @staticmethod
    def _parse_date(response: requests.Response, date: datetime, today: datetime, curr_flag: bool) -> str:
        if date == today and not curr_flag:
            parse_date = response.text[:response.text.find('#')].strip().split('.')
            return f"{parse_date[2]}-{parse_date[1]}-{parse_date[0]}"
        return date.strftime('%Y-%m-%d')

    # Main API call method
    @on_exception(
            expo,
            (
                CNBRatesClientException,
                requests.exceptions.RequestException,
                requests.exceptions.HTTPError,
                requests.exceptions.ConnectionError,
                requests.exceptions.Timeout
            ),
            max_tries=10
        )
    def get_rates(self, dates: List[datetime], today: datetime, curr_flag: bool, currency: List[str]) -> List[str]:
        for d in dates:
            date_param = d.strftime('%d.%m.%Y')
            try:
                raw_response = self.get_raw(url=self.base_url + '?date=' + date_param, timeout=15)
                raw_response.raise_for_status()

            except Exception as err:
                logging.info('Request was not successful. Making another try.')
                raise CNBRatesClientException(f'Request error occurred: {err}')

            if 200 <= raw_response.status_code <= 400:
                temp_date = self._parse_date(raw_response, d, today, curr_flag)
                data = self._parse_response(raw_response, temp_date, currency)
                break

            else:
                logging.info('Request was not successful. Making another try.')
                time.sleep(1)

        return data
