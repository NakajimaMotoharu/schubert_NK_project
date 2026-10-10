"""Fresh actual same-active parent binding to unchanged independent PID1 oracle."""
import ast
import inspect
import pg1116_current_receipt as previous

CURRENT = {'boot': 'cbca87383b244090b77cbf029677cdd6',
           'invocation': 'a14cc600a4fd4f2e9d8c4731ad9d754b',
           'job': '81093', 'start': 51172132518}


def source():
    s = inspect.getsource(previous)
    for old, new in [('21f20c0cdbe34ce99431a55b10f92285', CURRENT['invocation']),
                     ("'36002'", "'81093'"), ('34658346852', '51172132518')]:
        if old not in s:raise ValueError('fixed fresh parent binding refused')
        s = s.replace(old, new)
    ast.parse(s);return s


_env = {'__name__': 'fresh_resume_receipt', '__file__': __file__}
exec(compile(source(), '<fresh actual parent receipt>', 'exec'), _env)
qualify = _env['qualify']
