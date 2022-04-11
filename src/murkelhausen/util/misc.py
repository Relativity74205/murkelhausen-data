"""Miscellaneous functions and definitions.

Anything that was declared here should be of a very general purpose and not
tied to this codebase in particular.
"""

from typing import Callable, Any, TypeVar, cast
from functools import wraps


#: **Function-type identifier** - By asserting to mypy that a decorator only ever consumes
#: functions, the wrapped function will keep its original signature.
F = TypeVar("F", bound=Callable[..., Any])


def run_once(func: F) -> F:
    """Decorator which ensures that a function can only be run a single time.

    The value that the original function returns is cached internally, and will
    be returned on consecutive calls without running the original function's code.

    Notes:
        By introspecting the wrapper's internals, the run_once logic can be
        circumvented. Every wrapped function has a dunder attribute
        `__wrapped__`, which is used to persist whether the internal
        function was already run or not. Hence, manually setting its attribute
        `has_run` to False will allow additional executions.

    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        if not func.has_run:
            func.result = func(*args, **kwargs)
            func.has_run = True
        return func.result

    func.has_run = False  # type: ignore
    # casts have no influence on runtime behavior and only serve as assertion for mypy
    return cast(F, wrapper)
