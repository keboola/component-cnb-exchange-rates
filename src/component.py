'''
Template Component main class.

'''
import csv
import logging
from datetime import datetime
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
        base_url = 'https://www.cnb.cz/cs/financni-trhy/devizovy-trh/kurzy-devizoveho-trhu/kurzy-devizoveho-trhu/' \
                   'denni_kurz.txt'

        status_code = 0
        kurzy = []

        # deset pokusů o stažení
        for i in range(10):
            r = requests.get(base_url)
            status_code = r.status_code
            if status_code == 200:
                datum = r.text.split('\n')[0].split('#')[0].strip().split('.')
                datum_API = datum[2] + '-' + datum[1] + '-' + datum[0]
                today = datetime.now(pytz.timezone('Europe/Prague'))
                today_str = today.strftime('%Y') + '-' + today.strftime('%m') + '-' + today.strftime('%d')
                for line in r.text.split('\n')[2:]:
                    line_split = line.split('|')
                    if len(line_split) == 5:
                        kurzy.append([datum_API] + line_split[:4] + [line_split[4].replace(',', '.')])
                        kurzy.append([today_str] + line_split[:4] + [line_split[4].replace(',', '.')])
                print('Connected to www.cnb.cz successfully.')
                print('Attemp nmr. ' + str(i+1))
                break
            else:
                time.sleep(2)

        # Create output table (Tabledefinition - just metadata)
        table = self.create_out_table_definition(name='output.csv',
                                                 destination=out_storage_path,
                                                 incremental=out_incremental,
                                                 primary_key=['date', 'code'])

        out_table_path = table.full_path
        logging.info(out_table_path)

        # ověřuji délku pole kurzů, pokud by se někdy v budoucnu např. změnila struktura API
        if status_code == 200 and len(kurzy) > 0:
            with open(out_table_path, mode='wt', encoding='utf-8', newline='') as out_file:
                write = csv.writer(out_file)
                write.writerow(header)
                write.writerows(kurzy)
        else:
            raise Exception("Data were not fetched!")

        # Save table manifest (output.csv.manifest) from the tabledefinition
        self.write_manifest(table)

        # Write new state - will be available next run
        self.write_state_file({"some_state_parameter": "value"})

        # printing favourite color
        hex_color = params['favorite_color'].lstrip('#')
        rgb_color = tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))
        logging.warning('Your favourite color is: ' + self.closest_colour(rgb_color))


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
