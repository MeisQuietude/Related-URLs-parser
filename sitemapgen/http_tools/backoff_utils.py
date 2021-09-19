import sys
import traceback


def log_backoff(details, logger, log_level):
    msg = "Backing off %s(%s) for %.1fs (%s)"
    log_args = [details['target'].__name__, repr(details['args']), details['wait']]

    exc_typ, exc, _ = sys.exc_info()
    if exc is not None:
        exc_fmt = traceback.format_exception_only(exc_typ, exc)[-1]
        log_args.append(exc_fmt.rstrip("\n"))
    else:
        log_args.append(details['value'])
    logger.log(log_level, msg, *log_args)


def log_giveup(details, logger, log_level):
    msg = "Giving up %s(%s) after %d tries (%s)"
    log_args = [details['target'].__name__, repr(details['args']), details['tries']]

    exc_typ, exc, _ = sys.exc_info()
    if exc is not None:
        exc_fmt = traceback.format_exception_only(exc_typ, exc)[-1]
        log_args.append(exc_fmt.rstrip("\n"))
    else:
        log_args.append(details['value'])

    logger.log(log_level, msg, *log_args)
