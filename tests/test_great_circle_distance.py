# coding: utf-8


import pytest

from find_customers import great_circle_distance


def test_distance_is_zero_for_the_same_points():
    assert great_circle_distance((0, 0), (0, 0)) == 0


# Data from http://www.greatcirclemapper.net/en/great-circle-mapper.html
@pytest.mark.parametrize('start,end,low,high', [
    # EIDW | DUB -> KIAD | IAD = 5478
    ((53.4212989807, -6.2700700760), (38.9444999700, -77.4558029200), 5450, 5490),
    # UKBB | KBP -> YSSY | SYD = 14911
    ((50.3450012207, 30.8946990967), (-33.9460983276, 151.1770019531), 14835, 14985),
    # EIDW | DUB -> LEBL | BCN = 1486
    ((53.4212989807, -6.2700700760), (41.2971000671, 2.0784599781), 1478, 1493)
])
def test_known_distances(start, end, low, high):
    assert low < great_circle_distance(start, end) < high


def test_raises_if_unable_to_create_location():
    with pytest.raises(TypeError):
        great_circle_distance((0,), (0,))


@pytest.mark.parametrize('first', [
    None,
    42,
    dict()
])
def test_raises_if_has_no_lat_attribute(first):
    with pytest.raises(AttributeError) as err:
        great_circle_distance(first, (0, 0))

    assert "has no attribute 'lat'" in str(err)


def test_raises_if_has_no_lon_attribute():
    bad_location = type('Location', (object,), dict(lat=0))

    with pytest.raises(AttributeError) as err:
        great_circle_distance(bad_location, (0, 0))

    assert "has no attribute 'lon'" in str(err)


def test_raises_if_not_a_float():
    with pytest.raises(TypeError):
        great_circle_distance(('0', 0), (0, 0))

