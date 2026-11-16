"""Existing F03 row continuation: bind raw two-site correction before any production edit."""
from pathlib import Path
import datetime
import hashlib
import json
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

r=Path.cwd();sys.path[:0]=[str(r/'tools/quality'),str(r/'tools/quality/vm/050_s1')]
from pmo_group_context import build_context
from pmo_quota_binding import append_start,digest
b=r/'evidence/01_PT/018_NK-OPS-001';d=r/'documents/400_PGPT/470_PMO/601_WBS66短期実行_20261117'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p))
path='src/schubert-nk-batch/src/main/java/dev/codex/schubert/nk/batch/file/BackupStartIntentFiles.java'
report=b/'evidence/PG36848-ssc449-fresh-sibling-spotbugs-v1/batch-spotbugs.xml'
assert report.exists()
bugs=ET.parse(report).getroot().findall('BugInstance')
assert sorted(x.get('type') for x in bugs)==['DMI_HARDCODED_ABSOLUTE_FILENAME','US_USELESS_SUPPRESSION_ON_METHOD']
assert all(x.find('Method').get('classname').endswith('.BackupStartIntentFiles') for x in bugs)
ledger=r/'documents/900_OTHER/910_台帳';bug=ledger/'915_障害表.md';ykt=ledger/'916_横展開管理台帳.md'
assert max(map(int,re.findall(r'^## BUG-?(\d{3,4})(?!\d)',bug.read_text(),re.M)))==3136
assert max(map(int,re.findall(r'^## YKT-?(\d{3,4})(?!\d)',ykt.read_text(),re.M)))==2607
spec=b/'4457_F03固定Path静的是正仕様.md';assert not spec.exists()
spec.open('x').write('# 固定Pathの評価位置と原静的設定\n\nF03既存行2.4ppの継続・cap5、追加価格0。BackupStartIntentFiles.createServiceの固定Path.ofをacquire lambdaから既存注釈のfactory本体へ移すだけ。現createPublicationと同じ構造、全nonnull/owner/state/context recheck後かつResourceScope呼出前に純粋Path値を構築する。固定文字列/選択/所有/全port構築前提/FD取得後処理/全既注釈/全Test本文を保持。LinuxDirectoryCalls.createとopenは従来どおりacquire内、public API/実外部仕様不変。新suppressionや除外/flag緩和0。SS343 SSC137/308より詳細な局所実装判断で設計変更不要。\n\n正常oracle: 原Java tokenを当一式だけ逆展開し完全一致、固定path字面/既抑制の値・matchType・justification不変、全Testsource不変、Root Main477コンパイル成功/六publicAPIではなく当publicABIを旧版へ比較、他全physical不変、原SB全physical/error/missing0と二指摘0を確認。PMDは変更methodのsource位置を新同sourceへ分類。新コードのcreateService通常PT/native/実intent操作は別に未実施/HOLDを保持し、静的成功でPASS/rawや元項目全体へ混ぜない。\n')
q=json.loads(Path(sys.argv[1]).read_text());group='PGPT-WBS66-F03-BACKUP-STATIC-20261117'
estimate=json.loads((d/'022_F03六module静的群開始.json').read_text())['values']['estimateAtGroupStartPp']
values=dict(build_context(group_id=group,category='IMPLEMENTATION',kind='REWORK',scope=spec.read_text(),oracle_refs=[ref(spec),ref(report)]),source='84d9d3eda489c89c522ff4a4785a12c4c5a51f20',headAtStart=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),wbsLeafIds=['WBS-F03'],managementWorkIds=['WBS-F03/2-2'],estimateAtGroupStartPp=estimate,groupCapPp=5,sameExistingUnfinishedPriceNotAdditional=True,completedOriginalRowPricePp=0,newAcceptance=0,nextCommand='Correct only fixed Path evaluation location, preserve every annotation and original tests, then frozen-source original477 Main compile and full fresh-sibling static. No actual createService/native/intent operation.')
event=append_start(group,values,sys.argv[1],digest(q),datetime.datetime.now(datetime.timezone.utc).isoformat())
(d/'044_F03固定Path是正群開始.json').open('x').write(json.dumps(dict(actualExit=0,eventId=event,groupId=group,values=values,quota=q),ensure_ascii=False,indent=2)+'\n')
texts=[(bug,'## BUG-3137 固定Path式がlambda内となり既承認抑制の対象methodと不一致\n\nPG/PT発見2026-11-17、低/高。対象BackupStartIntentFiles.createService/lambda$createService$0、F03-STATIC-BACKUP-001。期待SS343固定startup namespaceを既注釈のfactoryで表現し原SB0。実際PG36848でDMI_HARDCODED_ABSOLUTE_FILENAMEとUS_USELESS_SUPPRESSION_ON_METHOD各1、SB全646ClassStats/missing/errors0。原因Path.of式だけがlambda synthetic methodへ移り、既承認注釈は外側に残った。固定Path値だけを既context recheck後/acquire前のlocalへ保持し、取得port/全副作用順/字面/既注釈/全Testを変えず是正。YKT2608/SS343 SSC137308/354/F03、実操作PTと品質全体は未受入、修正commit/再試験/証跡/完了未確定、修正前OPEN。'),(ykt,'## YKT-2608 BUG3137 固定Pathと既抑制methodの評価位置\n\n共通原因=固定Path.ofがacquire lambda内。対象BackupStartIntentFilesのcreate/createPublication/createService全三factoryと既PG36848全Batch646結果。createはclosed targetの変数path、createPublicationは既outer localで非該当、createServiceだけouter fixed localへ是正する。全Test/注釈token不変・原Root/全physicalSBとABI/他byteの追加品質で確認、当source通常createService/native/intent/HOLDは代替0。検索だけclose禁止、関連commit/再試験証跡未実施、OPEN。')]
for p,text in texts:
    title,body=p.read_text().split('\n',1);p.write_text(title+'\n\n'+text+'\n'+body)
print(json.dumps(dict(actualExit=0,event=event,bug='BUG3137',ykt='YKT2608',extraPricePp=0)))
