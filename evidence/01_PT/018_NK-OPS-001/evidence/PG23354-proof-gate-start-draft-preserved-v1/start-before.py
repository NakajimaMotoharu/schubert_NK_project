from pathlib import Path
import json,hashlib,datetime,subprocess
from pmo_quota_binding import append_start,digest
from pmo_group_context import build_context
r=Path.cwd();b=r.parent/'PMO/pgpt-completion-stage-20261102';p=r/'evidence/01_PT/018_NK-OPS-001/3748_通常PT候補の既資格二重確認防止_仕様.md';assert not p.exists();p.write_text('''# 通常PT候補の既資格二重確認防止・限定是正仕様

WBS-F03 / BUG2484・YKT2222予定、原再資格群4310→4311の費用/原見積/実4PT/元eventは保持。UserOutcome三sourceは原source-reuse-matrixにも同sourceSHAでFOUR100/NATURAL_ZEROの既subproofがあり、着手前にoriginal matrixを照合しなかった。unique453/正式1964-53/新leaf0は元から不加算だが、newDirectWholeSourceProof3という新規含意を訂正し、current run Code proof3・既境界再資格4・新規source資格0と分離する。source/resultを消さず追記訂正とする。

metadata-only：不変原932 matrix、既PG20458索引50、PG23274名前候補87、現在pending7、今回23334 post、原matrixで示す二つの既post公開JSONを有限照合。元exec/XML/class/原Test・archive・private rawを再読/再演しない。新Main/Test/JVM/compiler/Unit/coverage実行0。既proofのpath/hash/source/counter現物を保存し、原値のproofを合格へ変換しない。API等全HOLDを維持。

input406は候補着手の優先規則を生成：原counter完全(FOUR100/NATURAL_ZERO)でcurrent sourcehash一致なら旧証跡再利用調査優先・確認目的Unitを選ばない、partial/no-code/known-candidate/pendingは実既proofを先に照合、NOT_IN_CURRENTだけで未実装/未試験を断言しない。未知/欠測は資格へしない。拒否対象/四heldはmetadataのみ・Unit対象へしない。新規sourceを指す三文字名/同姓source衝突も拒否。

独立407は元matrix932/原status内訳、三重複SHA/原post SHA/currentCode・counter一致とcurrentTest異sourceという歴史差を照合、無変更確認再実行を要求しない。unknown/new-source=1や既counter=新規成果という誤選定をmetadataの反例で拒否する。全名簿93の資格をこの有限修正で宣言しない。stage pendingの当三はrequalified側へ移し、元pending四は保持、暫定93/原282交差73・残209/partial18・残62/unique453/新leaf0/工数nullは不変。

着手前0.5/1/3pp cap4、通常PTの計画重複予防是正として費用別記(返金/成功取消無し)。既BUG台帳最終番号を確認後に起票し修正、fresh group末を実post終端後に取得。次は既counter/候補/新pendingを照合済みで本当に未証明の独立範囲一つを選ぶ。通常commit/報告では停止せず477継続。
''');q=json.loads(Path('/tmp/pgpt-existing-proof-gate-quota.json').read_bytes());receipt=b/'start-quota-PG23348.json';assert not receipt.exists();receipt.write_text(json.dumps(q)+'\n');group='PGPT-EXISTING-WHOLE-PROOF-REPLAY-PREVENTION-20261108';ctx=build_context(group_id=group,category='STATIC_METADATA',kind='REWORK',scope=p.read_text(),oracle_refs=[dict(path=str(p.relative_to(r)),sha256=hashlib.sha256(p.read_bytes()).hexdigest())]);v=dict(ctx,wbsRevision='WBS-v2-20261007-PMO',costRevision='WBS-cost-v2-20261007-PMO',wbsLeafIds=['WBS-F03'],source=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),productionCoreMain='7aed8eace7c844c2f79f2e39db766faf914890d5',estimateAtGroupStartPp=dict(low=.5,base=1,high=3),capPp=4,newAcceptance=0);event=append_start(group,v,receipt,digest(q),datetime.datetime.now().astimezone().isoformat());out=r/'documents/400_PGPT/470_PMO/600_通常PGPT_20261106/283_既資格再確認防止是正着手.json';assert not out.exists();out.write_text(json.dumps(dict(groupId=group,eventId=event,**v),ensure_ascii=False,indent=2)+'\n')
for name in ['checkpoint','cost-ledger','continuation-gate']:
 p=b/(name+'.json');m=json.loads(p.read_bytes());assert m['ordinaryActiveGroup'] is None;m.update(ordinaryActiveGroup=group,ordinaryGroupNotYetClosed=True,mayFinishTurn=False);p.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
print(event,group)
