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

d = r / 'documents/400_PGPT/470_PMO/601_WBS66短期実行_20261117'
s = r.parent / 'PMO/pgpt-completion-stage-20261102'
load = lambda p: json.loads(p.read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
first = load(d / '035_F03四module全477Main群開始.json')
post = r / 'evidence/01_PT/018_NK-OPS-001/evidence/PG36836-bootstrap-original-javac-diagnostic-v1/manifest.json'
m = load(post); assert m['actualExit'] == 1; m['source'] = m['sourceCore']
q = load(Path(sys.argv[1])); now = datetime.datetime.now(datetime.timezone.utc).isoformat()
bound = end_fields(first['quota'], q, digest(q), now, m['terminalAtUTC'], 5)
assert not any(x['groupId'] == first['groupId'] and x.get('groupBoundary') == 'END'
               for x in map(json.loads, metrics.EVENTS.read_text().splitlines()))
next_command = ('SSC449 design PR412/main7e883a3f is published; POM-only fix Coree8822b0e is committed, '
    'business Main/Test/Root flags unchanged. Start fresh original-POM four-module Main477 compile '
    'at the fixed Core; same checker-qual3.55.1 now explicit compile, no Test/app/native/DB or '
    'QA056 four held types. Preserve PG36830/34/36 exit1/10warnings and do not count them passed. '
    'Then current-source static and exact dependency/runtime/ABI checks, no old successful PT replay.')
values = dict(bound, source=m['source'], groupBoundary='END',
    originalFailedEvidence=dict(path=str(post.relative_to(r)),sha256=sha(post),actualExit=1),
    groupResult='FAILED_ORIGINAL_SOURCE_NOT_ACCEPTED',
    wbsLeafIds=['WBS-F03'], workCategory='CONTRACT_AUDIT',
    workAttributionKind='SOURCE_REQUALIFICATION', managementWorkIds=['WBS-F03/2-2'],
    estimateAtGroupStartPp=first['values']['estimateAtGroupStartPp'], groupCapPp=5,
    completedOriginalRowPricePp=0, remainingOriginalRowPricePp=2.4,
    newAcceptance=0, formalUpdated=False, effortCompletionRate=None,
    criterionReductions=['F03 four-module compile: Protocol/Storage succeeded, Bootstrap failed due10 missing SDK annotation warnings; Batch not run',
      'BUG3129/YKT2600 source cause proven by original javac flags; SSC449 missing checker-qual3.55.1 compile scope fixed but not yet retested'],
    technicalMeasurementDelta=dict(mainSourcesAttempted=477, protocolPhysical=175,
      storagePhysical=80, bootstrapPhysical=0, batchPhysical=0, rawCompileExit=1,
      warnings=10, newProductTests=0, heldClassfileActions=0),
    nextCommand=next_command)
event = metrics.append(first['groupId'], 'CHECKPOINT', values)
target = d / '036_F03四module失敗・原因と是正待ち.json'
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
    p.write_text(title + '\n\n## WBS66 四module compile原因確定・是正後未実行 ' + now + '\n\n'
      'Core7123/PG36830はProtocol/Storage成功・Bootstrap失敗・Batch未実施。PG36834/36836原RootflagsでJDBC annotation欠落10warning→Werror終了1を直接確認。'
      'BUG3129/YKT2600先起票、SSC449 PR412/main7e883a3fでSS311354914反映後、Coree8822b0eでBootstrapへ既checker-qual3.55.1をcompile依存追加。'
      '業務Main/Test/Rootflags不変・旧runtime同GAV、是正後通常compile/static未実行。元F03行PARTIAL/消化0、正式1964/53・受入増0・工数null・残1094.336不変。'
      'event '+event+'。次: '+next_command+'\n'+old)

print(json.dumps(dict(actualExit=0, event=event, newAcceptance=0,
    observedSharedPp=bound['observedSharedPp'], remainingOriginalRowPricePp=2.4)))
