# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""Module for test configurations for the tests directory."""

from logging import LogRecord

import pytest

from tests.types import FilterCaplogFixture


@pytest.fixture(scope="session", name="filter_caplog")
def fixture_filter_caplog() -> FilterCaplogFixture:
    """Return a function that will filter pytest captured log records for a given logger
    name.
    """

    def filter_caplog(records: list[LogRecord], logger_name: str) -> list[LogRecord]:
        """Filter pytest captured log records for a given logger name"""
        return [record for record in records if record.name == logger_name]

    return filter_caplog
