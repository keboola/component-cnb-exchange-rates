'''
Template Component main class.

'''
import csv
import logging
from datetime import datetime, timedelta
# from datetime import datetime, date, timedelta
import pytz
import time
import requests
import webcolors

from keboola.component.base import ComponentBase
from keboola.component.exceptions import UserException

# configuration variables
KEY_API_TOKEN = '#api_token'
KEY_PRINT_HELLO = 'print_hello'

# list of mandatory parameters => if some is missing,
# component will fail with readable message on initialization.
REQUIRED_PARAMETERS = [KEY_PRINT_HELLO]
REQUIRED_IMAGE_PARS = []


class Component(ComponentBase):
    """
        Extends base class for general Python components. Initializes the CommonInterface
        and performs configuration validation.

        For easier debugging the data folder is picked up by default from `../data` path,
        relative to working directory.

        If `debug` parameter is present in the `config.json`, the default logger is set to verbose DEBUG mode.
    """

    def __init__(self):
        super().__init__()

    def closest_colour(self, requested_colour):
        min_colours = {}
        for key, name in webcolors.CSS3_HEX_TO_NAMES.items():
            r_c, g_c, b_c = webcolors.hex_to_rgb(key)
            rd = (r_c - requested_colour[0]) ** 2
            gd = (g_c - requested_colour[1]) ** 2
            bd = (b_c - requested_colour[2]) ** 2
            min_colours[(rd + gd + bd)] = name
        return min_colours[min(min_colours.keys())]

    def call_cnb_api(self, base_url, dates, today, curr_flag, currency):
        rates = []
        for d in dates:
            date_param = d.strftime('%d') + '.' + d.strftime('%m') + '.' + d.strftime('%Y')
            for _ in range(10):
                r = requests.get(base_url + '?date=' + date_param)
                status_code = r.status_code
                if status_code == 200:
                    if d == today and curr_flag is False:
                        parse_date = r.text[:r.text.find('#')].strip().split('.')
                        temp_date = parse_date[2] + '-' + parse_date[1] + '-' + parse_date[0]
                    else:
                        temp_date = d.strftime('%Y-%m-%d')

                    for line in r.text.split('\n')[2:]:
                        line_split = line.split('|')
                        if len(line_split) == 5 and currency is None:
                            rates.append([temp_date] + line_split[:4] + [line_split[4].replace(',', '.')])
                        elif len(line_split) == 5 and line_split[3] in currency:
                            rates.append([temp_date] + line_split[:4] + [line_split[4].replace(',', '.')])
                    break
                else:
                    time.sleep(1)
        return rates

    def run(self):
        '''
        Main execution code
        '''

        logging.info('Running...')

        # config.json parameters
        params = self.configuration.parameters

        out_table_name = params['file_name']
        out_storage_path = 'in.c-cnb-extractor.' + out_table_name
        out_incremental = params['incremental']

        # output file definition - use if output mapping is enabled
        # kbc_out_path = self.configuration.config_data["storage"]["output"]["tables"][0]["destination"]
        # out_file_name = self.configuration.config_data["storage"]["output"]["tables"][0]["source"]
        # out_incremental = self.configuration.config_data["storage"]["output"]["tables"][0]["incremental"]

        header = ['date', 'country', 'currency', 'amount', 'code', 'rate']
        base_url = 'https://www.cnb.cz/cs/financni-trhy/devizovy-trh/kurzy-devizoveho-trhu/' \
                   'kurzy-devizoveho-trhu/denni_kurz.txt'

        # Get the dates from user input
        dates_list = []
        today = datetime.now(pytz.timezone('Europe/Prague')).date()

        if params['dates'] == "Current day (currently declared rates)":
            dates_list.append(today)
        elif params['dates'] == "Current day and yesterday":
            for i in range(2):
                dates_list.append(today - timedelta(days=i))
        elif params['dates'] == "Week":
            for i in range(7):
                dates_list.append(today - timedelta(days=i))
        elif params['dates'] == "Custom date range":
            try:
                date_from = datetime.strptime(params['dependent_date_from'], '%Y-%m-%d').date()
                date_to = datetime.strptime(params['dependent_date_to'], '%Y-%m-%d').date()
            except ValueError:
                raise UserException('Dates not specified correctly for custom date range!')

            if date_from >= date_to:
                raise UserException('\"Date from\" is higher or equal to date to!')
            elif date_from > today:
                raise UserException('\"Date from\" is in the future!')
            else:
                for i in range((min(date_to, today) - date_from).days + 1):
                    dates_list.append(date_from + timedelta(days=i))

            if date_to > today:
                logging.warning('For \"Date to\" you selected a day in the future! Therefore, '
                                '\"Date to\" was set to today\'s day')

        # If specific currencies are selected pick only the selected country codes
        if params['currency'] == 'All':
            selected_currency = None
        else:
            selected_currency = []
            for p in params:
                logging.info(p)
                if p.startswith("select_curr") and params[p]:
                    logging.warning(p.split('_'))
                    logging.warning(type(params[p]))
                    selected_currency.append(p.split('_')[2])

            if selected_currency == []:
                raise UserException('No currency was selected!')

        kurzy = self.call_cnb_api(base_url, dates_list, today, params['current_as_today'], selected_currency)

        # Create output table (Tabledefinition - just metadata)
        table = self.create_out_table_definition(name='output.csv',
                                                 destination=out_storage_path,
                                                 incremental=out_incremental,
                                                 primary_key=['date', 'code'])

        # ověřuji délku pole kurzů, pokud by se někdy v budoucnu např. změnila struktura API
        if len(kurzy) > 0:
            with open(table.full_path, mode='wt', encoding='utf-8', newline='') as out_file:
                write = csv.writer(out_file)
                write.writerow(header)
                write.writerows(kurzy)
        else:
            raise UserException("Data were not fetched!")

        # Save table manifest (output.csv.manifest) from the tabledefinition
        self.write_manifest(table)

        # Write new state - will be available next run
        self.write_state_file({"some_state_parameter": "value"})

        # printing favourite color
        hex_color = params['favorite_color'].lstrip('#')
        rgb_color = tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))
        logging.warning('Your job ran successfuly and your favourite color is: ' + self.closest_colour(rgb_color))


"""
        Main entrypoint
"""
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
