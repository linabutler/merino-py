# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""Module for communication with Kinto (Remote Settings)."""

from typing import Optional

import requests
from pydantic import BaseModel, Field
from requests import Response as RequestsResponse


class KintoEnvironment(BaseModel):
    """Class that holds information about Kinto environment variables."""

    server: str
    bucket: str
    collection: str


class KintoSuggestion(BaseModel):
    """Class that holds information about a Suggestion in Kinto."""

    id: int
    url: str
    iab_category: str
    icon: str
    advertiser: str
    title: str
    keywords: list[str] = Field(default_factory=list)
    # Both impression_url and click_url are optional. They're absent for
    # Mozilla-provided Wikipedia suggestions.
    click_url: Optional[str]
    impression_url: Optional[str]


class KintoAttachment(BaseModel):
    """Class that holds information about an attachment in Kinto."""

    filename: str
    mimetype: str


class KintoRequestAttachment(KintoAttachment):
    """Class that holds information about an attachment for the Kinto API."""

    filecontent: bytes
    suggestions: list[KintoSuggestion]


class KintoResponseAttachment(KintoAttachment):
    """Class that holds information about an attachment from the Kinto API."""

    location: str


class KintoResponseRecord(BaseModel):
    """Class that holds information about a record from the Kinto API."""

    id: str
    attachment: KintoResponseAttachment


class KintoResponse(BaseModel):
    """Class that holds Kinto API response data"""

    data: KintoResponseRecord


def delete_records(environment: KintoEnvironment) -> None:
    """Clear all record information from Kinto."""
    url: str = (
        f"{environment.server}/v1/"
        f"buckets/{environment.bucket}/"
        f"collections/{environment.collection}/"
        f"records"
    )
    response: RequestsResponse = requests.delete(url)
    response.raise_for_status()


def get_record(environment: KintoEnvironment, record_id: str) -> KintoResponseRecord:
    """Get attachment information from Kinto for the given record ID."""
    url: str = (
        f"{environment.server}/v1/"
        f"buckets/{environment.bucket}/"
        f"collections/{environment.collection}/"
        f"records/{record_id}"
    )
    response: RequestsResponse = requests.get(url)
    response.raise_for_status()

    kinto_response: KintoResponse = KintoResponse(**response.json())
    return kinto_response.data


def upload_attachment(
    environment: KintoEnvironment,
    record_id: str,
    attachment: KintoRequestAttachment,
    data_type: str,
) -> None:
    """Upload attachment to Kinto for the given record."""
    url: str = (
        f"{environment.server}/v1/"
        f"buckets/{environment.bucket}/"
        f"collections/{environment.collection}/"
        f"records/{record_id}/"
        f"attachment"
    )
    response: RequestsResponse = requests.post(
        url=url,
        files={
            "attachment": (
                attachment.filename,
                attachment.filecontent,
                attachment.mimetype,
            ),
        },
        data={"data": f'{{"type": "{data_type}"}}'},
    )
    response.raise_for_status()


def upload_icons(environment: KintoEnvironment, icon_ids: set[str]) -> None:
    """Upload icon attachments to Kinto for the given icon IDs."""
    for icon_id in icon_ids:
        url: str = (
            f"{environment.server}/v1/"
            f"buckets/{environment.bucket}/"
            f"collections/{environment.collection}/"
            f"records/icon-{icon_id}/"
            f"attachment"
        )
        response: RequestsResponse = requests.post(
            url=url,
            files={
                "attachment": (
                    f"icon-{icon_id}.png",
                    f"icon-{icon_id}",
                    "image/png",
                ),
            },
            data={"data": '{"type": "icon"}'},
        )
        response.raise_for_status()
