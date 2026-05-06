import datetime
import logging
import os
import sys


class _StderrToLogger:
    def __init__(self, logger, original_stream):
        self.logger = logger
        self.original_stream = original_stream
        self._buffer = ""

    def write(self, text):
        self.original_stream.write(text)
        self.original_stream.flush()
        self._buffer += text
        while "\n" in self._buffer:
            line, self._buffer = self._buffer.split("\n", 1)
            if line.strip():
                self.logger.error(line.rstrip())

    def flush(self):
        self.original_stream.flush()
        if self._buffer.strip():
            self.logger.error(self._buffer.rstrip())
            self._buffer = ""

    def isatty(self):
        return getattr(self.original_stream, "isatty", lambda: False)()


_ORIGINAL_EXCEPTHOOK = sys.excepthook


def setup_six6_logging(module_name, base_dir):
    """Configure dated six6 logs under base_dir/log without hiding stderr."""
    log_dir = os.path.join(os.path.abspath(base_dir), "log")
    os.makedirs(log_dir, exist_ok=True)
    date = datetime.datetime.now().strftime("%Y-%m-%d")
    log_file = os.path.join(log_dir, f"{date}_{module_name}.log")

    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
        "%Y-%m-%d %H:%M:%S",
    )

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(formatter)
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)

    root_logger.addHandler(file_handler)
    root_logger.addHandler(stream_handler)

    logger = logging.getLogger(module_name)
    if not isinstance(sys.stderr, _StderrToLogger):
        sys.stderr = _StderrToLogger(logger, sys.__stderr__)

    def log_uncaught(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            _ORIGINAL_EXCEPTHOOK(exc_type, exc_value, exc_traceback)
            return
        root_logger.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

    sys.excepthook = log_uncaught
    return logger
