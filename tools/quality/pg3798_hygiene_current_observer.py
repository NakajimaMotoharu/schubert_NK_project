"""Immutable observer for newly published7fff; no business start/stop authority."""
import pg3462_outbox_current_observer as previous
from pathlib import Path
import pg3788_hygiene_publication_sources as role
from pg1446_current_cold_stage import P
from pg1674_critical_management_gate import management_gate

SOURCE=role.SOURCE;BOM=role.BOM


def source():
    raw=role.mapping.role_text(previous.source()).replace('pg3462','pg3798').replace('PG3462','PG3798').replace('pg3458-current-outbox-publication-independent-post-v1','pg3794-hygiene-publication-independent-post-v1')
    compile(raw,'<new signed source readonly observer>','exec');return raw


def namespace():
    values={'__file__':str(Path(__file__).resolve().parent/'vm/050_s1/pg3798_hygiene_current_observer.py'),'__name__':'hygiene_current_readonly_observer'}
    exec(compile(source(),'<current7fff observer namespace>','exec'),values);return values


def main():
    import sys
    if sys.argv[1:]==['stage']:
        with management_gate(P/'current-management-critical.lock'):return namespace()['main']()
    return namespace()['main']()


if __name__=='__main__':main()
