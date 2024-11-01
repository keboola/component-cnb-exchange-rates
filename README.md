CNB Exchange Rates Extractor
=============

This extractor enables you to download exchange rates from the Czech National Bank (CNB).

Exchange rates for commonly traded currencies are published every working day after 2:30 p.m. (Europe/Prague timezone) 
and are valid for the current working day. Where relevant, they also apply to the following Saturday, Sunday, or public holiday. 

For example, an exchange rate declared on Tuesday, December 23, is valid for Tuesday, December 23; the public holidays on December 24–26; 
and Saturday, December 27, and Sunday, December 28.

Find more information on CNB's official website: [www.cnb.cz](https://www.cnb.cz/cs/financni-trhy/devizovy-trh/kurzy-devizoveho-trhu/kurzy-devizoveho-trhu/)

Features
========

| **Feature**             | **Note**                                      |
|-------------------------|-----------------------------------------------|
| Incremental loading     | Allow fetching data in new increments.       |
| Date range filter       | Specify a date range.                           |

Supported Endpoints
===================

These are the endpoints that Keboola supports: [cs/financni-trhy/devizovy-trh/kurzy-devizoveho-trhu/kurzy-devizoveho-trhu/denni_kurz.txt](https://www.cnb.cz/cs/financni-trhy/devizovy-trh/kurzy-devizoveho-trhu/kurzy-devizoveho-trhu/denni_kurz.txt)

If you need additional endpoints, please submit your request to [ideas.keboola.com](https://ideas.keboola.com/).

Configuration
=============
[Create a new configuration](https://help.keboola.com/components/#creating-component-configuration) of the CNB Exchange Rates connector.

Dates
-------
You can specify the time period for rates extraction.

Currencies
-------
The UI includes a currency selector.

Output
======

Provides tables, foreign keys, and schema information.

Development
-----------

If required, change the local data folder path (the `CUSTOM_FOLDER` placeholder) to
your custom path in the `docker-compose.yml` file:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    volumes:
      - ./:/code
      - ./CUSTOM_FOLDER:/data
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Clone this repository, initialize the workspace, and run the connector with the following
commands:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
git clone {{ cookiecutter.repository_url }} {{ cookiecutter. repository_folder_name }}
cd {{ cookiecutter. repository_folder_name }}
docker-compose build
docker-compose run --rm dev
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Run the test suite and lint checks using this command:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
docker-compose run --rm test
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Integration
===========

For information about deployment and integration with Keboola, please refer to the
[deployment section of the developers'
documentation](https://developers.keboola.com/extend/component/deployment/)
