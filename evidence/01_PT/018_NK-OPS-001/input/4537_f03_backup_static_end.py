"""Persist true full-module static progress; keep F03 and all operational PT incomplete."""
from pathlib import Path
import datetime
import hashlib
import json
import sys

r=Path.cwd();sys.path[:0]=[str(r/'tools/quality'),str(r/'tools/quality/vm/050_s1')]
import pg998_metrics as metrics
from pmo_quota_binding import digest,end_fields
from source_evidence_binding import bind
b=r/'evidence/01_PT/018_NK-OPS-001';d=r/'documents/400_PGPT/470_PMO/601_WBS66短期実行_20261117'
load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p))
start=load(d/'044_F03固定Path是正群開始.json');p=b/'evidence/PG36966-backup-saved-static-independent-v3/manifest.json';m=load(p)
assert m['actualExit']==0 and m['spotbugsBugsMissingErrors']==0
q=load(Path(sys.argv[1]));now=datetime.datetime.now(datetime.timezone.utc).isoformat()
bound=end_fields(start['quota'],q,digest(q),now,m['terminalAtUTC'],5)
assert not any(x['groupId']==start['groupId'] and x.get('groupBoundary')=='END' for x in map(json.loads,metrics.EVENTS.read_text().splitlines()))
next_command=('Continue priority P01808 three-child contract: verify saved PG15276/15278/15281 original14 pure Profile/Terminal evidence against current Root class bytes and exact Test hashes, without rerunning successful14. Classify remaining Checkpoint/StopHold/PrivateFile ordinary versus held actual operations using complete source/Test call graphs, then execute only genuinely missing permitted normal PT with independent oracles. Keep QA056 API/Web four classfile phases pending, and F03 PMD971 classification separate, no native/Root/VM/DB/key/intent actions or quality relaxation.')
values=dict(bound,source=m['source'],groupBoundary='END',wbsLeafIds=['WBS-F03'],workCategory='CONTRACT_AUDIT',workAttributionKind='REWORK',
    managementWorkIds=['WBS-F03/2-2'],estimateAtGroupStartPp=start['values']['estimateAtGroupStartPp'],groupCapPp=5,
    completedOriginalRowPricePp=0,remainingOriginalRowPricePp=2.4,additionalPricePp=0,
    sourceEvidenceBinding=bind([(p,sha(p))],m['source']),newAcceptance=0,formalUpdated=False,effortCompletionRate=None,
    criterionReductions=['F03 full Main compile remains4/6 modules: current477 originalRoot/NullAway/Werror success,1101physical unchanged except one factory class',
      'F03 full SB now4/6 modules qualified: current Bootstrap200/Batch646 allClassStats/bugs-missing-errors0 plus unchanged Protocol175/Storage80 proofs',
      'F03 two raw Backup findings corrected at fixed Path expression; existing suppression annotation/rules and all external behavior unchanged',
      'F03 PMD fullBootstrap/Batch287 current971/processing0;309 exact-source/site candidates662 unmatched, none autoaccepted; API/Web QA056 unresolved'],
    technicalMeasurementDelta=dict(compileModules=4,spotbugsModules=4,main=477,physical=1101,newProductTests=0,pmd287Raw=971,pmdReuseCandidatesNotFinal=309,pmdUnmatched=662,originalBackupSpotbugs=2,currentBackupSpotbugs=0),
    bugsClosed=['BUG3137','BUG3138','BUG3139','BUG3140'],horizontalClosed=['YKT2608','YKT2609','YKT2602'],nextCommand=next_command)
