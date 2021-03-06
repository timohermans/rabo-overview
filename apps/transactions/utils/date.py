from datetime import date
from typing import Tuple
from dateutil.relativedelta import relativedelta


def get_start_end_date_from(source: date) -> Tuple[date, date]:
    start_date = date(source.year, source.month, 1)
    end_date = start_date + relativedelta(months=1, days=-1)
    return start_date, end_date
