"""Price the existing protocol completeness audit after the SSC447 prerequisite, without test replay."""
from pathlib import Path
import csv,datetime,hashlib,json,subprocess,sys
r=Path.cwd();sys.path[:0]=[str(r/'tools/quality'),str(r/'tools/quality/vm/050_s1')]
from pmo_group_context import build_context
from pmo_quota_binding import append_start,digest
b=r/'evidence/01_PT/018_NK-OPS-001';d=r/'documents/400_PGPT/470_PMO/601_WBS66短期実行_20261117';s=r.parent/'PMO/pgpt-completion-stage-20261102';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p));plan=r.parent/'PMO/hourly-monitor/wbs66-20261116/58_直近20pp不足時の対象と予算判断を実行用の検収表へ渡す';row=next(x for x in csv.DictReader((plan/'WBS.tsv').open(encoding='utf-8-sig'),delimiter='\t') if x['ID']=='WBS-G13.01');hold=next(x for x in csv.DictReader((plan/'76保留の引渡し.tsv').open(encoding='utf-8-sig'),delimiter='\t') if 'H-G13.01' in x.values());estimate={k:float(row[v]) for k,v in [('low','楽観pp'),('base','残pp'),('high','慎重pp')]};assert estimate==dict(low=.25,base=.75,high=1.5)
spec=b/'4452_G1301現候補全Protocol・64layout追跡監査仕様.md';content='''# G13.01 現候補全Protocol・64layout追跡監査仕様

WBS-G13.01 / SS361、SS323・UI233～236・SYS011/SCP001002003006。Core7123、既e479同Protocol165Main/35Test/五TSVとphysical175/Code162・152PTの適用を個別hashで照合。元SSC447補.9は既済・再演0。

H-G13.01の原引渡しはREAD/STATIC/DOCUMENT_SCOPE_ONLY_CHECKED_PER_TOOL、明示公開metadataに対するrequirement/source/physical/WBSの多対多traceである。fixture/DB/native/Root等の実操作は別の着手契約が必要。本監査はそれらを行わず、対象はProtocol source/既公開fixture/既適格の175physical metadataだけ、保留型classfile/Root2/保護二工具/原本/秘密を先に対象外にする。原HOLDや元G13全子の受入を一括解除しない。

G13P-001: 現165Main/全35Test/五fixtureの源Core、元scope/input/tool hashと適用条件を照合、旧152の成功確認再実行0/旧exec合成0。
G13P-002: 165Mainをcanonical485の一意owner・関連Program/RD/UI/SSと結合し、全175physicalを源Mainへ欠落0で多対一照合。raw4method58branchの未成立はownerへ返し、trace完全性と製品品質を混同しない。
G13P-003: UI233の64layoutを独立layouts/named-types/fields/golden fixture及び承認SS323へ結合し、69公開型の源class/ownerを照合。実TestID・JUnit method・入力fixture行とtrace IDを対応付ける。64rowを64JUnit成功へ増幅0。
G13P-004: SYS011とSCP001002003006の実原文・担当scope・終了依存へ接続。UI/SS改訂と旧fixtureの版差はfield table/offset/length等の実物で個別判断し、古いheader SHAのみで互換合格/変更を推定しない。Golden vectorをproductionに合わせて変更0。
G13P-005: 独立postで全file hash/集合/参照の一意性・未確認一覧・現在Core/元Unit/公開証拠/監査者と時刻を照合。owner/requirement/TestID未特定があれば未確認のまま返し、G13.01を完了へしない。Main/fixture/type/外部仕様の変更は本群外で先行分類・起票する。

原.25/.75/1.5pp、cap2。元17件の再資格を新規受入へ算入0。G13.01が完了しても元G13全7子のうち一子であり、元190新規受入/全451/工数率へ変換しない。UI/SS正本はorigin/main、元WBS65/777比較基点は保持。
'''
if spec.exists():assert spec.read_text()==content
else:spec.open('x').write(content)
q=json.loads(Path(sys.argv[1]).read_text());group='PGPT-WBS66-G1301-PROTOCOL-TRACE-20261117';scope='Existing G13.01 explicit public/source/physical/WBS trace audit only: current165Protocol Main,175 physical metadata,64 layouts/69named types/five independent fixtures, exact152 scope reuse and source/tool differences. H-G13.01 permits READ/STATIC/DOCUMENT_SCOPE only; no product fixture/DB/native/Root/held four classes, old successful tests replays, private reflection or external actions. Trace completeness is separate from all-product quality; enumerate known raw misses by actual owner and retain unresolved conditions. Close original .75 work row only if all trace gaps are resolved, not original G13 parent.'
values=dict(build_context(group_id=group,category='CONTRACT_AUDIT',kind='ORIGINAL_PLAN',scope=scope,oracle_refs=[ref(spec),ref(d/'006_SSC447群終了・元項目不足対応.json')]),source='7123bb3bc8319cfadea41e5be38a75e825e5c14c',headAtStart=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),wbsLeafIds=['WBS-G13.01'],managementPlan='WBS66-58-20261117-SHORTTERM',managementWorkIds=['WBS-G13.01'],estimateAtGroupStartPp=estimate,groupCapPp=2,originalRow=row,holdOriginal=hold,actualAllocatedPp=None,tokenTotals=None,newAcceptance=0,nextCommand='Build current-source165/physical175/64-layout/69-type/requirement/TestID trace; reuse old152 only with exact unchanged inputs, preserve known4M58B gaps and all product/HOLD conditions; independent post before row completion.')
event=append_start(group,values,sys.argv[1],digest(q),datetime.datetime.now(datetime.timezone.utc).isoformat());target=d/'027_G1301追跡監査群開始.json';target.open('x').write(json.dumps(dict(actualExit=0,eventId=event,groupId=group,values=values,quota=q),ensure_ascii=False,indent=2)+'\n')
for name in ['checkpoint.json','continuation-gate.json','cost-ledger.json']:
 p=s/name;v=json.loads(p.read_text());v.update(phase='WBS66_ACTIVE',lastEventId=event,ordinaryActiveGroup=group,ordinaryGroupNotYetClosed=True,currentQuota=q,executionAllowed=True,newImplementationAllowed=True,mayFinishTurn=False,nextCommand=values['nextCommand'],latestWbs66Record=ref(target));p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(actualExit=0,event=event,estimate=estimate,cap=2,holdDisposition='READ_STATIC_DOCUMENT_ONLY'))) 
