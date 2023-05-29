from __future__ import annotations

from datetime import datetime, tzinfo
from typing import List, NamedTuple, Optional, Sequence, Tuple, Union

import pytz

from . import sa

__all__ = ['HeadersAndDataTuple', 'naive_to_utc', 'get_fiscal_year']


class HeadersAndDataTuple(NamedTuple):
    headers: List[str]
    data: Sequence[sa.engine.Row]


def naive_to_utc(
    dt: datetime, timezone: Optional[Union[str, tzinfo]] = None
) -> datetime:
    """
    Return a UTC datetime for a given naive datetime or date object.

    Localizes it to the given timezone and converts it into a UTC datetime
    """
    tz: tzinfo
    if timezone:
        if isinstance(timezone, str):
            tz = pytz.timezone(timezone)
        else:
            tz = timezone
    elif isinstance(dt, datetime) and dt.tzinfo:
        tz = dt.tzinfo
    else:
        tz = pytz.UTC

    if isinstance(tz, pytz.BaseTzInfo):
        dt = tz.localize(dt)
    return dt.astimezone(tz).astimezone(pytz.UTC)


def get_fiscal_year(jurisdiction: str, dt: datetime) -> Tuple[datetime, datetime]:
    """
    Return the financial year for a given jurisdiction and timestamp.

    Returns start and end dates as tuple of timestamps. Recognizes April 1 as the start
    date for India (jurisfiction code: 'in'), January 1 everywhere else.

    Example::

        get_fiscal_year('IN', utcnow())
    """
    if jurisdiction.lower() == 'in':
        if dt.month < 4:
            start_year = dt.year - 1
        else:
            start_year = dt.year
        # starts on April 1 XXXX
        fy_start = datetime(start_year, 4, 1)
        # ends on April 1 XXXX + 1
        fy_end = datetime(start_year + 1, 4, 1)
        timezone = 'Asia/Kolkata'
        return (naive_to_utc(fy_start, timezone), naive_to_utc(fy_end, timezone))
    return (
        naive_to_utc(datetime(dt.year, 1, 1)),
        naive_to_utc(datetime(dt.year + 1, 1, 1)),
    )
