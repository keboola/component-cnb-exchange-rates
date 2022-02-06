## CNB exchange rates Extractor

This component was built to extract the exchange rates from [CNB](www.cnb.cz) right to Keboola storgae. It was developed using the [KBC template](https://bitbucket.org/kds_consulting_team/kbc-python-template/src/master/) provided kindly by the KDS team.

It lets the user specify date ranges in the component UI and then it basically just access this [endpoint](https://www.cnb.cz/cs/financni-trhy/devizovy-trh/kurzy-devizoveho-trhu/kurzy-devizoveho-trhu/denni_kurz.txt) and extracts the exchange rates for specified dates. User can also select only specific currencies to be downloaded.

### Contact

In case of any issues or problems with this component don't hesitate to contact me on this mail: **zdenekhanik6@gmail.com**