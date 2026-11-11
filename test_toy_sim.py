from toy_sim import ALL, hijacked_share, incident_replay


def test_hijack_spreads_without_rov():
    _, _, _, base, _ = incident_replay()
    assert 0 < base <= 1


def test_upstream_rov_reduces_spread():
    _, _, _, base, with_up = incident_replay()
    assert with_up < base


def test_everyone_checking_stops_hijack():
    attacker, _, victim, _, _ = incident_replay()
    assert hijacked_share(victim, attacker, set(ALL)) == 0