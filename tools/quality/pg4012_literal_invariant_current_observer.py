"""New-source observer only; no business start or stop authority."""
from pathlib import Path
import pg3462_outbox_current_observer as previous
import pg4002_literal_invariant_publication_sources as role
from pg1446_current_cold_stage import P
from pg1674_critical_management_gate import management_gate

SOURCE, BOM, ro = role.SOURCE, role.BOM, role.ro


def source():
    raw = ro.unused.role_text(previous.source()).replace('pg3462', 'pg4012').replace('PG3462', 'PG4012')
    raw = raw.replace('pg3458-current-outbox-publication-independent-post-v1', 'pg4008-literal-invariant-publication-independent-post-v1')
    compile(raw, '<new current7bb observer only>', 'exec')
    return raw


def namespace():
    values = {'__file__': str(Path(__file__).resolve().parent / 'vm/050_s1/pg4012_literal_invariant_current_observer.py'), '__name__': 'new_main_current_readonly_observer'}
    exec(compile(source(), '<new current immutable observer namespace>', 'exec'), values)
    return values


def main():
    import sys
    if sys.argv[1:] == ['stage']:
        with management_gate(P / 'current-management-critical.lock'): return namespace()['main']()
    return namespace()['main']()


if __name__ == '__main__': main()
