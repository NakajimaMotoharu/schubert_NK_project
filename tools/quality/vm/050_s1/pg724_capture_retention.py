"""Readonly current PG722 Backup post; fixed source and original PID1 budget."""
from pathlib import Path
from pg724_retention_sources import bind, capture, oracle

R = Path(__file__).resolve().parent


def source():
    raw = bind((R/'pg692_capture_retention.py').read_text())
    return raw.replace('from pg724_retention_sources import capture,oracle','')


if __name__ == '__main__':
    exec(compile(source(),'<independent current Backup post>','exec'),
         {'__file__':str(R/'pg724_capture_retention.py'),'__name__':'__main__','capture':capture,'oracle':oracle})
