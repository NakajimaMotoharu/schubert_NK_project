"""Recover only missing 456/460 text after existing event5402; never rerun end."""
from pathlib import Path
import datetime,hashlib,json
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';i=b/'input';d=r/'documents/400_PGPT/470_PMO/600_通常PGPT_20261106';s=r.parent/'PMO/pgpt-completion-stage-20261102';load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
c=load(i/'3420_pgcopy_source_end_v2.json');rec=load(d/'2095_WBS65PgJDBC COPY source段終了.json');assert rec['eventId']=='PGPT-20261008-5402' and rec['groupId']==c['groupId'] and rec['actualExit']==0
for name in ['checkpoint.json','continuation-gate.json','cost-ledger.json']:
 v=load(s/name);assert v['lastEventId']==rec['eventId'] and v['ordinaryGroupNotYetClosed'] is False
 assert v['latestWbs65Record']['sha256']==sha(d/'2095_WBS65PgJDBC COPY source段終了.json')
c['checkpointText']=c['summary']+' 管理失敗BUG3005（source段ラベルとcanonical集計区分）を605別版で是正、BUG3006（checkpointText誤名）は既終了event5402/2095/外部state三つ同一を確認し456/460欠落だけ補完、end再発行0。両管理修正は製品PT/正式成果へ加算0。'
q=load(s/'quota-ssc417-end-v2-20261115.json');c['checkpointText']+=' 実利用枠観測残'+str(q['primary']['remainingPercent'])+'%、共有窓差0pp（専有実費ではなく丸めた共有観測差）、実token欠測null。'
(i/'3422_pgcopy_end_recovered_config_not_for_replay.json').open('x').write(json.dumps(dict(c,recoveryOnly=True,doNotReplay=True),ensure_ascii=False,indent=2)+'\n')
now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat();text='\n## 最新checkpoint（'+now+'、WBS65 SSC417 source段・管理終了補完）\n\n'+c['checkpointText']+' 正本184/625行。event '+rec['eventId']+'。次: '+c['nextCommand']+'\n\n'
for name in ['456_領域別進捗・利用枠・中断再開管理.md','460_基盤残件・再開優先順.md']:
 p=r/'documents/400_PGPT/450_品質'/name;t=p.read_text();assert rec['eventId'] not in t[:5000];first,rest=t.split('\n',1);p.write_text(first+'\n'+text+rest)
e=b/'evidence/PG33712-pgcopy-source-only-limited-join-v1';(e/'end-footer-recovery.json').open('x').write(json.dumps(dict(actualExit=0,existingEvent=rec['eventId'],existingRecord=dict(path=str((d/'2095_WBS65PgJDBC COPY source段終了.json').relative_to(r)),sha256=sha(d/'2095_WBS65PgJDBC COPY source段終了.json')),onlyMissingDocsRepaired=True,newEndEventWritten=False,productExecution=0,relatedBugs=['BUG3005','BUG3006']),ensure_ascii=False,indent=2)+'\n')
for name,ids in [('915_障害表.md','BUG3005/BUG3006'),('916_横展開管理台帳.md','YKT2534/YKT2535')]:
 with (r/'documents/900_OTHER/910_台帳'/name).open('a') as f:f.write('\n2026-11-15 '+ids+'限定状態CLOSED: PG33712/forecast-metadata-correction.json及びend-footer-recovery.json終了0。canonical184/625/元budget保持、source-only追加stageを別fieldへ分離、元end5402/2095と外部state三つのevent/hash一致を照合し456/460だけ補完。元失敗/入力/forecastは保全、二重event/製品PT再実行0。修正commitは後続保存commit。\n')
print(dict(actualExit=0,existingEvent=rec['eventId'],newEvent=False,onlyMissingFooterRecovered=True))
