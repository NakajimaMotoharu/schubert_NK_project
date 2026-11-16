"""Return full Storage25 static proof; retain the other module conditions."""
from pathlib import Path
import datetime
import hashlib
import json
import sys

r = Path.cwd()
sys.path[:0] = [str(r / 'tools/quality'), str(r / 'tools/quality/vm/050_s1')]
import pg998_metrics as metrics
from pmo_quota_binding import digest, end_fields
from source_evidence_binding import bind

d = r / 'documents/400_PGPT/470_PMO/601_WBS66短期実行_20261117'
s = r.parent / 'PMO/pgpt-completion-stage-20261102'
load = lambda p: json.loads(p.read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
first = load(d / '033_F03Storage全25Main群開始.json')
post = r / 'evidence/01_PT/018_NK-OPS-001/evidence/PG36826-storage-main-xml-return-v1/manifest.json'
m = load(post); assert m['actualExit'] == 0
q = load(Path(sys.argv[1])); now = datetime.datetime.now(datetime.timezone.utc).isoformat()
bound = end_fields(first['quota'], q, digest(q), now, m['terminalAtUTC'], 5)
assert not any(x['groupId'] == first['groupId'] and x.get('groupBoundary') == 'END'
               for x in map(json.loads, metrics.EVENTS.read_text().splitlines()))
next_command = ('Continue F03/2-2 current original-POM four-module Main compile for Protocol165/Storage25/'
    'Bootstrap87/Batch200, no Test sources or product initialization, after exact source/ownership '
    'admission. Bootstrap/Batch contain none of QA056 four held types; API/Web classfile operations '
    'remain waiting QA056. This integrated reactor supplies fresh dependency artifacts and actual '
    'compile flags, not a replay of old152/39 successes. No real native/DB/Root execution. Then '
    'individual static scope and P01808 current ordinary contract gaps; do not stop on this return.')
values = dict(bound, source=m['source'], groupBoundary='END',
    sourceEvidenceBinding=bind([(post, sha(post))], m['source']),
    wbsLeafIds=['WBS-F03'], workCategory='CONTRACT_AUDIT',
    workAttributionKind='SOURCE_REQUALIFICATION', managementWorkIds=['WBS-F03/2-2'],
    estimateAtGroupStartPp=first['values']['estimateAtGroupStartPp'], groupCapPp=5,
    completedOriginalRowPricePp=0, remainingOriginalRowPricePp=2.4,
    newAcceptance=0, formalUpdated=False, effortCompletionRate=None,
    criterionReductions=['F03 Storage: all25 Main original NullAway/Werror compile0 and all80 physical SpotBugs ClassStats exact, bugs/missing/errors0',
      'F03 Storage PMD: all18 raw findings have exact per-site current-source SS333 SSC063/308 dispositions, applicable/unclassified/processingErrors0; old39 not rerun'],
    technicalMeasurementDelta=dict(mainSources=25, physicalClassStats=80,
      rawPmdFindings=18, staticApplicable=0, unclassified=0, newProductTests=0, heldClassfileActions=0),
    nextCommand=next_command)
event = metrics.append(first['groupId'], 'CHECKPOINT', values)
target = d / '034_F03Storage全25Main静的結果.json'
target.open('x').write(json.dumps(dict(actualExit=0, eventId=event, values=values,
    quota=q, remainingDetailBasePp='1094.336'), ensure_ascii=False, indent=2) + '\n')
for name in ['checkpoint.json', 'continuation-gate.json', 'cost-ledger.json']:
    p = s / name; v = load(p)
    v.update(lastEventId=event, ordinaryActiveGroup=None, ordinaryGroupNotYetClosed=False,
      currentQuota=q, mayFinishTurn=False, executionAllowed=True,
      newImplementationAllowed=bound['newImplementationAllowedByQuota'], nextCommand=next_command,
      latestWbs66Record=dict(path=str(target.relative_to(r)), sha256=sha(target)))
    p.write_text(json.dumps(v, ensure_ascii=False, indent=2) + '\n')
for name in ['456_領域別進捗・利用枠・中断再開管理.md','460_基盤残件・再開優先順.md']:
    p = r / 'documents/400_PGPT/450_品質' / name; title, old = p.read_text().split('\n', 1)
    p.write_text(title + '\n\n## WBS66 Storage25 Main静的品質確定 ' + now + '\n\n'
      'PG36820/36822/36824/36826 Core7123: 全25Mainの原Maven NullAway/Werror compile0、全80physicalのSB指摘/欠落/解析Error0。'
      'PMDraw18は同sourceのSS333 SSC063/308各siteへ個別対応・適用/未分類0、独立XML/全物理集合照合0。'
      '不変ResourceScope/例外7classは旧39とbyte同一、再演0・全80coverage転記0。元2.4行PARTIAL・価格消化0、'
      '正式1964/53・元190受入増0・工数null・残1094.336pp不変。event ' + event + '。次: ' + next_command + '\n' + old)

print(json.dumps(dict(actualExit=0, event=event, newAcceptance=0,
    observedSharedPp=bound['observedSharedPp'], remainingOriginalRowPricePp=2.4)))
