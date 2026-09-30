"""Preserve the real failed full regression before any target is regenerated."""
import pathlib,json,hashlib,xml.etree.ElementTree as E,datetime
repo=pathlib.Path('/home/mini/codex/project1/work/pgpt-foundation')
out=repo/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG385-six-failed-node-path'
out.mkdir(exist_ok=False)
modules={}
for name in ['protocol','storage','bootstrap','api','web']:
    suites=[E.parse(p).getroot() for p in (repo/f'src/schubert-nk-{name}/target/surefire-reports').glob('TEST-*.xml')]
    modules[name]={k:sum(int(s.get(k)) for s in suites) for k in ['tests','failures','errors','skipped']}
assert modules['web']['errors']==2
log=pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379/pg385-six-provisional.log')
manifest={'id':'PG385-six-failed-node-path','formal':False,'result':'FAILED','sourceCommit':'a6b5c7c8b021c4b391b3af90572eab5d0eac8ab1','branch':'dev-foundation','executionTime':datetime.datetime.now(datetime.timezone.utc).isoformat(),'exitCode':1,'modules':modules,'batch':'NOT-RUN in this reactor; old selected target is not full-run evidence','expected':'all6 F/E/S0 with fixed Node24.19.0','actual':'Web LogSearchScriptTest/ScenarioSearchScriptTest IOException: node unavailable; operator PATH incorrectly named node-24.19.0 instead of actual node-v24.19.0','log':{'path':str(log),'sha256':hashlib.sha256(log.read_bytes()).hexdigest()},'coverage':'incomplete/not accepted','bugs':'environment command error, no Production oracle/source change','redaction':'counts and allowlisted environment facts only; no raw XML/log/private values'}
(out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print(manifest['modules'])
