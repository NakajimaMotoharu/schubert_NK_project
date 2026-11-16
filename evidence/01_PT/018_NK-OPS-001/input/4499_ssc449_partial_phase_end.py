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
first = load(d / '037_SSC449四module是正後Main群開始.json')
post = r / 'evidence/01_PT/018_NK-OPS-001/evidence/PG36854-ssc449-four-main-partial-return-v2/manifest.json'
m = load(post); assert m['actualExit'] == 0
q = load(Path(sys.argv[1])); now = datetime.datetime.now(datetime.timezone.utc).isoformat()
bound = end_fields(first['quota'], q, digest(q), now, m['terminalAtUTC'], 5)
assert not any(x['groupId'] == first['groupId'] and x.get('groupBoundary') == 'END'
               for x in map(json.loads, metrics.EVENTS.read_text().splitlines()))
next_command = ('Continue required manufacturing dependency for F03: six closed-literal migration SQL Main '
    'owned/costed by P01903. Price additional .4/1.2/3.6 cap4 before edits, register remaining SQL '
    'static issue before correction and detail supplement if required; preserve all SQL bytes/order, '
    'borrowed TX/resource semantics, public API and existing independent whole160 tests. Review '
    'and execute ordinary memory-only Test closures with exact current source, no DB/master/native '
    'or held types. Avoid new suppression/exclusions. Backup path2, remaining PMD971 and API/Web '
    'QA056 remain separate incomplete conditions. Do not stop at this partial return.')
values = dict(bound, source=m['source'], groupBoundary='END',
    sourceEvidenceBinding=bind([(post, sha(post))], m['source']),
    wbsLeafIds=['WBS-F03'], workCategory='CONTRACT_AUDIT',
    workAttributionKind='REWORK', managementWorkIds=['WBS-F03/2-2'],
    estimateAtGroupStartPp=first['values']['estimateAtGroupStartPp'], groupCapPp=5,
    completedOriginalRowPricePp=0, remainingOriginalRowPricePp=2.4,
    newAcceptance=0, formalUpdated=False, effortCompletionRate=None,
    criterionReductions=['F02/F03 four complete modules: actual477 Main/1092 physical original compile0; Protocol175/Storage80 byte-identical reusable proofs, no152/39 replay',
      'BUG3129 compiler SDK annotations fixed within original C row, current explicit3.55.1 classpath; original failure preserved',
      'BUG3130 dependency stale-M2 flaw isolated; fresh sibling exact byte/whole191+646 ClassStats/missing0/errors0 and four guard negatives verified, raw8SQL+2Backup remain',
      'PMD fullRoot287 source: raw971/processing0, 309 exact-source/site/message candidate reviews and662 unmatched; candidates not final dispositions; original F03 still not accepted',
      'BUG3131 post domain corrected parent Unit versus MainCore; negative3 and seven-scope horizontal verified, no product replay'],
    technicalMeasurementDelta=dict(mainSources=477, physicalClasses=1092, compiledModules=4,
      analysisMissingClasses=0, analysisErrors=0, rawSpotbugsUnresolved=10, rawPmdFindings=971,
      pmdReuseCandidatesNotFinal=309, pmdUnmatched=662, newProductTests=0, heldClassfileActions=0),
    nextCommand=next_command)
event = metrics.append(first['groupId'], 'CHECKPOINT', values)
target = d / '038_SSC449四module結果・F03残条件.json'
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
    p.write_text(title + '\n\n## WBS66 四module477Main正常compile・静的残971/10確定 ' + now + '\n\n'
      'Coree8822b0e/PG36844・36854: 原NullAway/WerrorでProtocol165/Storage25/Bootstrap87/Batch200全477Main compile0、物理175/80/191/646=1092。'
      '新旧Protocol175/Storage80全byte同一・旧152/39再演0。SDK annotation欠落BUG3129当Bootstrapは是正済、YKT2600のAPI/WebはQA056保留。'
      '原SBの旧m2依存BUG3130はPG36848 fresh siblingでmissing/error0・191/646全ClassStatsだがSQL8/Backup2の指摘は残り品質PASSでない。'
      'PG36846 PMDraw971/processing0、PG36851既source/site一致の再利用候補309・新規要確認662（最終分類未完）。'
      'PG36852 post比較domain失敗BUG3131を保全、36854/36856のparent Unit/source別role・負7/横七確認で当工具/YKT2602閉鎖。'
      '正式1964/53・元190新規0・工数null、原既存価格5.050＋追加完了1.950・元残1094.336pp不変、F03元2.4はPARTIAL/消化0。'
      '全own Maven/static jobは元tool sessionの終了を回収済、外部/VM/aruは未照会UNKNOWN・二重操作0。event '+event+'。次: '+next_command+'\n'+old)

print(json.dumps(dict(actualExit=0, event=event, newAcceptance=0,
    observedSharedPp=bound['observedSharedPp'], remainingOriginalRowPricePp=2.4)))
