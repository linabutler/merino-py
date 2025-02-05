# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""Unit tests for the __init__ provider module."""

import pytest
from pytest_mock import MockerFixture

from merino.config import settings
from merino.exceptions import InvalidProviderError
from merino.providers import ProviderType, get_providers, init_providers


@pytest.mark.asyncio
async def test_init_providers() -> None:
    """Test for the `init_providers` method of the Merino providers module."""
    await init_providers()

    providers, default_providers = get_providers()

    assert len(providers) == 4
    assert ProviderType.ADM in providers
    assert ProviderType.WIKI_FRUIT in providers
    assert ProviderType.TOP_PICKS in providers

    assert len(default_providers) == 3


@pytest.mark.asyncio
async def test_init_providers_unknown_provider_type(mocker: MockerFixture) -> None:
    """Test for the `init_providers` with an unknown provider."""
    mocker.patch.dict(settings.providers, values={"unknown-provider": {}})

    with pytest.raises(InvalidProviderError) as excinfo:
        await init_providers()

    assert str(excinfo.value) == "Unknown provider type: unknown-provider"
