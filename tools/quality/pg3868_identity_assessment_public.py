"""Publish exact source-bound technical assessments, never raw runtime or credentials."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import shlex
from lan_server import run
from pg3798_hygiene_current_observer import SOURCE

ROOT=Path(__file__).resolve().parents[2]
W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379')


def main():
    original=json.loads((W/'pg3864-suppression-identity-review-v1/manifest.safe.json').read_bytes());v=original['result']
    if original['actualExit']!=0 or v['productionSource']!=SOURCE or v['newTechnicalAssessments']!=30 or v['rawFindings']!=1840 or v['technicalDispositions']!=278 or v['unclassified']!=1562 or v['F03Accepted']or v['MainChanged']:raise ValueError('actual narrow thirty identity assessments required')
    code="from pathlib import Path\nimport hashlib,json\np=Path('/home/mini/schubert-nk-pgpt/runs/PG3864-suppression-identity-review-v1/all1840-dispositions.safe.json');raw=p.read_bytes();assert hashlib.sha256(raw).hexdigest()==EXPECTED;print(raw.decode())\n"
    status,text=run('python3 -c '+shlex.quote('EXPECTED='+repr(v['dispositionsSha256'])+'\n'+code),timeout=30)
    if status:raise ValueError('exact safe source metadata read required')
    rows=json.loads(next(line for line in text.splitlines()if line.startswith('[')))
    if len(rows)!=1840 or Counter(r['disposition']for r in rows)!=Counter(v['dispositions']):raise ValueError('all1840 exact partition required')
    selected=[r for r in rows if r['rule']=='CompareObjectsWithEquals']
    if len(selected)!=65 or sum(r['disposition']=='REQUIRED_JDK_SELF_SUPPRESSION_IDENTITY_GUARD'for r in selected)!=30:raise ValueError('thirty assessed plus thirtyfive unresolved required')
    for row in rows:
        path=ROOT/row['path']
        if not path.is_relative_to(ROOT/'src')or hashlib.sha256(path.read_bytes()).hexdigest()!=row['sourceSha256']:raise ValueError('every current source finding hash independently matches')
    for row in selected:
        if row['disposition']=='REQUIRED_JDK_SELF_SUPPRESSION_IDENTITY_GUARD'and(row['qualityGatePass']is not False or row['scope']!='EXACT_LANGUAGE_API_CONTRACT_ONLY_NOT_FUNCTIONAL_GATE'):raise ValueError('no gate promotion')
    out=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG3868-identity-assessment-v1';out.mkdir()
    raw=(json.dumps(selected,ensure_ascii=False,sort_keys=True)+'\n').encode();(out/'all-65-identity-findings.json').write_bytes(raw)
    value={'actualExit':0,'run':'PG3868-identity-assessment-v1','source':SOURCE,'testId':'PT-F03-IDENTITY-3864','originalReceiptSha256':hashlib.sha256((W/'pg3864-suppression-identity-review-v1/manifest.safe.json').read_bytes()).hexdigest(),'technicalAssessment':v,'files':{'all-65-identity-findings.json':hashlib.sha256(raw).hexdigest()},'owningSuitesWithWitnesses':sum(bool(r.get('owningTestIds'))for r in selected if r['disposition']!='UNCLASSIFIED'),'formalAccepted':False,'F03Accepted':False,'applicableViolationCount':None,'suppressionAdded':False,'ruleChanged':False,'newRegressionIssued':False,'vmActions':0}
    raw=(json.dumps(value,ensure_ascii=False,sort_keys=True)+'\n').encode();(out/'manifest.json').write_bytes(raw)
    print(json.dumps({'actualExit':0,'manifestSha256':hashlib.sha256(raw).hexdigest(),'newTechnicalAssessments':30,'technicalDispositions':278,'unclassified':1562,'owningFindingsWithWitnesses':value['owningSuitesWithWitnesses'],'F03Accepted':False}));return 0


if __name__=='__main__':raise SystemExit(main())
