"""Same current D5 parent CHR-A01, untouched Current oracle/DIF001 only."""
import ast
from pg961_current_a01 import code as previous


def code():
    s = previous()
    changes = [('PG961', 'PG1189'), ('pg961', 'pg1189'), ('pg956', 'pg1183'),
               ('cc9ed874-7f4f-450e-a188-8de1e42c8441', 'cbca8738-3b24-4090-b77c-bf029677cdd6'),
               ('pg957-ordinary-once-v1', 'pg1184-canonical-resume-once-v1'),
               ('pg954-ordinary-before-v1', 'pg1182-canonical-runtime-post-v1'),
               ('40ef6e894573d2ffab1d1732124960f9c98d5f97', 'd5b00104280028d9ea81b44c1d1c805f3c2861ed'),
               ('b75e8bd539edf40d1324896a16e51842d00a3983ba1eae661c86ab68d4692524', '0b617d455553f89cb15043ea9555c4d81ddf3e1dc27176af62e5f50ba8931b0d'),
               ('0.1.0-PG932', '0.1.0-PG1068')]
    for old, new in changes:
        if old not in s:raise ValueError('actual current A01 binding refused')
        s = s.replace(old, new)
    old = "assert (W/'pg1184-canonical-resume-once-v1.exit').read_bytes()==b'0\\n'"
    if s.count(old) != 1:raise ValueError('fixed actual once record required')
    s = s.replace(old, "assert json.loads((W/'pg1184-canonical-resume-once-v1.safe.json').read_bytes())['actualExit']==0")
    old = "root=pathlib.Path('/var/lib/pgpt-s1-preservation/pg1184-canonical-resume-once-v1')"
    if s.count(old) != 1:raise ValueError('fixed canonical original namespace required')
    s = s.replace(old, "root=pathlib.Path('/var/lib/pgpt-s1-preservation/pg1106-ordinary-cold-before-v1/proven-nested-once-v1/canonical-resume-once-v1')")
    s = s.replace("assert time.monotonic_ns()//1000", "assert m['MainPID']==issued['MainPID']=='430851'and m['InvocationID']=='a14cc600a4fd4f2e9d8c4731ad9d754b'\nassert time.monotonic_ns()//1000")
    ast.parse(s);return s


if __name__ == '__main__':
    env = {'__file__': __file__, '__name__': 'current_resume_A01'}
    exec(compile(code(), '<current same-active D5 A01>', 'exec'), env);env['main']()
