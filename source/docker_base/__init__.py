import sys
import traceback


def print_error_message(
        message):
    # Flush stdout to keep messages in the correct order. Otherwise we get
    # info messages after the error message.
    sys.stdout.flush()
    sys.stderr.write("{}\n".format(message))


def call_subcommand(
        function,
        *arguments):

    status = 1

    try:
        function(*arguments)
        status = 0
    except SystemExit:
        raise
    except RuntimeError as exception:
        print_error_message(str(exception))
    except:
        lines = traceback.format_exc().splitlines()
        print_error_message(lines[-3])
        print_error_message(lines[-2])
        print_error_message(lines[-1])

    return status
