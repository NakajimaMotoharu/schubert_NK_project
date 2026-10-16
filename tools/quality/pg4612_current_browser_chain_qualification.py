"""Affected seven host/oracle tests, static closure; no live Browser/login/DB preflight."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
from pyflakes.api import check,checkPath
import pg4584_current_admission_image as admission
import pg4586_current_independent_acceptance as root
import pg4604_current_same_owner_browser as browser
import pg4606_current_browser_composite as composite
import pg4610_current_parent_progress_read as progress
from pg1446_current_cold_stage import W

SLOT='pg4612-current-browser-chain-qualification-v1'


def main():
    os.umask(0o077);out=W/SLOT;out.mkdir(mode=0o700)
    with(out/'tests.private.log').open('xb')as log:
        r=subprocess.run(['python3','-B','-m','unittest','pg4584_current_acceptance_test','pg4608_current_browser_chain_test'],stdout=log,stderr=log)
    log=(out/'tests.private.log').read_bytes()
    if r.returncode!=0 or b'Ran 7 tests'not in log or not log.rstrip().endswith(b'OK'):raise ValueError('original seven independent tests0/no skip')
    b=admission.live();raw=root.seal_payload(b,admission.before())
    chain={'before':{'history':[{'source':'7bb25aa9c8a1d1af04525ec51beb1c4b7268aa9e'}]},'after':{},'context':{}}
    seal={'actualExit':0,'productionSource':admission.SOURCE,'observedOwned':{}}
    term={'actualExit':0,'productionSource':admission.SOURCE,'genuineParentDone':True,'proofHashes':{'done.private':'a'*64}}
    from types import FunctionType
    fn=FunctionType(browser.previous.previous.guard.__code__,{**vars(browser.previous.previous),'SOURCE':admission.SOURCE,'BOM':admission.BOM})
    emitted={'composite-fixture':composite.compose(raw,chain,'b'*64),'browser-guard-fixture':admission.entry.observer.bind(fn(seal,term,b)),'parent-progress':progress.payload({})}
    paths=[Path('tools/quality')/name for name in ['pg4584_current_admission_image.py','pg4584_current_acceptance_test.py','pg4586_current_independent_acceptance.py','pg4602_current_browser_ready.py','pg4604_current_same_owner_browser.py','pg4606_current_browser_composite.py','pg4608_current_browser_chain_test.py','pg4610_current_parent_progress_read.py','pg4612_current_browser_chain_qualification.py']]
    findings=sum(checkPath(str(p))for p in paths)+sum(check(raw,'<'+name+'>')for name,raw in emitted.items())
    if findings:raise ValueError('all actual host/emitted static0')
    v={'actualExit':0,'source':admission.SOURCE,'toolTests':7,'failures':0,'errors':0,'skipped':0,'staticFindings':0,'hostSha256':{str(p):hashlib.sha256(p.read_bytes()).hexdigest()for p in paths},
      'emittedFixtureSha256':{k:hashlib.sha256(v.encode()).hexdigest()for k,v in emitted.items()},'logSha256':hashlib.sha256(log).hexdigest(),'liveBrowserNotRun':True,'fixtureNotAcceptance':True,'formalAccepted':False,'productionPtAdded':0,'rootActions':0}
    (out/'manifest.safe.json').write_text(json.dumps(v,sort_keys=True));print(json.dumps({k:v for k,v in v.items()if k!='hostSha256'}));return 0


if __name__=='__main__':raise SystemExit(main())
