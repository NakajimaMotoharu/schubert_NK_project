"""Publish source-coordinate/compiler metadata only, never promote catch facts to disposition."""
import hashlib
import json
from pathlib import Path
import shlex
from lan_server import run
from pg3798_hygiene_current_observer import SOURCE

ROOT=Path(__file__).resolve().parents[2];W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379')


def main():
    original=json.loads((W/'pg3820-catch-context-inventory-v1/manifest.safe.json').read_bytes());result=original['result']
    if original['actualExit']!=0 or result['productionSource']!=SOURCE or result['matchedFindings']!=573 or result['F03Accepted']or result['MainChanged']:raise ValueError('genuine source-bound facts, not accepted classifications, required')
    code="from pathlib import Path\nimport hashlib,json\np=Path('/home/mini/schubert-nk-pgpt/runs/PG3820-catch-context-inventory-v1/joined-facts.safe.json');raw=p.read_bytes();assert hashlib.sha256(raw).hexdigest()==EXPECTED;print(raw.decode())\n"
    status,text=run('python3 -c '+shlex.quote('EXPECTED='+repr(result['factsSha256'])+'\n'+code),timeout=30)
    if status:raise ValueError('exact bounded safe facts read required')
    rows=json.loads(next(line for line in text.splitlines()if line.startswith('[')))
    if len(rows)!=573 or any(set(r)!={'path','rule','beginline','endline','begincolumn','endcolumn','sourceSha256','facts','classification'}or r['classification']!='FACTS_ONLY_NOT_DISPOSITION'for r in rows):raise ValueError('all573 safe fact schema required')
    out=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG3834-catch-facts-v1';out.mkdir()
    raw=(json.dumps(rows,ensure_ascii=False,sort_keys=True)+'\n').encode();(out/'all-573-compiler-facts.json').write_bytes(raw)
    value={'actualExit':0,'run':'PG3834-catch-facts-v1','source':SOURCE,'testId':'PT-F03-CATCH-3820','originalReceiptSha256':hashlib.sha256((W/'pg3820-catch-context-inventory-v1/manifest.safe.json').read_bytes()).hexdigest(),'facts':result,'files':{'all-573-compiler-facts.json':hashlib.sha256(raw).hexdigest()},'formalAccepted':False,'newDispositions':0,'suppressionAdded':False,'ruleChanged':False,'newRegressionIssued':False,'vmActions':0}
    raw=(json.dumps(value,ensure_ascii=False,sort_keys=True)+'\n').encode();(out/'manifest.json').write_bytes(raw)
    print(json.dumps({'actualExit':0,'all573':True,'manifestSha256':hashlib.sha256(raw).hexdigest(),'newDispositions':0,'F03Accepted':False}));return 0


if __name__=='__main__':raise SystemExit(main())
