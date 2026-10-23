"""Independently compare the PT TSV to canonical SS351, never to Production methods."""
import datetime
import hashlib
import json
import os
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SS = 'documents/300_SS/350_運用・品質/351_Log・metric・alert・error code設計.md'
FIXTURE = 'src/schubert-nk-batch/src/test/resources/monitoring/metric-catalog.tsv'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def main():
    canonical = subprocess.check_output(['git','show','origin/main:'+SS],cwd=ROOT)
    if canonical != (ROOT/SS).read_bytes():
        raise ValueError('current SS must equal canonical main')
    section = canonical.decode().split('## 6. Metric catalog\n',1)[1].split('## 7.',1)[0]
    rows = {}
    for line in section.splitlines():
        if not line.startswith('| `nk_'):
            continue
        cells = line.split('|')
        for name in re.findall(r'`(nk_[a-z0-9_]+)`',cells[1]):
            if name in rows:
                raise ValueError('duplicate canonical metric')
            rows[name] = dict(type=cells[2].strip(),labels=sorted(k.strip() for k in cells[3].split(',')))
    fixture_raw = (ROOT/FIXTURE).read_bytes()
    fixture = {}
    for line in fixture_raw.decode().splitlines():
        name, kind, labels = line.split('\t')
        if name in fixture:
            raise ValueError('duplicate independent fixture metric')
        fixture[name] = dict(type=kind,labels=sorted(labels.split(',')))
    if len(rows)!=26 or rows!=fixture or 'bucket .05/.1/.25/.5/1/1.5/2/2.5/5' not in section:
        raise ValueError('independent fixture and canonical SS contract differ')
    value = dict(actualExit=0,timeUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
      command='python3 -B tools/quality/pg7016_metric_oracle_audit.py',toolSha256=sha(Path(__file__).read_bytes()),
      canonicalMain=subprocess.check_output(['git','rev-parse','origin/main'],cwd=ROOT,text=True).strip(),
      source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
      design=dict(path=SS,sha256=sha(canonical)),fixture=dict(path=FIXTURE,sha256=sha(fixture_raw)),
      matchedMetrics=26,matchedTypeAndLabelSets=26,expectedHttpBucketLiteral='.05/.1/.25/.5/1/1.5/2/2.5/5',
      productionMethodUsedForExpected=False,executedTests=0,newAccepted=0,formalUpdated=False)
    out = ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG7016-metric-oracle-audit-v1'
    os.umask(0o077);out.mkdir()
    with (out/'manifest.json').open('x') as stream:
        json.dump(value,stream,ensure_ascii=False,sort_keys=True,indent=2)
        stream.write('\n');stream.flush();os.fsync(stream.fileno())
    print(json.dumps(dict(actualExit=0,matched=26,manifestSha256=sha((out/'manifest.json').read_bytes()))))


if __name__ == '__main__':
    main()
