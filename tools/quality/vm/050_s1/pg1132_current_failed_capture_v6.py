"""New-only complete failed capture with independent stable journal projection."""
import ast
import inspect
import pg1120_current_failed_capture as transport
from pg1130_current_failed_capture_v5 import payload as previous
import pg1131_journal_stable_projection as journal


def payload():
    raw = previous().replace('failed-capture-v5', 'failed-capture-v6')
    marker = "native=tree(pathlib.Path('/run/schubert-nk/pt-coverage'))"
    if raw.count(marker) != 1: raise ValueError('fixed journal projection insertion refused')
    raw = raw.replace(marker, "JOURNAL_READS.append(journals)\n journals={u:journal.project(bytes.fromhex(value)).hex()for u,value in journals.items()}\n " + marker)
    marker = "shutil.copytree('/run/schubert-nk/pt-coverage',SAVE/'native-after',symlinks=False)"
    if raw.count(marker) != 1: raise ValueError('fixed raw journal preservation insertion refused')
    raw = raw.replace(marker, marker + "\n with(SAVE/'journals-before.private.json').open('x')as f:os.fchmod(f.fileno(),0o600);json.dump(JOURNAL_READS,f,sort_keys=True);f.flush();os.fsync(f.fileno())")
    marker = 'finally:\n for u in reversed(refs)'
    if raw.count(marker) != 1: raise ValueError('fixed final raw journal preservation insertion refused')
    raw = raw.replace(marker, " with(SAVE/'journals-after.private.json').open('x')as f:os.fchmod(f.fileno(),0o600);json.dump(JOURNAL_READS,f,sort_keys=True);f.flush();os.fsync(f.fileno())\n" + marker)
    raw = "import types\njournal=types.ModuleType('independent-journal')\nexec(" + repr(inspect.getsource(journal)) + ",journal.__dict__)\nJOURNAL_READS=[]\n" + raw
    ast.parse(raw); return raw


def main():
    raw = inspect.getsource(transport.main)
    raw = raw.replace('pg1120-current-failed-capture-v1', 'pg1132-current-failed-capture-v6')
    raw = raw.replace('PG1120-current-failed-capture-v1', 'PG1132-current-failed-capture-v6')
    env = dict(transport.__dict__); env['PAYLOAD'] = payload()
    exec(compile(raw, '<new-only stable journal failed capture>', 'exec'), env)
    return env['main']()


if __name__ == '__main__': raise SystemExit(main())
