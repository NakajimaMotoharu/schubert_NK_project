"""Freeze independent in-memory JDBC unit scope before manufacturing; original estimates retained."""
from pathlib import Path
import datetime,hashlib,json,subprocess,sys
r=Path.cwd();sys.path[:0]=[str(r/'tools/quality'),str(r/'tools/quality/vm/050_s1')]
from pmo_group_context import build_context
from pmo_quota_binding import append_start,digest
b=r/'evidence/01_PT/018_NK-OPS-001';d=r/'documents/400_PGPT/470_PMO/601_WBS66短期実行_20261117';s=r.parent/'PMO/pgpt-completion-stage-20261102';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p))
spec=r/'evidence/01_PT/004_NK-DAT-001/447_WBS66参照DAO純JDBC単体仕様.md';specification='''# WBS66 P004-03 参照DAO純JDBC単体仕様

Program NK-DAT-001 / WBS-P004-03 / SS332、SS331§3.12、DAT009/OPS009/UI251。
Production Core e4794ddf45487268883334d0f8773d89bd47dcba。実DB依存の元8件はHOLDのまま変更/実行しない。
新たな独立unitはRunReferenceRepositoryへのConnection/PreparedStatement/ResultSetのメモリ内Proxyのみ。Driver/DB起動・接続・service/Root/VM/鍵/intent/permit/native/四保留型classfileを使用しない。SQLを実行するDBは存在せず、文字列とbind値/順序を独立literalで照合する。

RRF-PURE-001: SQL全文literal、timeout5、UUID・OffsetDateTime UTC、先グレゴリオ暦/1年/9999年とmicrosecond、正常結果の四BooleanとborrowedConnection非変更、row→statement各一回close。
RRF-PURE-002: 16投影のうち全false以外15正常、四flag/anyReference/redactionを独立boolean演算で照合。全falseはSQL整合性障害。
RRF-PURE-003: constructor/read null、autoCommit/readOnly/isolation、開始/終端interrupt、flag保持、close後条件。
RRF-PURE-004: statement/row/column null、0row/2row、全false、SQLDataExceptionのredacted repository failure化。
RRF-PURE-005: 各JDBC呼出位置（bind2、column4、next2を個別）SQL例外、資源獲得/解放counts、borrowedConnection不変。
RRF-PURE-006: 同位置RuntimeException/Error、primaryとclose secondaryのSQL/Runtime/Error precedence、戻る例外のidentity・redacted suppressed、row/statement両close。
RRF-PURE-007: SQLExceptionのcause/suppressed/next内Errorの伝播、直接SQL failureのmessage/cause/suppressedにprovider診断を残さない。
RRF-PURE-008: 独立fixtureの並行呼出、共有borrowed connectionを捏造しない。有限Futureとfinally shutdown、失敗を握り潰さない。

期待値はSS332から記述したSQL文字列・独立入力とboolean/時刻literal・例外identity・fixture側資源counter。Production methodでexpectedを生成しない。新規fixtureは未実装→初回検証をTDDとして扱う。実装済みproduction違反なら修正前915/916起票。source/static/command/exit/XML/CRC/raw四counterは同凍結sourceで記録。shared utility全scope及び実DB lock/visibility、DurableRecordFiles/MaintenanceRunFiles、F02/F03の終了依存をこのunitで成立させない。元P004-03の正式受入加算は全5artifact・個別4判定・終了依存が成立後だけ。

見積は追加発見の独立純JDBC qualificationとして低.4/標準1.2/高3.6pp、cap4。元P004-03/2の.423ppは固定・未完のまま。新追加1.2と消化は別記し、元計画消化と混同しない。
'''
if spec.exists():assert spec.read_text()==specification
else:spec.open('x').write(specification)
group='PGPT-WBS66-P00403-PURE-JDBC-20261117';scope='New independent memory-only JDBC unit for current RunReferenceRepository literal SQL/UTC/null/transaction/failure/close precedence and concurrent independent fixtures. No real DB/driver/client/OS/native/VM/Root/held-four classfiles or original DB-dependent tests. Retain old successful MaintenanceRecords16 by exact source proof, no replay. Target unmet P004-03 contract/source-quality only; full leaf remains pending foundation, original DB/retained file and other artifacts.'
q=json.loads(Path(sys.argv[1]).read_text());values=dict(build_context(group_id=group,category='IMPLEMENTATION',kind='ADDITIONAL_FINDING',scope=scope,oracle_refs=[ref(spec)]),source='e4794ddf45487268883334d0f8773d89bd47dcba',headAtStart=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),wbsLeafIds=['WBS-P004-03'],managementPlan='WBS66-58-20261117-SHORTTERM',managementWorkIds=['WBS-P004-03/2'],estimateAtGroupStartPp=dict(low=.4,base=1.2,high=3.6),groupCapPp=4,additionalDiscoveryPlanPricePp=1.2,originalRowPricePp=.423,originalRowPriceUnchanged=True,originalScopeAcceptanceDelta=0,newAcceptance=0,actualAllocatedPp=None,tokenTotals=None,nextCommand='Implement pure in-memory JDBC unit, lint/compile/static/unit and independent raw post at frozen source; keep original DB tests and full acceptance pending.')
event=append_start(group,values,sys.argv[1],digest(q),datetime.datetime.now(datetime.timezone.utc).isoformat());target=d/'015_P00403純JDBC追加群開始.json';target.open('x').write(json.dumps(dict(actualExit=0,eventId=event,groupId=group,values=values,quota=q),ensure_ascii=False,indent=2)+'\n')
for name in ['checkpoint.json','continuation-gate.json','cost-ledger.json']:
 p=s/name;v=json.loads(p.read_text());v.update(phase='WBS66_ACTIVE',lastEventId=event,ordinaryActiveGroup=group,ordinaryGroupNotYetClosed=True,currentQuota=q,executionAllowed=True,newImplementationAllowed=True,mayFinishTurn=False,nextCommand=values['nextCommand'],latestWbs66Record=ref(target));p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(actualExit=0,event=event,estimate=values['estimateAtGroupStartPp'],cap=4)))
