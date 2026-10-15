"""New-only immutable observer admitted by the complete PG3106 finite post."""
import pg2982_current_resume_observer as previous
from pg1446_current_cold_stage import P
from pg1674_critical_management_gate import management_gate

SOURCE = previous.SOURCE
BOM = previous.BOM


def source():
    raw = previous.source().replace('pg2982', 'pg3120').replace('PG2982', 'PG3120')
    raw = raw.replace('pg2980-scoped-resume-independent-post-v1', 'pg3106-full-native-resume-independent-post-v1')
    compile(raw, '<complete finite post new observer>', 'exec')
    return raw


def namespace():
    ns = {'__file__': str(previous.R / 'pg3120_prepared_browser_observer.py'), '__name__': 'prepared_browser_observer'}
    exec(compile(source(), '<new immutable browser cohort observer>', 'exec'), ns)
    return ns


def main():
    import sys
    ns = namespace()
    if sys.argv[1:] == ['stage']:
        with management_gate(P / 'current-management-critical.lock'):
            ns['main']()
    else:
        ns['main']()


if __name__ == '__main__':
    main()
