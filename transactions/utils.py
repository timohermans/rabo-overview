import csv
from datetime import date
from dateutil.relativedelta import relativedelta


def read_raw_transaction_data_from(file):
    reader = csv.reader(file, delimiter=',', quotechar='"')
    header_mapping = {i: header for i, header in enumerate(next(reader))}
    for i, row in enumerate(reader):
        yield {header_mapping[row_i]: value for row_i, value in enumerate(row)}


def get_start_end_date_from(source: date):
    start_date = date(source.year, source.month, 1)
    end_date = start_date + relativedelta(months=1, days=-1)
    return start_date, end_date
