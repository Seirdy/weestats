"""Set up common values for reading/working with the repo's sample logs."""
from pathlib import Path

import numpy as np
import pytest  # type: ignore

from clogstats.stats.gather_stats import DateRange


@pytest.fixture()
def date_range() -> DateRange:
    """Date range for sample logs."""
    start_time = np.datetime64("2020-06-19T12:46:00")
    end_time = np.datetime64("2020-06-19T13:43:00")
    return DateRange(start_time=start_time, end_time=end_time)


@pytest.fixture()
def log_path() -> Path:
    """Path to sample logs in repo."""
    return Path(__file__).parent.joinpath("sample_logs")
