"""Ordinary owned ABI stubs + unchanged local manager domain; no bus/VM/Unit actions."""
import argparse
import json
import subprocess
import finite_selected_profile as profile
from pg5940_private_lock_compile import ROOT,W,BASE,sha
from pg6054_expiry_read_qualification import qualify

OLD='01e41088c6562c3b7d103ae0bacc9f693bc1aad4'
TEST='src/schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/bootstrap/SystemdBinderAbiTest.java'
SLOT='pg6740-systemd-owned-abi-selected-v1'
EXPECTED=(34,9)


def inventory():
    return profile.inventory({'bootstrap':{'bootstrap.SystemdBinderAbiTest','bootstrap.LinuxSystemdSessionTest'}},EXPECTED)


def guard(source):
    changed=set(subprocess.check_output(['git','diff','--name-only',OLD,source,'--','src'],cwd=ROOT,text=True).splitlines())
    if changed!={TEST}:raise ValueError('one independent Test only, all Main/old oracles unchanged')
    if subprocess.check_output(['git','diff',OLD,source,'--','pom.xml','.mvn','mvnw','tools/quality/static','program/characterization'],cwd=ROOT):
        raise ValueError('all gates/Current fixed')
    p=BASE/'PG6738-systemd-abi-source-review-v1/manifest.json'
    if sha(p)!='cd183662b6788bfef569ece4ed1cd3263b497967cbd8af15b0a5f28e9cd95b46':raise ValueError('frozen independent PG review')
    q=json.loads(p.read_bytes())
    if q['actualExit']!=0 or q['productionSource']!=OLD or q['symbols']!=21 or q['sourceSha256']!=sha(ROOT/q['sourcePath']):
        raise ValueError('all21 reviewed ABI and exact unchanged Main')


def read_original():
    run=W/SLOT;source=json.loads((run/'begin.safe.json').read_bytes())['source'];guard(source)
    cases,_=inventory()
    return qualify(source,run,cases,EXPECTED,set(),
      BASE/'PG6724-broker-observer-qualification-v1/manifest.json',
      '70670e2540807bf2c8357d285d50c9aa0a19434b04406cfab8b344ef4dae2fd6',
      W/'pg6724-broker-observer-qualification-v1/manifest.safe.json',
      W/'pg6724-broker-observer-qualification-v1/findings.safe.json',
      'pg6742-systemd-owned-abi-original-v1','PG6742-systemd-owned-abi-original-v1',expected_phase_exits=(0,0,0))


def main():
    p=argparse.ArgumentParser();p.add_argument('action',choices=('run','read'));action=p.parse_args().action
    if action=='read':return read_original()
    cases,counts=inventory()
    return profile.execute(SLOT,guard,cases,counts,EXPECTED,{'bootstrap':['bootstrap/LinuxSystemdSession$Native']})


if __name__=='__main__':main()
