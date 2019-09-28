# Third-Party Imports
import pytest

# Local Imports
from clockrange import ClockRange, ClockState, _limit_from_spec, _rendered_from_counter


@pytest.mark.parametrize(
    "specs,ticks,counters,cycles,rendered",
    (
        # 1-stage clock
        ((10,), 0, (0,), 0, (0,)),
        ((10,), 9, (9,), 0, (9,)),
        ((10,), 20, (0,), 2, (0,)),
        ((range(10),), 0, (0,), 0, (0,)),
        ((range(10),), 9, (9,), 0, (9,)),
        ((range(10),), 20, (0,), 2, (0,)),
        ((range(0, 10, 1),), 0, (0,), 0, (0,)),
        ((range(0, 10, 1),), 9, (9,), 0, (9,)),
        ((range(0, 10, 1),), 20, (0,), 2, (0,)),
        ((range(1, 10),), 0, (0,), 0, (1,)),
        ((range(1, 10),), 9, (0,), 1, (1,)),
        ((range(1, 10),), 20, (2,), 2, (3,)),
        ((range(1, 10, 2),), 20, (0,), 4, (1,)),
        ((["A", "B", "C"],), 0, (0,), 0, ("A",)),
        ((["A", "B", "C"],), 2, (2,), 0, ("C",)),
        (([1.22, "B", "C"],), 3, (0,), 1, (1.22,)),
        # 2-stages clock
        ((4, 10), 0, (0, 0), 0, (0, 0)),
        ((4, 10), 10, (1, 0), 0, (1, 0)),
        ((4, 10), 20, (2, 0), 0, (2, 0)),
        ((4, 10), 30, (3, 0), 0, (3, 0)),
        ((4, 10), 40, (0, 0), 1, (0, 0)),
        ((4, 10), 41, (0, 1), 1, (0, 1)),
        ((range(4), range(10)), 0, (0, 0), 0, (0, 0)),
        ((range(4), range(10)), 10, (1, 0), 0, (1, 0)),
        ((range(4), range(10)), 12, (1, 2), 0, (1, 2)),
        ((range(4), range(10)), 41, (0, 1), 1, (0, 1)),
        ((range(1, 4), range(1, 10)), 10, (1, 1), 0, (2, 2)),
        ((["A", "B", "C"], [10, 20, 30]), 0, (0, 0), 0, ("A", 10)),
        ((["A", "B", "C"], [10, 20, 30]), 5, (1, 2), 0, ("B", 30)),
        # 3-stages clock
        ((2, 4, 10), 41, (1, 0, 1), 0, (1, 0, 1)),
        ((2, 4, 10), 80, (0, 0, 0), 1, (0, 0, 0)),
    ),
)
def test_clockrange_random_access(specs, ticks, counters, cycles, rendered):
    assert ClockRange(specs)[ticks] == ClockState(counters, cycles, rendered)


def test_clockrange_random_access_with_negative_value_should_raise():
    crange = ClockRange((4, 10))
    with pytest.raises(IndexError):
        crange[-1]


def test_clockrange_iterable():
    iterable = iter(ClockRange((4, 10)))
    assert next(iterable) == ClockState((0, 0), cycles=0, rendered=(0, 0))
    assert next(iterable) == ClockState((0, 1), cycles=0, rendered=(0, 1))


def test_clockrange_len():
    assert len(ClockRange((4, 10))) == 40


def test_clockrange_state_ticks():
    crange = ClockRange((4, 10))
    state = crange[142]
    assert crange.ticks(state) == 142


def test_rendered_from_counter_spec_type_error():
    with pytest.raises(TypeError):
        _rendered_from_counter("aaa", None)


def test_limit_from_spec_spec_type_error():
    with pytest.raises(TypeError):
        _limit_from_spec("aaa")
