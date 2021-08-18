from datetime import date
from transactions.templatetags import filters


def test_gets_previous_month() -> None:
    source = date(2021, 6, 1)

    actual = filters.previous_month(source)

    assert actual == date(2021, 5, 1)


def test_gets_previous_month_for_previous_year() -> None:
    source = date(2021, 1, 1)

    actual = filters.previous_month(source)

    assert actual == date(2020, 12, 1)


def test_gets_next_month() -> None:
    source = date(2021, 6, 1)

    actual = filters.next_month(source)

    assert actual == date(2021, 7, 1)


def test_gets_next_month_for_next_year() -> None:
    source = date(2021, 12, 1)

    actual = filters.next_month(source)

    assert actual == date(2022, 1, 1)
