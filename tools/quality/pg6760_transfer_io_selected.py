"""Own Transfer temp fixtures only; exact1669 includes two declared nested IO types."""
import argparse
import inspect
import json
import subprocess
import finite_selected_profile as profile
import pg6054_expiry_read_qualification as original
from pg5940_private_lock_compile import ROOT,W,BASE

OLD='bad7b45337d10341e9972cc9b3f7a0b43d21e465'
MAIN='src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/file/TransferCleanup.java'
TEST='src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/file/TransferIoBoundaryTest.java'
ADDED={'batch:dev/codex/schubert/nk/batch/file/TransferCleanup$'+n+'.class' for n in ('Io','NioIo')}
SLOT='pg6764-transfer-io-selected-v2'
EXPECTED=(27,10)


def inventory():
    return profile.inventory({'batch':{'batch.file.TransferIoBoundaryTest','batch.file.TransferCleanupTest','batch.file.TransferCleanupFailureTest'}},EXPECTED)


def guard(source):
    changed=set(subprocess.check_output(['git','diff','--name-only',OLD,source,'--','src'],cwd=ROOT,text=True).splitlines())
    if changed!={MAIN,TEST}:raise ValueError('one Main plus independent Test only, every prior oracle fixed')
    if subprocess.check_output(['git','diff',OLD,source,'--','pom.xml','.mvn','mvnw','tools/quality/static','program/characterization'],cwd=ROOT):raise ValueError('quality/build/Current fixed')


def runner(total,suites,targets):
    raw=profile.runner(total,suites,targets)
    if raw.count('len(physical)==1667')!=1:raise ValueError('one exact prior physical guard')
    raw=raw.replace('len(physical)==1667','len(physical)==1669',1)
    return raw


def qualification_definition():
    raw=inspect.getsource(original.qualify)
    for before,after in (
      ('len(physical) != 1667','len(physical) != 1669 or len(old_physical) != 1667'),
      ('set(physical) != set(old_physical)','set(physical) != set(old_physical) | ADDED'),
      ('physicalMain=1667','physicalMain=1669'),
      ('unchangedPhysical=1667-len(changed)','unchangedPhysical=1669-len(changed)')):
        if raw.count(before)!=1:raise ValueError('exact physical extension binding '+before)
        raw=raw.replace(before,after,1)
    anchor="    for name, value in (('manifest.safe.json', result),"
    if raw.count(anchor)!=1:raise ValueError('one result publication boundary')
    raw=raw.replace(anchor,"    result.update(priorPhysicalMain=1667,addedPhysical=sorted(ADDED),physicalCountChangeReason='two nested Transfer read-only IO types; all old keys retained')\n"+anchor,1)
    scope={**vars(original),'ADDED':ADDED}
    exec(compile(raw,'<Transfer1669 original qualifier>','exec'),scope)
    return scope['qualify']


def read_original():
    run=W/SLOT;source=json.loads((run/'begin.safe.json').read_bytes())['source'];guard(source);cases,_=inventory()
    return qualification_definition()(source,run,cases,EXPECTED,{MAIN},
      BASE/'PG6746-request-read-original-v1/manifest.json','af3dcb55d39916cd4883ddfa37337c92033b60080e6e9c7c44de760a35b1714a',
      W/'pg6746-request-read-original-v1/manifest.safe.json',W/'pg6746-request-read-original-v1/findings.safe.json',
      'pg6766-transfer-io-original-v2','PG6766-transfer-io-original-v2',expected_phase_exits=(0,0,0))


def main():
    p=argparse.ArgumentParser();p.add_argument('action',choices=('run','read'));action=p.parse_args().action
    if action=='read':return read_original()
    cases,counts=inventory();scope={**vars(profile),'runner':runner}
    exec(compile(inspect.getsource(profile.execute),'<exact Transfer1669 finite profile>','exec'),scope)
    return scope['execute'](SLOT,guard,cases,counts,EXPECTED,{'batch':['batch/file/TransferCleanup']})


if __name__=='__main__':main()
