from datetime import date
from unittest import TestCase

from ..templatetags import filters


class PreviousMonthTestCase(TestCase):
    def test_gets_previous_month(self) -> None:
        source = date(2021, 6, 1)

        actual = filters.previous_month(source)

        self.assertEqual(actual, date(2021, 5, 1))

    def test_gets_previous_month_for_previous_year(self) -> None:
        source = date(2021, 1, 1)

        actual = filters.previous_month(source)

        self.assertEqual(actual, date(2020, 12, 1))

class NextMonthTestCase(TestCase):
    def test_gets_next_month(self) -> None:
        source = date(2021, 6, 1)

        actual = filters.next_month(source)

        self.assertEqual(actual, date(2021, 7, 1))

    def test_gets_next_month_for_next_year(self) -> None:
        source = date(2021, 12, 1)

        actual = filters.next_month(source)

        self.assertEqual(actual, date(2022, 1, 1))
