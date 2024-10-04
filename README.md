CNB exchange rates Extractor
=============

This component was built to extract the exchange rates from [CNB](www.cnb.cz) right to Keboola storage. It was developed using the [KBC template](https://bitbucket.org/kds_consulting_team/kbc-python-template/src/master/) provided kindly by the KDS team.

It lets the user specify date ranges in the component UI and then it basically just access endpoint and extracts the exchange rates for specified dates. User can also select only specific currencies to be downloaded.

Functionality notes
===================

Prerequisites
=============

Get the API token, register application, etc.

Features
========

| **Feature**             | **Note**                                      |
|-------------------------|-----------------------------------------------|
| Incremental loading     | Allows fetching data in new increments.       |
| Date range filter       | Specify date range.                           |

Supported endpoints
===================
- [cs/financni-trhy/devizovy-trh/kurzy-devizoveho-trhu/kurzy-devizoveho-trhu/denni_kurz.txt](https://www.cnb.cz/cs/financni-trhy/devizovy-trh/kurzy-devizoveho-trhu/kurzy-devizoveho-trhu/denni_kurz.txt)

If you need more endpoints, please submit your request to
[ideas.keboola.com](https://ideas.keboola.com/)

Configuration
=============

Dates
-------
You can specify the time period for rates extraction.

Currencies
-------
In the UI is prepared selector for currencies.

Output
======

List of tables, foreign keys, schema.

Development
-----------

If required, change local data folder (the `CUSTOM_FOLDER` placeholder) path to
your custom path in the `docker-compose.yml` file:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    volumes:
      - ./:/code
      - ./CUSTOM_FOLDER:/data
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Clone this repository, init the workspace and run the component with following
command:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
git clone {{ cookiecutter.repository_url }} {{ cookiecutter. repository_folder_name }}
cd {{ cookiecutter. repository_folder_name }}
docker-compose build
docker-compose run --rm dev
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Run the test suite and lint check using this command:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
docker-compose run --rm test
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Integration
===========

For information about deployment and integration with KBC, please refer to the
[deployment section of developers
documentation](https://developers.keboola.com/extend/component/deployment/)
