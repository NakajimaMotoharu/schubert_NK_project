"""Readonly current750 Backup post under captured PID1 originalbudget; no start."""
from pathlib import Path
from pg760_retention_sources import bind,capture,oracle
from pg724_capture_retention import source as previous

R=Path(__file__).resolve().parent


def source():return bind(previous())


if __name__=='__main__':
    exec(compile(source(),'<current534 plus ten independently>','exec'),
         {'__file__':str(R/'pg760_capture_retention.py'),'__name__':'__main__','capture':capture,'oracle':oracle})
