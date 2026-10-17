"""Allowlisted current static findings only; no logs, report snippets, or secrets."""
import datetime
import hashlib
import json
import os
from lan_server import run
from pg4844_ssc301_302_full import ROOT, W, SOURCE

PUBLIC = ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG4854-current-static-requalified-v1'


def project(rows, result):
    if len(rows) != result['rawFindings'] or result['technicalDispositions'] + result['unclassified'] != len(rows):
        raise ValueError('all exact original raw rows, no removal')
    allowed = ('id', 'path', 'sourceSha256', 'rule', 'priority', 'coordinates', 'disposition', 'qualityGatePass', 'rawWarningRemoved')
    values = []
    for row in rows:
        if row['qualityGatePass'] is not False or row['rawWarningRemoved'] is not False:
            raise ValueError('not a quality acceptance or suppressed warning')
        item = {k: row[k] for k in allowed}
        item['messageSha256'] = hashlib.sha256(row['message'].encode()).hexdigest()
        witnesses = row.get('currentAssessmentProof', {}).get('currentOwningTests', [])
        item['owningWitnesses'] = [{k: w[k] for k in ('testId', 'testSourceSha256', 'currentXmlSha256')} for w in witnesses]
        values.append(item)
    return values


def main():
    static = json.loads((W/'pg4856-static-completion-v1/manifest.safe.json').read_bytes())
    outer = json.loads((W/'pg4854-current-static-requalified-v1/manifest.safe.json').read_bytes())
    if not (static['actualExit'] == outer['actualExit'] == 0 and static['productionSource'] == outer['source'] == SOURCE):
        raise ValueError('actual same-source static and independent classification first')
    result = outer['result']; path = '/home/mini/schubert-nk-pgpt/runs/PG4854-current-static-requalified-v1/all-findings.safe.json'
    command = 'python3 -c '+__import__('shlex').quote('import pathlib,hashlib; p=pathlib.Path('+repr(path)+'); v=p.read_bytes(); assert hashlib.sha256(v).hexdigest()=='+repr(result['allFindingsSha256'])+'; print(v.decode())')
    rc, output = run(command, timeout=30)
    if rc != 0: raise ValueError('exact saved row retrieval only')
    rows = json.loads(next(x for x in output.splitlines() if x.startswith('[')))
    values = project(rows, result)
    payload = (json.dumps(values, ensure_ascii=False, indent=2)+'\n').encode()
    os.umask(0o077); PUBLIC.mkdir(parents=True)
    with (PUBLIC/'findings.json').open('xb') as f: f.write(payload); f.flush(); os.fsync(f.fileno())
    value = {'actualExit': 0, 'productionSource': SOURCE, 'kind': 'TECHNICAL_DIAGNOSTIC_NOT_F03_ACCEPTANCE',
             'rawFindings': result['rawFindings'], 'technicalDispositions': result['technicalDispositions'],
             'unclassified': result['unclassified'], 'dispositions': result['dispositions'],
             'held': result['historicalNonContextHeld'], 'files': {'findings.json': hashlib.sha256(payload).hexdigest()},
             'pmd': static['result']['pmd'], 'checkstyle': static['result']['checkstyle'],
             'originalFailure': static['result']['recoveredOriginalFailure'],
             'sourceReports': {'static': static['result']['serverManifestSha256'], 'classification': result['serverManifestSha256'], 'originalRows': result['allFindingsSha256']},
             'rulesSuppressed': False, 'F03Accepted': False, 'formalAccepted': False, 'acceptedLeafDelta': 0,
             'pmdReissued': False, 'vmActions': 0, 'rawLogsReportSnippetsPropertiesExported': False,
             'recordedUTC': datetime.datetime.now(datetime.timezone.utc).isoformat()}
    raw = (json.dumps(value, ensure_ascii=False, indent=2)+'\n').encode()
    with (PUBLIC/'manifest.json').open('xb') as f: f.write(raw); f.flush(); os.fsync(f.fileno())
    print(json.dumps({'actualExit': 0, 'manifestSha256': hashlib.sha256(raw).hexdigest(), 'rows': len(values)})); return 0


if __name__ == '__main__': raise SystemExit(main())
