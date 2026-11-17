"""Return actual 113/three raw-100 programs to F03; preserve the historical raw XML and all holds."""
from pathlib import Path
from collections import Counter
import datetime,hashlib,json
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';ld=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p))
pp=b/'evidence/PG37248-monitor-lock113-independent-post-v1/manifest.json';p=ld(pp);assert p['actualExit']==0 and p['tests']==113 and p['targetRawFour100']
assert all(p[k]==0 for k in ['failed','errors','skipped','notRun']) and p['targetMissedMethods']==[]
reconcilep=b/'evidence/PG37092-f03-971-independent-reconcile-v2/manifest.json';old=ld(reconcilep);assert old['actualExit']==0 and old['originalPmdRaw']==971 and old['finalNotApplicable']==922 and old['unclassified']==49
assert sha(r/old['rawXml']['path'])==old['rawXml']['sha256']
oldroot=ld(b/'evidence/PG36960-current287-root-pmd-v1/manifest.json');inputs=oldroot['sourceInputs'];assert len(inputs)==287
changed={n for n,h in inputs.items() if sha(r/n)!=h}
three={'src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/monitoring/'+n+'.java' for n in ['BatchMetricRecorder','MonitoringObservationClock','MonitoringPoller']}
service='src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/platform/MorningServiceReadiness.java';assert changed==three|{service}
main_current=ld(b/'evidence/PG37228-monitor-lock4-test-static-v2/manifest.json');service_current=ld(b/'evidence/PG37186-service12-reused-compile-static-v1/manifest.json')
assert all(sha(r/n)==main_current['mainInputHashes'][n] for n in three) and sha(r/service)==service_current['mainInputHashes'][service]
current_raw=[x for x in main_current['rawFindings'] if x['path'] in three]+[x for x in service_current['rawFindings'] if x['path']==service]
assert len(current_raw)==5 and not any(x['rule']=='AvoidSynchronizedStatement' for x in current_raw)
import xml.etree.ElementTree as ET
known=ld(b/'evidence/PG37092-f03-971-independent-reconcile-v2/all-current-dispositions.json');unknown=ld(b/'evidence/PG37084-f03-specific-lifetime83-applicability-v1/remaining-unmatched.json');assert len(known)==922 and len(unknown)==49
assert len({x['rawFindingIndex'] for x in known+unknown})==971
all_old=[]
for node in ET.parse(r/old['rawXml']['path']).getroot().iter():
 if node.tag.rsplit('}',1)[-1]=='file':
  for raw in node:
   if raw.tag.rsplit('}',1)[-1]=='violation':all_old.append(dict(rawFindingIndex=len(all_old),path=str(Path(node.get('name')).relative_to(r)),**raw.attrib))
assert len(all_old)==971
for row in known+unknown:
 raw=row.get('raw',row);match=all_old[row['rawFindingIndex']];assert match['path']==raw['path'] and match['rule']==raw['rule']

old_changed=[x for x in all_old if x['path'] in changed];assert len(old_changed)==9
removed={259,262,263,264};assert {x['rawFindingIndex'] for x in old_changed if x['rule']=='AvoidSynchronizedStatement'}==removed
key=lambda x:(x['path'],x['rule'],x.get('method'))
assert Counter(key(x) for x in old_changed if x['rawFindingIndex'] not in removed)==Counter(key(x) for x in current_raw)
prior_remaining=ld(b/'evidence/PG37084-f03-specific-lifetime83-applicability-v1/remaining-unmatched.json');remaining=[x for x in prior_remaining if x['rawFindingIndex'] not in removed];assert len(remaining)==45
assert Counter(x['raw']['rule'] for x in remaining)==Counter(AvoidSynchronizedStatement=35,AvoidCatchingGenericException=10)
assert all(sha(r/x['raw']['path'])==x['sourceSha256'] for x in remaining)
out=b/'evidence/PG37254-monitor-lock113-criteria-return-v2';assert not out.exists();out.mkdir();remainingp=out/'remaining-source-findings.json';remainingp.write_text(json.dumps(remaining,ensure_ascii=False,indent=2)+'\n')
v=dict(actualExit=0,terminalAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),sourceCore=p['sourceCore'],actualUnitSource=p['source'],run=p['run'],tests=113,oldWholeSourceCases=107,newWholeSourceCases=6,failed=0,errors=0,skipped=0,notRun=0,independentPost=ref(pp),targetRaw=p['targetRawCounters'],targetAllFiveCounters100=True,positiveProductCrc=p['positiveProductCrc'],fullPhysicalContext=1101,sourceRuleSuppressionChanges=0,
 oldRootRawXmlRetained=old['rawXml'],oldRootRaw=971,unchangedRootSources=283,changedRootSources=sorted(changed),currentChangedSourceRaw=current_raw,removedOriginalSyncFindingIndices=sorted(removed),remainingFindings=ref(remainingp),remainingUnresolvedBefore=49,remainingUnresolvedAfter=45,remainingSync35=True,recoveryCatch10StillHeld=True,
 currentSourceBoundCompositeRaw=967,compositeNotSingleRunOrSixModuleGate=True,original922NotApplicableNotNewAcceptances=True,
 criteria=[dict(id='WBS-F03/'+n,judgment='PARTIAL',reduced='Four ordinary static sites removed and three actual same-source programs all raw counters100; original107/new6 finite failure/reentry/exclusion proofs',remaining='Six-module/QA056, native35 and recovery10 findings, same-source complete451/trace and ending dependencies remain open') for n in ['reuse','criterion/contract','criterion/scope','criterion/quality']],
 completedOriginalRowPricePp=0,remainingOriginalRowPricePp=2.4,additionalPricePp=0,remainingDetailBasePp='1092.098',newOriginal190Accepted=0,formalTests=1964,formalScopes=53,formalUpdated=False,effortCompletionRate=None,
 reworkSeparated=['3162 import-order formatter validator','3163 new Test AutoCloseable declaration','3164 direct-field lock static warning: mitigated with explicit paired final alias/result; detector root cause not concluded','3165 new private Test field name','3166 static tool statement ordering, successful compile reused','3167 future completion must be checked after state observation'],
 limitedClosedBugs=['BUG3161','BUG3162','BUG3163','BUG3165','BUG3166','BUG3167'],mitigatedButCauseNotClosed=['BUG3164'],globalHorizontalStillOpen=['YKT2630 native35','YKT2633 detector-cause hypothesis','existing Root/native/QA056 holds'],
 actualRootNativeVmDbKeyIntentOperations=0,oldExecCombined=False)
