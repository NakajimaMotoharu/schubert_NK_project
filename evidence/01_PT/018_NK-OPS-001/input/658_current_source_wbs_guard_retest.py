"""Retest changed metadata guards only; no production/runtime tests."""
from pathlib import Path
import datetime
import hashlib
import json
import os
import subprocess
import sys

B=Path('evidence/01_PT/018_NK-OPS-001')
O=B/'evidence/PG24172-wbs-current-source-guard-retest-v1'
assert not O.exists()
O.mkdir()
env=dict(os.environ, PYTHONPATH='tools/quality')
stages={}
for name,args,expected in [('metadata-regression',['-m','unittest','wbs_current_source_structure_test','-v'],0),
                           ('current-structure',['tools/quality/wbs_progress_audit.py','--current-source-structure-only'],0),
                           ('full-audit',['tools/quality/wbs_progress_audit.py'],1)]:
    command=[sys.executable,'-B',*args]
    started=datetime.datetime.now().astimezone().isoformat()
    r=subprocess.run(command,capture_output=True,env=env,timeout=90)
    (O/(name+'.stdout')).write_bytes(r.stdout)
    (O/(name+'.stderr')).write_bytes(r.stderr)
    stages[name]=dict(command=command,actualExit=r.returncode,expectedExit=expected,startedAtJST=started,endedAtJST=datetime.datetime.now().astimezone().isoformat())
    assert r.returncode==expected,(name,r.returncode)
assert json.loads((O/'current-structure.stdout').read_bytes())['artifactCount']==1068
assert json.loads((O/'full-audit.stdout').read_bytes())['status']=='HOLD'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
tools=[Path(__file__),Path('tools/quality/wbs_current_source_structure.py'),Path('tools/quality/wbs_current_source_structure_test.py'),Path('tools/quality/wbs_progress_audit.py')]
manifest=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),reason='Changed metadata projection guards and non-mutating independent negative vector; original24162 preserved, not replayed.',stages=stages,metadataRegressionTests=8,projectionNegatives=5,productTestsExecuted=0,newAcceptance=0,formalUpdated=False,effortRate=None,tools={str(p):sha(p) for p in tools},files={p.name:sha(p) for p in O.iterdir()},bugs=['BUG-2518'],ykts=['YKT-2256'])
(O/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(actualExit=0,manifestSha256=sha(O/'manifest.json'),metadataTests=8,productTestsExecuted=0)))
