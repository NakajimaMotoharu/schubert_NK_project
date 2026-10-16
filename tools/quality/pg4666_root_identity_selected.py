"""Fixed selected independent identity tests and actual method counters; no VM actions."""
import inspect
import subprocess
import pg4412_shared_manager_selected as previous

WORK=previous.ROOT.parent/'pgpt-runs/PG379/pg4666-root-self-identity-selected-v1'
PACKAGE='dev.codex.schubert.nk.batch.file.'
TESTS=[PACKAGE+n for n in ['RootStartupPendingTest','StartupLaunchRecordTest','MorningStartupLaunchOwnerAdmissionTest']]


def main():
    if subprocess.check_output(['git','status','--porcelain']):raise ValueError('clean frozen test snapshot first')
    head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
    raw=inspect.getsource(previous.main)
    first=raw.index("                if entry.get('name') in [")
    last=raw.index(':\n                    counters[entry.get',first)
    raw=raw[:first]+"                if entry.get('name') == 'dev/codex/schubert/nk/batch/file/RootStartupPending'"+raw[last:]
    raw=raw.replace("'sourceRole': 'unaccepted candidate; deployed source remains7bb'","'sourceRole': 'test-only snapshot; deployed Main964e unchanged and ordinary Units stopped'")
    ns={**vars(previous),'SOURCE':head,'WORK':WORK,'TESTS':TESTS}
    exec(compile(raw,'<selected independent Root self identity suite>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