event=metrics.append(start['groupId'],'CHECKPOINT',values);target=d/'045_F03四moduleSB0・PMD残971.json'
target.open('x').write(json.dumps(dict(actualExit=0,eventId=event,values=values,quota=q,proof=ref(p),remainingDetailBasePp='1094.336',formal1964PT53ScopeUnchanged=True,newOriginal190Acceptance=0),ensure_ascii=False,indent=2)+'\n')
summary=('Core01c3b1a3/PG36956全477Main原Mavencompile0、物理1101。PG36958 Bootstrap200/Batch646全ClassStats・SB指摘/欠落/解析Error0、Protocol175/Storage80の不変byteも確認しfullSB4/6。固定Path評価位置だけを既注釈factoryへ移動、公開ABI/全注釈/全Test不変、他1100physical完全一致・native/intent実操作0。PG36960全287Main PMDraw971/processing0、36968再利用候補309/未照合662で最終分類未完。PG36962 source-domain/36965ダミーID失敗は保持、36966保存javap三出力を再演0で独立回収、parent比較負3/参照JSON正XML負を確認。BUG3137～3140とYKT2608/2609/再発2602は当範囲限定CLOSED、実createService通常PT/native/HOLDと全F03/451は未受入。元F03行2.4は完了0・残2.4、追加価格0、全残1094.336pp不変、正式1964/53・元190新規0・工数null。')
l=r/'documents/900_OTHER/910_台帳'
for name,ids in [('915_障害表.md',['BUG3137','BUG3138','BUG3139','BUG3140']),('916_横展開管理台帳.md',['YKT2608','YKT2609','YKT2602'])]:
    with (l/name).open('a') as f:
        for ident in ids:f.write('\n2026-11-17 '+ident+' 当静的/工具対象の是正・全非該当/再発防止確認で限定CLOSED。'+summary+' 証跡PG36966 SHA256 '+sha(p)+'、修正source '+m['source']+'、各input/ledgerを含むcommit履歴。完了2026-11-17。\n')
for name in ['456_領域別進捗・利用枠・中断再開管理.md','460_基盤残件・再開優先順.md']:
    p2=r/'documents/400_PGPT/450_品質'/name;title,body=p2.read_text().split('\n',1)
    p2.write_text(title+'\n\n## WBS66 四module完全SB0・固定Path局所是正 '+now+'\n\n'+summary+' 既知own compile/SB/PMD/post全真正終了、own job残0。foreign/VM/aru未照会UNKNOWN・二重操作0、fresh残'+str(q['primary']['remainingPercent'])+'、共有差'+str(bound['observedSharedPp'])+'、event '+event+'。次: '+next_command+'\n'+body)
s=r.parent/'PMO/pgpt-completion-stage-20261102'
for name in ['checkpoint.json','continuation-gate.json','cost-ledger.json']:
    p2=s/name;v=load(p2);v.update(lastEventId=event,ordinaryActiveGroup=None,ordinaryGroupNotYetClosed=False,currentQuota=q,productionCoreMain=m['source'],currentWbs66RemainingDetailBasePp='1094.336',latestWbs66Record=ref(target),mayFinishTurn=False,executionAllowed=True,newImplementationAllowed=bound['newImplementationAllowedByQuota'],nextCommand=next_command)
    v['currentManufacturingBoundary']=dict(source=m['source'],run='PG36956/36958/36960/36966',ownJobState='TRUE_TERMINAL0_STATIC_ONLY',foreignHostVmDbState='UNQUERIED_UNKNOWN',scope='FULL4MODULE477MAIN_SB4OF6_PMD971_PENDING',evidence=ref(p),whole451Accepted=False,newAcceptance=0)
    p2.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
(b/'4458_F03固定Path通常製造・静的実結果.md').open('x').write('# F03 固定Path製造・静的実結果\n\n'+summary+'\n\n元Normal PTの未実施を静的チェックへ混ぜない。環境・command・全exit・source/byte/hashは36956/58/60/66。基準estimate2.4/cap5不変、実専有token/費用不明。\n')
print(json.dumps(dict(actualExit=0,event=event,compileModules=4,spotbugsModules=4,pmdRaw=971,newAcceptance=0,originalRowCompletedPp=0)))
