import logging
import re

from app.log_config import LOG_DATEFMT, LOG_FORMAT


def test_log_format_includes_milliseconds() -> None:
    formatter = logging.Formatter(fmt=LOG_FORMAT, datefmt=LOG_DATEFMT)
    record = logging.LogRecord(
        name="app.test",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="hello",
        args=(),
        exc_info=None,
    )
    record.created = 1_713_000_000.678
    record.msecs = 678.0

    formatted = formatter.format(record)

    assert re.search(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.678", formatted)
