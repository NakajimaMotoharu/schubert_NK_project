"""Pure count guard for summaries of independently qualified evidence; never a PT/quality gate."""
import re


def _verified_count(value):
    if type(value) is not int or value < 1:
        raise ValueError('a positive independently verified integer test count is required')
    return value


def unit_pass_summary(verified_tests):
    return f'ALL{_verified_count(verified_tests)}_PASS_FOUR100_POST0'


def declared_test_count(summary):
    if not isinstance(summary, str):
        return None
    values = re.findall(r'(?:^|_)(?:ALL|RESOURCE)([1-9][0-9]*)_', summary)
    return int(values[0]) if len(values) == 1 else None


def matches_verified_count(summary, verified_tests):
    return declared_test_count(summary) == _verified_count(verified_tests)
