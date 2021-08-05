from datetime import date
from unittest import TestCase

from ..templatetags import filters


class PreviousMonthTestCase(TestCase):
    def test_gets_previous_month(self):
        source = date(2021, 6, 1)

        actual = filters.previous_month(source)

        self.assertEqual(actual, date(2021, 5, 1))

    def test_gets_previous_month_for_previous_year(self):
        source = date(2021, 1, 1)

        actual = filters.previous_month(source)

        self.assertEqual(actual, date(2020, 12, 1))

    def test_reverts_to_now_when_date_invalid(self):
        source = 'hello'

        actual = filters.previous_month(source)

        self.assertEqual(actual, date.today())


class NextMonthTestCase(TestCase):
    def test_gets_next_month(self):
        source = date(2021, 6, 1)

        actual = filters.next_month(source)

        self.assertEqual(actual, date(2021, 7, 1))

    def test_gets_next_month_for_next_year(self):
        source = date(2021, 12, 1)

        actual = filters.next_month(source)

        self.assertEqual(actual, date(2022, 1, 1))

    def test_reverts_to_now_when_date_invalid(self):
        source = 'hello'

        actual = filters.next_month(source)

        self.assertEqual(actual, date.today())
