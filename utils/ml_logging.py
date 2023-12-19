import functools
import logging
import time
from typing import Callable, Optional

# Define a new logging level named "KEYINFO" with a level of 25
KEYINFO_LEVEL_NUM = 25
logging.addLevelName(KEYINFO_LEVEL_NUM, "KEYINFO")  # type: ignore


def keyinfo(self: logging.Logger, message, *args, **kws):  # type: ignore
    """
    Log 'msg % args' with severity 'KEYINFO'.
    """
    if self.isEnabledFor(KEYINFO_LEVEL_NUM):
        self._log(KEYINFO_LEVEL_NUM, message, args, **kws)


logging.Logger.keyinfo = keyinfo  # type: ignore


class CustomFormatter(logging.Formatter):  # type: ignore
    """
    CustomFormatter overrides 'funcName' and 'filename' attributes in the log record.

    When a decorator is used to log function calls in a different file, this formatter helps
    preserve the correct file and function name in the log records.

    - 'funcName' is overridden with 'func_name_override', if present in the record.
    - 'filename' is overridden with 'file_name_override', if present in the record.
    """

    def format(self, record: logging.LogRecord) -> str:  # type: ignore
        record.funcName = getattr(record, "func_name_override", record.funcName)
        record.filename = getattr(record, "file_name_override", record.filename)
        return super().format(record)


def get_logger(
    name: str = "micro",
    level: Optional[int] = None,
    include_stream_handler: bool = True,
) -> logging.Logger:  # type: ignore
    """
    Returns a configured logger with a custom name, level, and formatter.

    Parameters:
    name (str): Name of the logger.
    level (int, optional): Initial logging level. Defaults to INFO if not provided.
    include_stream_handler (bool): Whether to include a stream handler. Defaults to True.

    Returns:
    logging.Logger: Configured logger instance.
    """
    formatter = CustomFormatter(
        "%(asctime)s - %(name)s - %(processName)-10s - "
        "%(levelname)-8s %(message)s (%(filename)s:%(funcName)s:%(lineno)d)"
    )
    logger = logging.getLogger(name)  # type: ignore

    # Set the logging level if it's specified or if the logger has no level set
    if level is not None or logger.level == 0:
        logger.setLevel(level or logging.INFO)  # type: ignore

    if include_stream_handler and not any(isinstance(h, logging.StreamHandler) for h in logger.handlers):  # type: ignore
        sh = logging.StreamHandler()  # type: ignore
        sh.setFormatter(formatter)
        logger.addHandler(sh)

    return logger


def log_function_call(
    logger_name: str, log_inputs: bool = False, log_output: bool = False
) -> Callable:
    """
    Decorator to log function calls, input arguments, output, execution duration, and completion message.

    Parameters:
    logger_name (str): The name for the logger.
    log_inputs (bool): Whether to log input arguments. Defaults to True.
    log_output (bool): Whether to log the function's output. Defaults to True.

    Returns:
    Callable: The decorated function.
    """

    def decorator_log_function_call(func):
        @functools.wraps(func)
        def wrapper_log_function_call(*args, **kwargs):
            logger = get_logger(logger_name)
            func_name = func.__name__

            if log_inputs:
                args_str = ", ".join(map(str, args))
                kwargs_str = ", ".join(f"{k}={v}" for k, v in kwargs.items())
                logger.info(
                    f"Function {func_name} called with arguments: {args_str} and keyword arguments: {kwargs_str}"
                )
            else:
                logger.info(f"Function {func_name} called")

            start_time = time.time()
            result = func(*args, **kwargs)
            duration = time.time() - start_time

            if log_output:
                logger.info(f"Function {func_name} output: {result}")

            logger.info(f"Function {func_name} executed in {duration:.2f} seconds")
            logger.info(f"Function {func_name} completed")

            return result

        return wrapper_log_function_call

    return decorator_log_function_call
