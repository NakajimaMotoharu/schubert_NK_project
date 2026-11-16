"""Record the verified source-only stage; retain every unfinished static condition."""
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
first = load(d / '031_F03正式MavenMainvalidate開始.json')
post = r / 'evidence/01_PT/018_NK-OPS-001/evidence/PG36814-six-main-maven-validate-independent-v1/manifest.json'
m = load(post); assert m['actualExit'] == 0
q = load(Path(sys.argv[1])); now = datetime.datetime.now(datetime.timezone.utc).isoformat()
bound = end_fields(first['quota'], q, digest(q), now, m['terminalAtUTC'], 5)
assert not any(x['groupId'] == first['groupId'] and x.get('groupBoundary') == 'END'
               for x in map(json.loads, metrics.EVENTS.read_text().splitlines()))
next_command = ('Continue F03/2-2 with independent Storage25 Main-only original Maven compile '
    'and static checks after explicit current source/tool/ownership admission; no Test/application '
    'initialization/native execution or four QA056 held classfiles. No need to repeat six Main '
    'Spotless validate. Original F02/F03 remain not accepted; P01808 unchanged14 proof is reference '
    'only until complete current scope/byte/dependency conditions are established.')
values = dict(bound, source=m['source'], groupBoundary='END',
    sourceEvidenceBinding=bind([(post, sha(post))], m['source']),
    wbsLeafIds=['WBS-F03'], workCategory='CONTRACT_AUDIT',
    workAttributionKind='SOURCE_REQUALIFICATION', managementWorkIds=['WBS-F03/2-2'],
    estimateAtGroupStartPp=first['values']['estimateAtGroupStartPp'], groupCapPp=5,
    completedOriginalRowPricePp=0, remainingOriginalRowPricePp=2.4,
    newAcceptance=0, formalUpdated=False, effortCompletionRate=None,
    criterionReductions=['F03 source format: actual original Maven six-module Main Spotless/enforcer validate now successful; previous CLI-only limitation removed for Main scope',
      'F02 dependency convergence: original reactor root plus six modules passed seven enforcer gates; Main compile/runtime still separate'],
    technicalMeasurementDelta=dict(mainSources=1022, normalSpotlessGates=7,
      dependencyConvergenceGates=7, newProductTests=0, heldClassfileActions=0),
    nextCommand=next_command)
event = metrics.append(first['groupId'], 'CHECKPOINT', values)
target = d / '032_F03正式MavenMainvalidate結果.json'
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
    p.write_text(title + '\n\n## WBS66 正式Maven Main validate完了 ' + now + '\n\n'
      'PG36812/36814 Core7123: 全1022Mainの原Maven Spotless・enforcer七gate成功、classfile/Test/DB/native生成実行0。'
      'F03のCLI-only不足をMain範囲で解消、型/null/PMD/SB・四型QA056は未成立のまま。元2.4行はPARTIAL・価格消化0、'
      '原正式1964/53・元190受入増0・工数null・残1094.336pp不変。event ' + event + '。次: ' + next_command + '\n' + old)
print(json.dumps(dict(actualExit=0, event=event, newAcceptance=0,
    observedSharedPp=bound['observedSharedPp'], remainingOriginalRowPricePp=2.4)))
