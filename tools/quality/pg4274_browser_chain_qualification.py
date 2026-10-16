"""Affected eight tool tests, full generated guard/composite and reader static closure."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
from pyflakes.api import check,checkPath
import pg4260_stable_admission_image as admission
import pg4270_current_same_owner_browser as browser
import pg4272_current_browser_composite as composite
import pg4276_current_parent_cost_read as cost
from pg1446_current_cold_stage import W

SLOT='pg4274-browser-chain-qualification-v1'


def main():
    os.umask(0o077);out=W/SLOT;out.mkdir(mode=0o700)
    r=subprocess.run(['python3','-B','-m','unittest','pg4250_current_admission_image_test','pg4260_stable_admission_image_test','pg4270_current_browser_chain_test','-v'],capture_output=True)
    log=r.stdout+r.stderr;(out/'host-tests.log').write_bytes(log)
    if r.returncode or b'Ran 8 tests'not in log or not log.rstrip().endswith(b'OK'):raise ValueError('all affected8 FES0 required')
    b=admission.live();raw=composite.root.seal_payload(b,admission.before())
    chain={'before':{'history':[{'source':'4856b3fcaeb4cae983d77757a38dc0bf56a693e2'}]},'after':{},'context':{}}
    seal={'actualExit':0,'productionSource':admission.SOURCE,'observedOwned':{}}
    terminal={'actualExit':0,'productionSource':admission.SOURCE,'genuineParentDone':True,'proofHashes':{'done.private':'a'*64}}
    emitted={'composite-fixture':composite.compose(raw,chain,'b'*64),'browser-guard-fixture':browser.previous.guard(seal,terminal,b),'root-cost-reader':cost.payload({})}
    paths=sorted(Path('tools/quality').glob('pg427*.py'))
    n=sum(checkPath(str(p))for p in paths)+sum(check(raw,'<whole '+name+'>')for name,raw in emitted.items())
    if n:raise ValueError('all generated/host static0 required')
    value={'actualExit':0,'source':admission.SOURCE,'toolTests':8,'failures':0,'errors':0,'skipped':0,'staticFindings':0,
      'hostSha256':{str(p):hashlib.sha256(p.read_bytes()).hexdigest()for p in paths},'emittedFixtureSha256':{k:hashlib.sha256(v.encode()).hexdigest()for k,v in emitted.items()},
      'logSha256':hashlib.sha256(log).hexdigest(),'actualBrowserNotRun':True,'fixtureNotAcceptance':True,'formalAccepted':False,'productionPtAdded':0,'rootActions':0}
    (out/'manifest.safe.json').write_text(json.dumps(value,sort_keys=True));print(json.dumps(value));return 0


if __name__=='__main__':raise SystemExit(main())
