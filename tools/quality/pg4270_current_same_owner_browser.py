"""Existing twelve real-browser oracles on this genuine fresh Root's four owners."""
import datetime
import hashlib
import json
import os
import subprocess
import sys
import pg4036_literal_invariant_browser_actual as previous
import pg4029_literal_invariant_browser_ready_serial as ready
import pg4252_current_independent_acceptance as accepted
from pg4260_stable_admission_image import live,SOURCE
from pg1446_current_cold_stage import W,P,SSH
from pg1674_critical_management_gate import management_gate

SLOT='pg4270-current-same-owner-browser-v1'


def receipt(slot):
    value=json.loads((W/slot/'manifest.safe.json').read_bytes())
    if value['actualExit']!=0 or value['source']!=SOURCE or type(value.get('result'))is not dict:raise ValueError('actual current phase receipt required')
    return {**value['result'],'actualExit':value['actualExit'],'productionSource':value['source']}


def guard():
    seal,term=receipt(accepted.SEAL),receipt(accepted.TERM)
    if not seal['genuineCompletion']['genuineRootDone'] or seal['genuineCompletion']['completionCode']!=term['completionCode']:raise ValueError('same genuine terminal/seal required')
    return previous.guard(seal,term,live())


def main():
    if subprocess.check_output(['git','status','--porcelain']):raise ValueError('clean fixed Browser operator required')
    ready.require_ready();raw=guard()
    os.umask(0o077);out=W/SLOT;out.mkdir(mode=0o700);(out/'guard.private.py').write_text(raw)
    operator=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip();start=datetime.datetime.now(datetime.timezone.utc).isoformat()
    before_socks=previous.previous.owned_socks()
    with management_gate(P/'current-management-critical.lock'):
        before=subprocess.check_output(SSH+['sudo','-n','python3','-B','-'],input=raw.encode(),timeout=25)
        env={**os.environ,'PLAYWRIGHT_BROWSERS_PATH':'/home/mini/codex/project1/work/characterization-tools/playwright-browsers',
             'PLAYWRIGHT_HOST_PLATFORM_OVERRIDE':'ubuntu24.04-x64','LD_LIBRARY_PATH':'/home/mini/codex/project1/work/characterization-tools/root/usr/lib/x86_64-linux-gnu'}
        shared=ready.previous.previous.previous
        command=[str(shared.JAVA/'java'),'-cp',shared.classpath(W/ready.SLOT/'classes'),'dev.codex.schubert.characterization.NativeNkBrowserBusinessCohort','run',str(out/'cases')]
        with(out/'browser.private.log').open('xb')as log:r=subprocess.run(command,stdout=log,stderr=log,env=env,timeout=600)
        after=subprocess.check_output(SSH+['sudo','-n','python3','-B','-'],input=raw.encode(),timeout=25)
    same=json.loads(before)==json.loads(after)and before_socks==previous.previous.owned_socks()
    codes=[r.returncode]
    if not r.returncode:
        with(out/'all24.private.log').open('xb')as log:
            post=subprocess.run([sys.executable,'-B','tools/quality/pg3136_browser_rows_oracle.py',str(out/'cases/before-rows.private.json'),str(out/'cases/after-rows.private.json'),str(out/'cases/context.private.json')],stdout=log,stderr=log,timeout=30)
        codes.append(post.returncode)
    qualified=operator==subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()and not subprocess.check_output(['git','status','--porcelain'])
    value={'actualExit':next((c for c in codes if c),0),'phaseExits':codes,'operatorSource':operator,'productionSource':SOURCE,'sourceQualified':qualified,
           'guardSha256':hashlib.sha256(raw.encode()).hexdigest(),'sameFourOrdinaryOwnersBeforeAfter':same,'sameSocksBeforeAfter':same,
           'independentNormalTlsBeforeAfter':json.loads(before)['tls'],'sharedCurrentBrowserIgnoreHttpsErrors':True,'browserStandardTrustStoreQualified':False,
           'plannedCases':12,'passedCases':len(list((out/'cases').glob('PT-NBR-*.safe.json'))),'all24IndependentPost':len(codes)==2 and not any(codes),
           'startedUTC':start,'completedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'formalAccepted':False,'ownedStopIssued':False,'nativeGlobalAccepted':False}
    (out/'manifest.safe.json').write_text(json.dumps(value,sort_keys=True));print(json.dumps(value));return value['actualExit']or(0 if qualified and same else 1)


if __name__=='__main__':raise SystemExit(main())
