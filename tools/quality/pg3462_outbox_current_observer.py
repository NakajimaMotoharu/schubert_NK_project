"""New immutable read-only observer for actual published4856, no start/stop authority."""
import pg2682_operation_current_observer as old
import pg3450_current_outbox_publication_sources as role
from pg1446_current_cold_stage import P
from pg1674_critical_management_gate import management_gate

SOURCE = role.production()
BOM = role.ro.role.BOM


def source():
    raw = old.source(BOM)
    for a, b in [('pg2682', 'pg3462'), ('PG2682', 'PG3462'), (old.SOURCE, SOURCE),
                 ('PG2654', 'PG3420'),
                 ('b2d6f605-61cf-425f-8fbd-12d606f6ee66', role.BOOT),
                 ('pg2680-operation-publication-post-v1', 'pg3458-current-outbox-publication-independent-post-v1')]:
        if a not in raw:
            raise ValueError('complete new immutable observer role: ' + a)
        raw = raw.replace(a, b)
    compile(raw, '<immutable actual current4856 observer>', 'exec')
    return raw


def namespace():
    namespace = {'__file__': str(old.previous.previous.R / 'pg3462_outbox_current_observer.py'),
                 '__name__': 'outbox_current_readonly_observer'}
    exec(compile(source(), '<current4856 immutable observer namespace>', 'exec'), namespace)
    return namespace


def main():
    import sys
    ns = namespace()
    if sys.argv[1:] == ['stage']:
        with management_gate(P / 'current-management-critical.lock'):
            return ns['main']()
    return ns['main']()


if __name__ == '__main__':
    main()
