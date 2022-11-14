# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""Integration tests for the Merino __error__ API endpoint."""

import logging
from logging import LogRecord
from typing import Any

from fastapi.testclient import TestClient
from freezegun import freeze_time
from pytest import LogCaptureFixture

from tests.integration.api.types import LogDataFixture
from tests.types import FilterCaplogFixture


def test_error(
    client: TestClient, caplog: LogCaptureFixture, filter_caplog: FilterCaplogFixture
) -> None:
    """Test that the error endpoint is supported to conform to dockerflow"""
    caplog.set_level(logging.ERROR)

    response = client.get("/__error__")

    assert response.status_code == 500
    records = filter_caplog(caplog.records, "merino.web.dockerflow")
    assert len(records) == 1
    assert records[0].message == "The __error__ endpoint was called"


@freeze_time("1998-03-31")
def test_error_request_log_data(
    caplog: LogCaptureFixture,
    filter_caplog: FilterCaplogFixture,
    log_data: LogDataFixture,
    client: TestClient,
) -> None:
    """
    Tests that the request logs for the '__error__' endpoint contain the required
    extra data
    """
    caplog.set_level(logging.INFO)

    expected_log_data: dict[str, Any] = {
        "name": "request.summary",
        "agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 11.2; rv:85.0)"
            " Gecko/20100101 Firefox/103.0"
        ),
        "path": "/__error__",
        "method": "GET",
        "lang": "en-US",
        "querystring": {},
        "errno": 0,
        "code": 500,
        "time": "1998-03-31T00:00:00",
    }

    client.get(
        "/__error__",
        headers={
            "accept-language": "en-US",
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 11.2; rv:85.0) "
                "Gecko/20100101 Firefox/103.0"
            ),
        },
    )

    records: list[LogRecord] = filter_caplog(caplog.records, "request.summary")
    assert len(records) == 1

    record: LogRecord = records[0]
    assert log_data(record) == expected_log_data
