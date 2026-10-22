"""Own public request IO boundaries and related ABI/domain, never actual Backup or VM work."""
import argparse
import json
import subprocess
import finite_selected_profile as profile
from pg5940_private_lock_compile import ROOT,W,BASE
from pg6054_expiry_read_qualification import qualify

OLD='c45cd204ba1b049f39219ce58a1684ba9b07d9a6'
TEST='src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/file/BackupRequestReadBoundaryTest.java'
SLOT='pg6744-request-read-selected-v1'
EXPECTED=(47,11)


def inventory():
    return profile.inventory({'batch':{'batch.file.BackupRequestReadBoundaryTest','batch.file.BackupWorkerRequestFilesTest'},
      'bootstrap':{'bootstrap.SystemdBinderAbiTest','bootstrap.LinuxSystemdSessionTest'}},EXPECTED)


def guard(source):
    changed=set(subprocess.check_output(['git','diff','--name-only',OLD,source,'--','src'],cwd=ROOT,text=True).splitlines())
    if changed!={TEST}:raise ValueError('one new independent Test, all Main and prior oracles byte-fixed')
    if subprocess.check_output(['git','diff',OLD,source,'--','pom.xml','.mvn','mvnw','tools/quality/static','program/characterization'],cwd=ROOT):
        raise ValueError('all gates/Current fixed')


def read_original():
    run=W/SLOT;source=json.loads((run/'begin.safe.json').read_bytes())['source'];guard(source)
    cases,_=inventory()
    return qualify(source,run,cases,EXPECTED,set(),
      BASE/'PG6724-broker-observer-qualification-v1/manifest.json',
      '70670e2540807bf2c8357d285d50c9aa0a19434b04406cfab8b344ef4dae2fd6',
      W/'pg6724-broker-observer-qualification-v1/manifest.safe.json',
      W/'pg6724-broker-observer-qualification-v1/findings.safe.json',
      'pg6746-request-read-original-v1','PG6746-request-read-original-v1',expected_phase_exits=(0,0,0))


def main():
    p=argparse.ArgumentParser();p.add_argument('action',choices=('run','read'));action=p.parse_args().action
    if action=='read':return read_original()
    cases,counts=inventory()
    return profile.execute(SLOT,guard,cases,counts,EXPECTED,{'batch':['batch/file/BackupWorkerRequestFiles'],
      'bootstrap':['bootstrap/LinuxSystemdSession$Native']})


if __name__=='__main__':main()
