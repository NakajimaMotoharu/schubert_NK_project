"""Unused signed750 only; currentPG715/nine private ADMIN trees protected unchanged."""
from pathlib import Path
from pg752_sources import bind
from pg718_stage_candidate import source as previous
from pg662_sources import replace

R=Path(__file__).resolve().parent


def source():
    return replace(bind(previous()),(
        ('pg718','pg754'),('PG718','PG754'),('pg715-release-v1','pg750-release-v1'),
        ('pg715-manifest.sig','pg750-manifest.sig'),('pg715-manifest-v1.sig','pg750-manifest-v1.sig'),
        ("'/var/lib/pgpt-s1-preservation/pg702-bootstrap-existing-v1'",
         "'/var/lib/pgpt-s1-preservation/pg702-bootstrap-existing-v1','/var/lib/pgpt-s1-preservation/pg737-bootstrap-tools-v1','/var/lib/pgpt-s1-preservation/pg737-bootstrap-verify-v1','/var/lib/pgpt-s1-preservation/pg737-bootstrap-existing-v1'"),
    ))


if __name__=='__main__':
    env={'__file__':str(R/'pg754_stage_candidate.py'),'__name__':'unused_signed750_only'}
    exec(compile(source(),'<unused signed750 current preserved>','exec'),env);env['main']()
