__version__ = "0.0.1"

# Standard Library Imports
import functools
import math
import operator
from dataclasses import dataclass
from typing import Any, Iterable, Iterator, List, Tuple, Union

CountLimit = int

CountLimits = Tuple[CountLimit, ...]

ClockSpec = Union[List[Any], range, int]

ClockSpecs = Tuple[ClockSpec, ...]


@dataclass
class CountState:
    counters: Tuple[int, ...]
    cycles: int


@dataclass
class ClockState(CountState):
    rendered: Tuple[Any, ...]

    @classmethod
    def from_countstate(cls, specs: ClockSpecs, state: CountState) -> "ClockState":
        rendered = tuple([_rendered_from_counter(s, c) for s, c in zip(specs, state.counters)])
        return cls(counters=state.counters, cycles=state.cycles, rendered=rendered)


class ClockRange:
    """ClockRange produces values according to a given clock-like periodic sequence specification.

    Parameters
    ----------
    specs : ClockSpecs

    See Also
    ----------
    clockrange.ClockState : encapsulates values produced by ClockRange instances

    Examples
    --------

    ClockRange instances are iterable:
    >>> it = iter(ClockRange((24, 60, 60)))

    ClockRange instances support random access:
    >>> clock = ClockRange((24, 60, 60))
    >>> assert clock[60].counters == (0, 1, 0)

    ClockRange specifications accept integers representing 0-N ranges:
    >>> clock = ClockRange((24, 60, 60))
    >>> assert clock[0].counters == (0, 0, 0)
    >>> assert clock[1].counters == (0, 0, 1)
    >>> assert clock[60].counters == (0, 1, 0)
    >>> assert clock[86400].counters == (0, 0, 0)
    >>> assert clock[86400].cycles == 1

    ClockRange specifications accept lists of arbitrary symbols:
    >>> clock = ClockRange((2, ["A", "B"]))
    >>> assert clock[0].counters == (0, 0)
    >>> assert clock[0].rendered == (0, "A")
    >>> assert clock[3].rendered == (1, "B")

    ClockRange specifications accept native range instances:
    >>> clock = ClockRange((range(1, 20, 2), 100))
    >>> assert clock[0].counters == (0, 0)
    >>> assert clock[0].rendered == (1, 0)
    >>> assert clock[100].counters == (1, 0)
    >>> assert clock[100].rendered == (3, 0)

    """

    def __init__(self, specs: ClockSpecs):
        self.limits = _limits_from_specs(specs)
        self.specs = specs

    def __getitem__(self, key: int) -> ClockState:
        if key < 0:
            raise IndexError("argument 'key' must be >= 0")
        countstate = _countstate_from_ticks(self.limits, key)
        return ClockState.from_countstate(self.specs, countstate)

    def __len__(self) -> int:
        return _multiply(self.limits)

    def __iter__(self) -> Iterator[ClockState]:
        ticks = 0
        while True:
            yield self[ticks]
            ticks += 1

    def ticks(self, state: ClockState) -> int:
        """Returns the number of ticks needed to build 'state', according to the known spec

        Parameters
        ----------
        state : ClockState
            ClockState data previously produced by this ClockRange instance

        Returns
        -------
        int
            The number of ticks needed to produce the given state
        """
        return _ticks_from_countstate(self.limits, state)


def _rendered_from_counter(spec: ClockSpec, counter: int) -> Any:
    if isinstance(spec, int):
        return counter
    if isinstance(spec, (list, tuple)):
        return spec[counter]
    if isinstance(spec, range):
        return spec.start + (counter * spec.step)
    raise TypeError(f"unsupported type for argument 'spec' {type(spec)}")


def _limits_from_specs(specs: ClockSpecs) -> CountLimits:
    return tuple([_limit_from_spec(spec) for spec in specs])


def _limit_from_spec(spec: ClockSpec) -> CountLimit:
    if isinstance(spec, int):
        return spec
    if isinstance(spec, (list, tuple)):
        return len(spec)
    if isinstance(spec, range):
        return math.ceil((spec.stop - spec.start) / spec.step)
    raise TypeError(f"unsupported type for argument 'spec' {type(spec)}")


def _countstate_from_ticks(limits: CountLimits, ticks: int) -> CountState:
    counters = [0] + [0 for _ in limits]
    capacity = _multiply(limits)
    for idx, _ in enumerate(limits):
        counters[idx] = int(ticks // capacity)
        ticks = int(ticks % capacity)
        capacity = int(capacity / limits[idx])
    cycles = counters[0]
    counters = counters[1:]
    counters[-1] = ticks
    return CountState(tuple(counters), cycles)


def _ticks_from_countstate(limits: CountLimits, state: CountState) -> int:
    ticks = 0
    counters = [state.cycles] + list(state.counters)
    capacity = _multiply(limits)
    for idx, _ in enumerate(limits):
        ticks += counters[idx] * capacity
        capacity = int(capacity / limits[idx])
    ticks += counters[-1]
    return int(ticks)


def _multiply(integers: Iterable[int]) -> int:
    return functools.reduce(operator.mul, integers, 1)
