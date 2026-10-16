"""Affected three owned tool tests; reuse unchanged eight-test qualification, no VM action."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
from pyflakes.api import checkPath
import pg4282_current_owned_sources as role
from pg1446_current_cold_stage import W

SLOT='pg4290-current-owned-qualification-v1'


def main():
    os.umask(0o077);out=W/SLOT;out.mkdir(mode=0o700)
    prior=json.loads((W/'pg4274-browser-chain-qualification-v1/manifest.safe.json').read_bytes())
    if prior['actualExit']!=0 or prior['source']!=role.SOURCE or prior['toolTests']!=8:raise ValueError('actual affected prerequisite first')
    for p,h in prior['hostSha256'].items():
        if hashlib.sha256(Path(p).read_bytes()).hexdigest()!=h:raise ValueError('unchanged eight-test source first')
    r=subprocess.run(['python3','-B','-m','unittest','pg4282_current_owned_sources_test','-v'],capture_output=True)
    log=r.stdout+r.stderr;(out/'host-tests.log').write_bytes(log)
    if r.returncode or b'Ran 3 tests'not in log or not log.rstrip().endswith(b'OK'):raise ValueError('affected3 FES0 first')
    paths=sorted(Path('tools/quality').glob('pg428*.py'))+[Path(__file__)]
    if sum(checkPath(str(p))for p in paths):raise ValueError('all affected host static0 required')
    value={'actualExit':0,'source':role.SOURCE,'toolTests':3,'failures':0,'errors':0,'skipped':0,'staticFindings':0,
           'unchangedPrerequisiteTests':8,'priorManifestSha256':hashlib.sha256((W/'pg4274-browser-chain-qualification-v1/manifest.safe.json').read_bytes()).hexdigest(),
           'fixtureFiles':15,'fixturePython':11,'fixtureJava':4,'fullPythonClosureAndRealDispatchNamespaceChecked':True,
           'hostSha256':{str(p):hashlib.sha256(p.read_bytes()).hexdigest()for p in paths},'logSha256':hashlib.sha256(log).hexdigest(),
           'actualContextNotYetAccepted':True,'actualABICompiled':False,'stageIssued':False,'stopIssued':False,'independentPostRun':False,
           'formalAccepted':False,'productionPtAdded':0,'fixtureIsNotAuthority':True}
    (out/'manifest.safe.json').write_text(json.dumps(value,sort_keys=True));print(json.dumps(value));return 0


if __name__=='__main__':raise SystemExit(main())
