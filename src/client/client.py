from datetime import datetime, date
from typing import List

from backoff import on_exception, expo
from requests import Response

from keboola.http_client import HttpClient


class CNBRatesClientException(Exception):
    pass


class CNBRatesClient(HttpClient):
    base_url = 'https://www.cnb.cz/cs/financni-trhy/devizovy-trh/kurzy-devizoveho-trhu/kurzy-devizoveho-trhu/denni_kurz.txt' # noqa E501

    def __init__(self):
        super().__init__(base_url=self.base_url)
        self.base_url = self.base_url[:-1]

    # Parsers
    @staticmethod
    def _parse_response(response: Response, temp_date: str, currencies: List[str]) -> List[List[str]]:
        data = []
        for line in response.text.split('\n')[2:]:
            line_split = line.split('|')
            if len(line_split) == 5 and (currencies is None or line_split[3] in currencies):
                data.append([temp_date] + line_split[:4] + [line_split[4].replace(',', '.')])
        return data

    @staticmethod
    def _parse_date(response: Response, dt: date, today: date, curr_flag: bool) -> str:
        if dt == today and not curr_flag:
            parse_date = response.text[:response.text.find('#')].strip().split('.')
            return f"{parse_date[2]}-{parse_date[1]}-{parse_date[0]}"
        return dt.strftime('%Y-%m-%d')

    # Main API call method
    @on_exception(expo, CNBRatesClientException, max_tries=10)
    def get_rates(self, dates: List[datetime], today: date, curr_flag: bool, currencies: List[str]) -> List[str]:
        data = []
        for d in dates:
            date_param = d.strftime('%d.%m.%Y')
            raw_response = self.get_raw(f"{self.base_url}?date={date_param}", timeout=15)
            raw_response.raise_for_status()

            temp_date = self._parse_date(raw_response, d, today, curr_flag)
            data = self._parse_response(raw_response, temp_date, currencies)

        return data
