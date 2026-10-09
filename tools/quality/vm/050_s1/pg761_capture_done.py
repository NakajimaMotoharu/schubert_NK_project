"""Current758 genuine PID1/RootDONE, readonly only; oldcompleted rejected."""
from pathlib import Path
from pg725_capture_done import payload as previous
from pg761_current_binding import bind,receipt

R=Path(__file__).resolve().parent


def payload(run):
    assert run not in {'55ac70e7-0180-4c32-8c91-5a379ebedf24','8633b77f-77dc-4a78-88b4-41165f159b43'}
    return bind(previous(run))


def source():
    raw=(R/'pg725_capture_done.py').read_text()
    start=raw.index('def main():');end=raw.index("if __name__=='__main__':",start)
    imports='import datetime,hashlib,json,os,subprocess\nfrom pathlib import Path\n'
    paths="R=Path(__file__).resolve().parent\nW=Path('/home/mini/codex/project1/work/pgpt-runs/PG379')\nP=Path('/home/mini/codex/project1/work/pgpt-vm/private')\n"
    return imports+paths+bind(raw[start:end])


if __name__=='__main__':
    env={'__file__':str(R/'pg761_capture_done.py'),'__name__':'current758_genuine','payload':payload,'receipt':receipt}
    exec(compile(source(),'<current758 DONE>','exec'),env);env['main']()
