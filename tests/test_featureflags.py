from dynaconf.utils import DynaconfDict

from merino.featureflags import FeatureFlags, session_id_context

mocked_settings = DynaconfDict(
    {
        "flags": {
            "test-enabled": {"scheme": "random", "enabled": 1},
            "test-not-enabled": {"scheme": "random", "enabled": 0},
            "test-perc-enabled": {"scheme": "random", "enabled": 0.5},
            "test-perc-enabled-session": {"scheme": "session", "enabled": 0.5},
        }
    }
)


def test_enabled():
    flags = FeatureFlags(mocked_settings)
    assert flags.is_enabled("test-enabled") is True


def test_not_enabled():
    flags = FeatureFlags(mocked_settings)
    assert flags.is_enabled("test-not-enabled") is False


def test_enabled_perc():
    flags = FeatureFlags(mocked_settings)
    assertions = {
        b"\x00\x00\x00\x00": True,
        b"\xff\xff\xff\xff": False,
    }

    for bid, test in assertions.items():
        assert flags.is_enabled("test-perc-enabled", bucket_for=bid) is test


def test_enabled_perc_session():
    flags = FeatureFlags(mocked_settings)
    assertions = {
        "000": True,
        "fff": False,
    }

    for bid, test in assertions.items():
        session_id_context.set(bid)
        assert flags.is_enabled("test-perc-enabled-session") is test
