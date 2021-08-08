import csv


def read_raw_transaction_data_from(file):
    reader = csv.reader(file, delimiter=",", quotechar='"')
    header_mapping = {i: header for i, header in enumerate(next(reader))}
    for i, row in enumerate(reader):
        yield {header_mapping[row_i]: value for row_i, value in enumerate(row)}