(out/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
result=b/'4478_F03通常監視113実行結果・三program四coverage100.md';result.open('x').write('# 通常監視113件の実行結果\n\nMain Core '+p['sourceCore']+'、Unit '+p['source']+'、run '+p['run']+'。元13whole class107件＋新1whole class6件を同一runで実行し、F/E/S/not-run0・真正exit0。PG37248で元XML/単一exec/全1101 CRC/initを照合し、actual Native/Root境界0。\n\n| 対象3 program合計 | covered | missed |\n|---|---:|---:|\n'+''.join('| '+k+' | '+str(x['covered'])+' | '+str(x['missed'])+' |\n' for k,x in p['targetRawCounters'].items())+'\n除外なし、全13method/34branch/109line/3class/495instructionが100%。他48 positive Mainも元counterを保存し、全1101/六module100%へ拡張しない。\n\nPG37224 compile477/PG37226 Batch646全SB0/PG37232 public ABI一致、他1098physical同一。現Main4/Test20 PMDはPG37244の個別根拠で非該当、CS0。原失敗37212/37218/37220/37236等を成功へ上書きしない。BUG3164は現静的は0だがdetector内部根因未確定で原因調査を残す。YKT2630も通常4だけ完了、native35未完。\n\nF03残は49→45（同期39→35、回復10保持）。旧971 XMLを保持し、283不変source＋現4 sourceの個別結果へ対応した合成raw967は単一run/六modulegateではない。元922非該当を再受入計上しない。F03四criteriaは全てPARTIAL、QA056・F02/F03六module・全451/trace/終了依存は未受入。元190新受入0、正式1964/53、工数null、原残1092.098pp。\n\n公開証拠/hashはPG37246の元run、PG37248の独立post、PG37250のmanifest/remaining-source-findingsへ記録。実行commandとOS/branch/commit、全113 TestID対応は元run begin/manifestに保持。IT/ST完了の宣言なし。\n')
ledger=r/'documents/900_OTHER/910_台帳'
with (ledger/'915_障害表.md').open('a') as f:f.write('\n\nBUG3161/3162/3163/3165/3166/3167 当通常scope限定CLOSED（2026-11-17）: Main7e6cb3cc/Unit15d7a84a/PG37246 whole113全FESnotrun0/真正0、PG37248独立1101CRC/単一exec/init0・当三program109L13M3C34B495I全miss0。3161は四siteのprivate paired locks/再入・異threadfailure解放、3162は四sourceのimport集合/他全token保持と全formatter診断、3163はAutoCloseable宣言/borrowed registry非close、3165はprivate定数の逆変換/静的同名指摘消滅、3166は成功16compileを再使用した後段static0、3167はstate後Future非完了確認＋LOCK406実排他/元worker終端を確認。修正commit e2ff2b36/7e6cb3cc/15d7a84a、再試験/証跡37224/26/32/42/44/46/48/50。BUG3164は当source無抑制SB646指摘0でMITIGATEDだが、元CWO内部根因未確定を保持しCLOSEDとしない。global/native/Root/QA056/正式受入は閉じない。\n')
with (ledger/'916_横展開管理台帳.md').open('a') as f:f.write('\n\nYKT2631/2632/2634/2635/2636 当scope限定完了（2026-11-17）: 対象四整形、両registry fixture、全private定数参照、static-only入力順、状態/Future観測順の全対象へ修正又は具体非該当を記録し、元107保持＋新6をPG37246同一113で実証。PG37248独立全1101/三target全counter100、PG37250現source/F03残45へ結合。YKT2630は通常四siteのみ完了、native35を残しOPEN。YKT2633は二入口paired final alias/解放後返却と当sourceSB0/実再入/交差排他を確認したが検出器根因は未確定でMITIGATED/OPEN。旧失敗/診断欠測/全HOLDを保存。修正commit e2ff2b36/7e6cb3cc/15d7a84a及び当post commit。\n')
print(json.dumps(dict(actualExit=0,tests=113,targetRawAll100=True,unresolvedBefore=49,after=45,formalNew=0)))
