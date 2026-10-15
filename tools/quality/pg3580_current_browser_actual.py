"""Current same-four-owner twelve real Browser cases and independent all24 delta."""
import datetime
import hashlib
import json
import os
import subprocess
import sys
import types
from pg1446_current_cold_stage import W,P,SSH
from pg1674_critical_management_gate import management_gate
from pg3564_current_browser_resume_sources import bind,SOURCE
from pg3578_current_browser_ready import require_ready,classpath,JAVA,SLOT as READY
import pg3582_current_browser_acceptance as root
import pg3140_browser_business_actual as template
import pg1191_chr_socks_owner as socks_owner

SLOT='pg3580-current-browser-business-actual-v1'


def guard(seal,terminal,binding):
    fn=template.guard
    return types.FunctionType(fn.__code__,{**fn.__globals__,'SOURCE':SOURCE,'GUARD':bind(template.GUARD)},'current_same_owner_browser_guard')(seal,terminal,binding)


def owned_socks():
    v=json.loads((W/'pg3480-outbox-chr-socks-v1/running.safe.json').read_bytes())
    socks_owner.EXPECTED={'pid':v['pid'],'ticks':v['ticks'],'argvSha256':v['argvSha256'],'executable':'/usr/bin/ssh','ppid':v['parentPid'],'uids':(1000,1000,1000,1000),'gids':(1000,1000,1000,1000),'listenerAddresses':('0100007F:D781',)}
    return socks_owner.require_owner()


def main():
    if subprocess.check_output(['git','status','--porcelain']):raise ValueError('clean fixed Browser operator required')
    require_ready()
    seal=json.loads((W/root.SEAL/'manifest.safe.json').read_bytes());terminal=json.loads((W/root.TERM/'manifest.safe.json').read_bytes())
    raw=guard(seal,terminal,root.live()['binding'])
    os.umask(0o077);out=W/SLOT;out.mkdir(mode=0o700);operator=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip();start=datetime.datetime.now(datetime.timezone.utc).isoformat()
    (out/'guard.private.py').write_text(raw);before_socks=owned_socks()
    with management_gate(P/'current-management-critical.lock'):
        before=subprocess.check_output(SSH+['sudo','-n','python3','-B','-'],input=raw.encode(),timeout=25)
        env={**os.environ,'PLAYWRIGHT_BROWSERS_PATH':'/home/mini/codex/project1/work/characterization-tools/playwright-browsers','PLAYWRIGHT_HOST_PLATFORM_OVERRIDE':'ubuntu24.04-x64','LD_LIBRARY_PATH':'/home/mini/codex/project1/work/characterization-tools/root/usr/lib/x86_64-linux-gnu'}
        command=[str(JAVA/'java'),'-cp',classpath(W/READY/'classes'),'dev.codex.schubert.characterization.NativeNkBrowserBusinessCohort','run',str(out/'cases')]
        with(out/'browser.private.log').open('xb')as log:r=subprocess.run(command,stdout=log,stderr=log,env=env,timeout=600)
        after=subprocess.check_output(SSH+['sudo','-n','python3','-B','-'],input=raw.encode(),timeout=25)
    same=json.loads(before)==json.loads(after)and before_socks==owned_socks()
    codes=[r.returncode]
    if r.returncode==0:
        with(out/'all24.private.log').open('xb')as log:
            actual=subprocess.run([sys.executable,'-B','tools/quality/pg3136_browser_rows_oracle.py',str(out/'cases/before-rows.private.json'),str(out/'cases/after-rows.private.json'),str(out/'cases/context.private.json')],stdout=log,stderr=log,timeout=30)
        codes.append(actual.returncode)
    value={'actualExit':next((c for c in codes if c),0),'phaseExits':codes,'operatorSource':operator,'productionSource':SOURCE,'sourceQualified':operator==subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()and not subprocess.check_output(['git','status','--porcelain']),'guardSha256':hashlib.sha256(raw.encode()).hexdigest(),'sameFourOrdinaryOwnersBeforeAfter':same,'sameSocksBeforeAfter':same,'independentNormalTlsBeforeAfter':json.loads(before)['tls'],'sharedCurrentBrowserIgnoreHttpsErrors':True,'browserStandardTrustStoreQualified':False,'plannedCases':12,'passedCases':len(list((out/'cases').glob('PT-NBR-*.safe.json'))),'all24IndependentPost':len(codes)==2 and not any(codes),'startedUTC':start,'completedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'formalAccepted':False,'ownedStopIssued':False,'nativeGlobalAccepted':False}
    with(out/'manifest.safe.json').open('x')as f:json.dump(value,f,sort_keys=True);f.flush();os.fsync(f.fileno())
    print(json.dumps(value,sort_keys=True));return value['actualExit']or(0 if value['sourceQualified']and same else 1)


if __name__=='__main__':raise SystemExit(main())
