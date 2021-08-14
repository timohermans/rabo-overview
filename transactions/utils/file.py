import csv
from typing import Any, Dict, Iterator


def read_raw_transaction_data_from(file: Any) -> Iterator[Dict[str, str]]:
    reader = csv.reader(file, delimiter=",", quotechar='"')
    header_mapping = {i: header for i, header in enumerate(next(reader))}
    for row in reader:
        yield {header_mapping[row_i]: value for row_i, value in enumerate(row)}
