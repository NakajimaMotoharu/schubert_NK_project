"""SSC192/216: declarations stay exact; one captured existing20 history is separately joined."""
import re
from pg535_bootstrap_contract import normal20


def record(value):
    if not isinstance(value, str) or len(value) > 65536:
        return None
    pattern = r'\{ path=([^ ;\r\n]+) ; argv\[\]=([^\r\n]*?) ; ignore_errors=(yes|no) ; start_time=\[([^\]\r\n]*)\] ; stop_time=\[([^\]\r\n]*)\] ; pid=([0-9]+) ; code=([^ ;\r\n]+) ; status=([^ ;\r\n]+) \}'
    match = re.fullmatch(pattern, value)
    if match is None:
        return None
    parts = match.groups()
    if not parts[0].startswith('/') or any(x in parts[1] for x in
            (' ; ignore_errors=', ' ; start_time=', ' ; stop_time=', ' ; pid=', ' ; code=', ' ; status=')):
        return None
    return parts


def configuration(previous, actual, terminal, actor, start, end):
    if not (isinstance(previous, dict) and isinstance(actual, dict)
            and set(previous) == set(actual) and 'ExecStart' in previous
            and all(isinstance(v, str) for v in [*previous.values(), *actual.values()])
            and all(previous[k] == actual[k] for k in previous if k != 'ExecStart')
            and normal20(terminal) and isinstance(actor, dict)
            and set(actor) == {'pid', 'ticks', 'invocation', 'zeroCapabilities'}
            and isinstance(actor['pid'], str) and re.fullmatch('[1-9][0-9]*', actor['pid'])
            and isinstance(actor['ticks'], str) and re.fullmatch('[1-9][0-9]*', actor['ticks'])
            and actor['invocation'] == terminal['InvocationID'] and actor['zeroCapabilities'] is True
            and isinstance(start, str) and isinstance(end, str)
            and start not in ('', 'n/a') and end not in ('', 'n/a')):
        return False
    old, new = record(previous['ExecStart']), record(actual['ExecStart'])
    return (old is not None and new is not None and old[:3] == new[:3]
            and old[3:] == ('n/a', 'n/a', '0', '(null)', '0/0')
            and new[3:] == (start, end, actor['pid'], 'exited', '20'))
