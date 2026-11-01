#!/usr/bin/env python3
"""IT仕様のJSON整合監査と派生Markdown生成だけ。製品/試験/環境/外部commandは起動しない。"""
from pathlib import Path
import collections
import hashlib
import json
import re
import os
import sys
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'documents/500_IT'
def read(n):return json.loads((OUT/'data'/n).read_text())
def write(n,s):
 p=OUT/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s.strip()+'\n')
def esc(x):return str(x).replace('&','&amp;').replace('<','&lt;').replace('>','&gt;').replace('[','&#91;').replace(']','&#93;').replace('|','\\|').replace('\n','<br>')
def sha(b):return hashlib.sha256(b).hexdigest()
pack=read('cases.json');cases=pack['cases'];conditions=read('conditions.json');trace=read('assertion-trace.json');bindings=read('bindings.json');issues=read('issues.json');layouts=read('layouts.json');baseline=read('baseline.json')
caseidx={c['id']:c for c in cases};condidx={c['id']:c for c in conditions};bindidx={b['id']:b for b in bindings};issueidx={i['id']:i for i in issues}
errors=[]
def check(ok,msg):
 if not ok:errors.append(msg)
check(len(caseidx)==len(cases),'case ID重複')
check(len(condidx)==len(conditions),'condition ID重複')
check(set(t['condition_id'] for t in trace)==set(condidx),'条件→trace集合不一致')
check(len(layouts)==64 and len({x['id'] for x in layouts})==64,'layout集合64不一致')
covered={l for c in cases for l in c.get('covered_layouts',[])}
check(covered=={x['id'] for x in layouts},'64layout→実経路case対応不一致')
check(all(x['max_total']==256+x['data']+x['record']*x['max_count'] for x in layouts),'layout総長計算不一致')
ss323=next((ROOT/'documents/300_SS').rglob('323*.md')).read_text()
ss_layouts=set(re.findall(r'^\| `([A-Z0-9]{8})` \d[\d,]*/',ss323,re.M))
check(ss_layouts==covered,'SS323/UI233 layout集合不一致')
required=['purpose','source_refs','route','components','contract','environment_profile','fixture','precondition_addendum','inputs','operation','synchronization','fault_and_concurrency','repetitions','assertions','forbidden_effects','observation','judgement','timeout','abort_and_preservation','cleanup_and_rerun','automation_and_missing','spec_status','execution_state','execution_blockers','ss_condition_ids']
for c in cases:
 for f in required:check(f in c and c[f] is not None and (c[f]!=[] or f=='ss_condition_ids'),c['id']+' mandatory '+f)
 check(c['execution_state']=='NOT_EXECUTED',c['id']+' executed/PASS混入')
 check(c['common_profile'] in pack['profiles'],c['id']+' profile不存在')
 for r in c['source_refs']:check((ROOT/r['document']).is_file(),c['id']+' source ref不存在')
 for a in c['assertions']:check(bool(a['expected']) and bool(a['evidence']),c['id']+' assertion/evidence欠落')
 for i in c['execution_blockers']:check(i in issueidx,c['id']+' blocker不明 '+i)
 if c['decision_issues'] and c.get('lifecycle')!='SUPERSEDED':check(c['spec_status']=='PENDING_DECISION',c['id']+' TBDありCONFIRMED')
 for cid in c['ss_condition_ids']:check(cid in condidx,c['id']+' condition不明')
for cond in conditions:
 check(cond['classification'] in ['IT_CASE','PT_AND_IT_CONTRACT','ST_OT','NOT_APPLICABLE','OPEN'],cond['id']+' 分類不明')
 check(sha(cond['text'].encode())==cond['text_sha256'],cond['id']+' 原文hash不一致')
 if cond['binding_id']:check(cond['binding_id'] in bindidx,cond['id']+' binding不明')
 if cond['classification'] in ['IT_CASE','PT_AND_IT_CONTRACT']:check(bool(cond['binding_id']),cond['id']+' 対応caseなし')
 if cond['classification']=='NOT_APPLICABLE':check(bool(cond['reason']),cond['id']+' 適用外理由なし')
for b in bindings:
 for link in b['links']:
  tid=link['test_id'];check(tid in caseidx,b['id']+' case不明')
  if tid in caseidx:check(set(link['assertion_ids'])<=set(a['id'] for a in caseidx[tid]['assertions']),b['id']+' assertion不明')
for x in read('default-it-crosscheck.json'):
 check(bool(x['test_ids']),x['source']+' 既定IT対象なし')
 for tid in x['test_ids']:check(tid in caseidx,'既定IT ID不明')
# 本文に具体的期待値のない単純合否句を独立assertionとして置かない。
for c in cases:
 for a in c['assertions']:check(a['expected'].strip() not in ['正常終了','設計どおり','エラーになる'],c['id']+' 抽象oracle')
# 書誌hashは固定commit参照を維持。現在の実装worktreeへアクセスしない。
for r in baseline['documents']:
 if r['kind']=='DESIGN':check(sha((ROOT/r['path']).read_bytes())==r['sha256'],'設計基準hash drift '+r['path'])
vols={
 'interface':('521_インターフェース.md','インターフェース'),
 'transaction':('522_トランザクション・データ.md','トランザクション・データ'),
 'security':('523_認証・権限・セキュリティ.md','認証・権限・セキュリティ'),
 'file':('524_ファイル・メディア・Range.md','ファイル・メディア・Range'),
 'operations':('525_運用・復旧・監視.md','運用・復旧・監視'),
 'async':('526_MQ・非同期・容量.md','MQ・非同期・容量'),
 'performance':('527_性能・資源・Logout混在.md','性能・資源・Logout混在')}
casefile={c['id']:vols[c['domain']][0] for c in cases}
def clink(tid,prefix='../520_ケース/'):
 return f'[{tid}]({prefix}{casefile[tid]}#{tid.lower()})'
for domain,(filename,title) in vols.items():
 lines=[f'# {title} 結合テストケース','', '編集正本は [cases.json](../data/cases.json)。この巻は自動生成。全件NOT_EXECUTED。', '', '全ケースは [512](../510_方針・準備/512_結合構成・環境・データ.md) の経路・環境・fixture・観測・C-ISOLATE と [541](../540_実行・管理/541_Codex実行・判定・証跡・再開.md) を参照する。共通CP-BASEの入力以外の初期状態・証跡・中断・後片付けは cases.json.profiles に一元化し、個別追加条件と併せて必須とする。', '', '他巻：'+' / '.join(f'[{v[1]}]({v[0]})' for v in vols.values()),'']
 for c in [x for x in cases if x['domain']==domain]:
  if c.get('lifecycle')=='SUPERSEDED':
   lines += [f'<a id="{c["id"].lower()}"></a>',f'## {c["id"]}（統合済・実行対象外）','', '継続先：'+clink(c['superseded_by'],prefix='')+'。'+c['supersession_reason'],''];continue
  lines += [f'<a id="{c["id"].lower()}"></a>',f'## {c["id"]} {c["title"]}','',f'仕様：**{c["spec_status"]}** ／ 実行：**NOT_EXECUTED** ／ 共通条件：CP-BASE。','',c['purpose'],'','| 項目 | 個別仕様（CP-BASEへ追加） |','|---|---|']
  for label,key in [('結合経路・部品','route'),('確認契約','contract'),('必要環境','environment_profile'),('artifact/設定/schema/data版','fixture'),('事前条件・依存','precondition_addendum'),('同期・待機','synchronization'),('故障注入・並行・再現','fault_and_concurrency'),('反復','repetitions'),('timeout・中断','timeout'),('副作用禁止','forbidden_effects'),('観測方法','observation'),('判定式','judgement'),('失敗保全','abort_and_preservation'),('後片付け・再実行','cleanup_and_rerun'),('自動化・未作成工具','automation_and_missing')]:lines.append(f'| {label} | {esc(c[key])} |')
  lines += ['', '**根拠文書・節・承認変更**','']
  for r in c['source_refs']:
   rel=os.path.relpath(ROOT/r['document'],OUT/'520_ケース')
   lines.append(f'- [{Path(r["document"]).name}](<{rel}>) {r["sections"]} ／ {r["approved_changes"]} ／ commit `{r["commit"][:12]}`')
  lines += ['',f'意味監査：{c.get("semantic_review")}。条件ID：JSONの `ss_condition_ids`（{len(c["ss_condition_ids"])}件）。旧candidateは参照候補のみ、充足認定禁止。[531](../530_追跡/531_SS条件対応・網羅性.md)から原文・工程分類を確認。','', '**入力・初期状態差分**','','```json',json.dumps(c['inputs'],ensure_ascii=False,indent=2),'```','','**操作順序・入口**','',c['operation'],'CP-BASEの予約→初期化→観測開始→一回操作→後条件採取→判定→後片付けを適用。','','**期待結果・取得証跡**','','| Assertion | 値・件数・順序・状態・非更新の期待 | 観測/証跡 |','|---|---|---|']
  lines += [f'| {a["id"]} | {esc(a["expected"])} | {", ".join(a["evidence"])}。実測/path/SHA/判定式はattemptへ記録 |' for a in c['assertions']]
  lines += ['', '**実行可能条件・不足**','', ', '.join(c['execution_blockers'])+' を全解除。判断待ち：'+(', '.join(c['decision_issues']) or 'なし（開始依存・工具準備は別途必要）')+'。[543](../540_実行・管理/543_未確定・不足・開始依存.md) の解除証拠を確認。','']
 write('520_ケース/'+filename,'\n'.join(lines))
# bindingは一度だけ表示し、条件表から参照。
b_lines=['# SS条件とケースの契約binding','', '自動生成。原文条件はconditions.json、assertion本文はcases.json。内部詳細はPT、ここでは実結合契約の範囲を示す。候補が同じ節は共通bindingを使用し、実行済み/網羅性認定を意味しない。','']
for b in bindings:
 b_lines += [f'<a id="{b["id"].lower()}"></a>',f'## {b["id"]}','','| Test ID | 経路 | Assertion | 証跡 |','|---|---|---|---|']
 for l in b['links']:b_lines.append('| '+clink(l['test_id'])+' | '+l['route']+' | '+','.join(l['assertion_ids'])+' | '+','.join(l['evidence_profiles'])+' |')
 b_lines+=['']
write('530_追跡/532_契約binding.md','\n'.join(b_lines))
classes={'IT_CASE':'ITケースで検証','PT_AND_IT_CONTRACT':'PT詳細＋IT結合契約','ST_OT':'ST/OT（PGPT開始依存も維持）','NOT_APPLICABLE':'適用外（文書管理/由来）','OPEN':'未確定/不足/開始依存'}
bydoc=collections.defaultdict(list)
for c in conditions:bydoc[c['document']].append(c)
for doc,rows in bydoc.items():
 n=Path(doc).name[:3];lines=[f'# SS{n} 条件対応表','',f'基準：{baseline["design_commit"]} ／ [{Path(doc).name}](<{os.path.relpath(ROOT/doc,OUT/"530_追跡/conditions")}>)','', '条件原文・原行・SHA・理由・承認/変更IDは [conditions.json](../../data/conditions.json)。条件IDは文書・節・原文hash由来で、追加時も連番振替をしない。', '', '| 条件ID / source行 | 節・条件抜粋 | 工程分類 | 契約binding / 開始依存 |','|---|---|---|---|']
 for c in rows:
  bind=f'[{c["binding_id"]}](../532_契約binding.md#{c["binding_id"].lower()})' if c['binding_id'] else ','.join(c['blocking_issues'])
  if c.get('contract_ids'):bind=', '.join(f'[{k}](../533_契約別意味監査.md#{k.lower()})' for k in c['contract_ids'])
  excerpt=c['text'].replace('\n',' ')[:85]
  lines.append(f'| {c["id"]} / L{c["line"]} | {esc(c["section"].split(" > ")[-1])}：{esc(excerpt)} | {classes[c["classification"]]} | {bind} |')
 write(f'530_追跡/conditions/SS{n}.md','\n'.join(lines))
counts=collections.Counter(c['classification'] for c in conditions);extents=collections.Counter(c['coverage_extent'] for c in conditions)
lines=['# SS条件対応・網羅性照合','', 'SS301と全24 Markdownを対象に段落・箇条書き・表の設計行・コード塊を棚卸しした。節題/表header/更新履歴等を実行case数へ加算しない。条件IDには原文hashを含め、原文とsource行を保持する。これはSS上の要件IDを勝手に再採番するものではない。','', '条件→結合点/観点→Test ID→Assertion/期待結果/証跡は、conditions.json.contract_ids → contracts.json.scenario_ids → scenarios.json.assertion_evidence/cases.json.assertions の参照。binding_idは一部indexのみで全契約集合ではない。Markdownはその派生表示である。PT内部詳細とIT結合契約を分離し、古いsource限定の復旧指示を新環境の操作へ複写しない。', '', '| 分類 | 条件ブロック数 |','|---|---|']
lines += [f'| {classes[k]} | {v} |' for k,v in sorted(counts.items())]
lines += ['', 'この数は独立した要件の個数・IT合格率ではない。各章の共通条件を複数の部品で再記述したblockも保持している。IT_CASEは直接契約の仕様割当、PT_AND_IT_CONTRACTは内部詳細のPT＋実結合の仕様割当で、実行実績は全件NOT_EXECUTED。START_DEPENDENCYは最終source・承認・PGPT残件の照合待ち。','', '## SS文書別の棚卸しと工程配分','', '| SS文書 | 全block | IT | PT＋IT | ST/OT | 適用外 | 未確定/開始依存 |','|---|---:|---:|---:|---:|---:|---:|']
for doc,rows in bydoc.items():
 ct=collections.Counter(r['classification'] for r in rows);n=Path(doc).name[:3]
 lines.append(f'| [SS{n}](conditions/SS{n}.md) {Path(doc).name[4:]} | {len(rows)} | '+ ' | '.join(str(ct[k]) for k in ['IT_CASE','PT_AND_IT_CONTRACT','ST_OT','NOT_APPLICABLE','OPEN'])+' |')
lines += ['', '## SS354/362の既定ITと具体ケース','', '| 既定条件 | ケース | 残る判断 |','|---|---|---|']
for d in read('default-it-crosscheck.json'):
 lines.append('| '+d['source']+'（意味監査PARTIAL・明示SC '+str(len(d.get('explicit_scenario_ids',[])))+'） | '+', '.join(clink(t) for t in d['test_ids'])+' | '+(','.join(d['remaining_issues']) or '開始gate/工具のみ')+' |')
lines += ['', '## 対応漏れ・参照だけの検出','',f'旧構造分類OPEN_COVERAGE={extents["OPEN_COVERAGE"]}、未確定oracleのみを参照する条件={extents["SPEC_PENDING"]}。後者は [coverage-gaps.json](../data/coverage-gaps.json) に個別抽出し、割当ありでも仕様充足へ算入しない。意味未照合のUNVERIFIED_REFERENCE・原文残句は別途残り、OPEN_COVERAGE=0でも未充足0とは扱わない。case/condition/binding/Assertion/証跡の不明参照はvalidation-report.jsonに記録する。契約bindingが存在しても、内部PTの全分岐やsectionの全literalを直接IT検証したとは認定しない。PT条件は既存PT ID/最終証跡を開始前に照合する。', '', '未確定caseの参照だけではその条件を仕様確定済み・実行可能へ数えない。ISS-DATA/TIME/MQCAP/DISK/EMPTY/STREAM/TRANSFER/CONFIG/METRIC/JOURNALは543へ集約した。特定source/PID/原本の復旧条件はSTART_DEPENDENCYに分離し、一般のowner/UNKNOWN/非更新はOPSケースで確認する。', '', '設計tableの全field/offset/constructor/Throwable graphはPTへ、実BytesMessage・grant・DB/JMS原子性・FS公開・OS実所有はITへ分担。全画面互換/24CHRのUI受入はST、RD適合/Go判断はOT。性能/容量/復旧/securityの既定IT項目は削除0。','', '## 64layout対応','', '| Layout | IF | bytes（data/record/max/total） | 結合ケース |','|---|---|---|---|']
for x in layouts:lines.append(f'| {x["id"]} | {x["interface"]} | {x["data"]}/{x["record"]}/{x["max_count"]}/{x["max_total"]} | {clink(x["test_id"])} |')
write('530_追跡/531_SS条件対応・網羅性.md','\n'.join(lines))
gaps=[{'condition_id':c['id'],'document':c['document'],'section':c['section'],'line':c['line'],'reason':c['reason'],'issues':c['blocking_issues'],'binding_id':c['binding_id']} for c in conditions if c['coverage_extent'] in ['SPEC_PENDING','OPEN_COVERAGE','UNVERIFIED_REFERENCE','CONTRACT_SLICE','CONTRACT_SLICE_PENDING']]
(OUT/'data/coverage-gaps.json').write_text(json.dumps(gaps,ensure_ascii=False,indent=2)+'\n')
# open issuesはJSON唯一正本
lines=['# 未確定事項・準備不足・IT開始依存','', 'issueの状態は個別欄とJSONを正とする。決定・解消は証拠/承認/更新reviewの後に行う。依存解除は仕様作成/PGPT完了/IT実行可能/IT合格を別々に判定する。JSON正本：[issues.json](../data/issues.json)。','']
for i in issues:
 lines += [f'## {i["id"]} {i["title"]}','',f'分類：{i["type"]} ／ 状態：{i["status"]} ／ 担当：{i["owner_role"]}','',f'根拠：{i["basis"]}','',f'影響：{i["affected_description"]}。機械影響リスト：{len(i["affected_test_ids"])}ケース（JSON参照）。', '', f'必要判断/解除証拠：{i["required_decision_or_evidence"]}', '', '解消記録：'+str(i.get('resolution') or '未解消。'),'']
write('540_実行・管理/543_未確定・不足・開始依存.md','\n'.join(lines))
report={'type':'DOCUMENT_STRUCTURE_AUDIT_ONLY','product_tests_executed':False,'design_commit':baseline['design_commit'],'implementation_reference_source':baseline['implementation_source'],'counts':{'cases':len(cases),'assertions':sum(len(c['assertions']) for c in cases),'conditions':len(conditions),'ss_documents':len(bydoc),'layouts':len(layouts),'spec_confirmed':sum(c['spec_status']=='CONFIRMED' for c in cases),'spec_pending':sum(c['spec_status']!='CONFIRMED' for c in cases),'executed':0,'open_coverage':extents['OPEN_COVERAGE'],'open_issues':sum(i['status']=='OPEN' for i in issues),'oracle_pending_condition_blocks':extents['SPEC_PENDING'],'bindings':len(bindings)},'condition_classifications':dict(counts),'coverage_extents':dict(extents),'errors':errors,'result':'PASS' if not errors else 'FAIL','limitation':'文書の構造/参照/集合/必須field/数値式の監査。製品・PT・ITの試験結果や全条件の意味的網羅性認定ではない。'}
(OUT/'data/validation-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
review=read('review-findings.json')
reviewlines=['# IT仕様書 自己レビュー結果','', 'レビュー日：2026-11-02 JST。担当：Codex（同一作成者による自己レビュー。独立承認・製品試験ではない）。', '', '**成果物一式の作成と構造レビューは完了。全ケースの仕様確定という完了条件は未達。IT実行は開始できない。** 判断待ちを実装挙動で埋めず、確定部分と分けた。', '', '| 指標 | 結果 |','|---|---|',f'| 参照設計 | origin/main `{baseline["design_commit"]}` |',f'| 実装補助source | dev-foundation `{baseline["implementation_source"]}`。初回49feと区別 |',f'| SS棚卸し | {len(bydoc)}文書 / {len(conditions)}設計・管理block（要件数/合格率ではない） |',f'| ケース/Assertion | {len(cases)} / {report["counts"]["assertions"]} |',f'| 仕様確定/判断待ち | {report["counts"]["spec_confirmed"]} / {report["counts"]["spec_pending"]} |',f'| layout | 64/64を31往復＋2内部eventへ割当 |',f'| 未割当 / 未確定oracleのみの条件 | {extents["OPEN_COVERAGE"]} / {extents["SPEC_PENDING"]}。後者は充足扱い0 |',f'| 開始依存block | {extents["START_DEPENDENCY"]}。特定source復旧/PGPT/CHR等、実行免除ではない |',f'| 文書構造監査 | {report["result"]} / errors {len(errors)}。[validation-report](../data/validation-report.json) |','| 製品/PT/IT実行 | 0、全ケースNOT_EXECUTED |','', '## 完了条件の照合','', '| 条件 | 評価・残る制約 |','|---|---|','| SS全体の対応先 | 原文/行/hash/節/変更IDを保持し、IT/PT＋IT/STOT/適用外/未確定へ全件分類。構造未割当0は意味的全充足を証明しない。内部詳細はPT完了証跡、未確定oracle条件は判断待ちとして残す |','| 結合経路/観測 | R-SYNC/FILE/MEDIA/ASYNC/WLOG/SESSION/OPS/RESTOREとO-*を指定。実process/UID/journal/DB/FS/Unitが必須。mock/proxyだけの受入不可 |','| 入力/順序/期待/後条件/証跡 | 確定ケースは値・件数・順序・code・非更新・barrier・timeoutを記載。判断待ちケースの全件確定は不可 |','| Codex実行準備 | fixture/driver/failpoint/SQL/collector/load/oracle/resume全T-*がUNIMPLEMENTED。存在確認済みPGPT工具は用途・副作用を明記しIT commandを捏造0 |','| 未確定と影響 | issues.jsonでcase/conditionを逆引き。131blockは未確定case参照だけを抽出。QA051等の上位判断を推測しない |','| NG/再試験/回帰/復旧 | 六分類、原失敗保全、914/915/916/911〜913の用途、影響graph/再試験attempt/cleanup/UNKNOWNを定義 |','| 工程境界・既定品質 | SS354/362の性能/容量/復旧/security/QA050を保持。ST/OTの独立判定と証跡共用条件、PGPT移管による免除禁止を明記 |','| IT開始前再照合 | 最終SS/最終release/PGPT同source完了/464残件/環境/toolの差分→更新→review→gateが必要。今回は未実施 |','', '## 指摘と是正','', '| 指摘ID | 内容 | 対応 | 状態 |','|---|---|---|---|']
for r in review:reviewlines.append('| '+r['id']+' | '+esc(r['finding'])+' | '+esc(r['action'])+' | '+r['status']+' |')
reviewlines += ['', '## 判断待ちケース（CONFIRMEDへ算入しない）','', '| Test ID | 未確定 |','|---|---|']
for c in cases:
 if c['spec_status']!='CONFIRMED':reviewlines.append('| '+clink(c['id'])+' | '+','.join(c['decision_issues'])+' |')
reviewlines += ['', '## 検査範囲と限界','', 'JSON必須field、case/condition/binding/assertion/issue参照、全64layout集合・長さ式、SS正本文書hash、実行結果混入0を検査した。代表手計算はGAM809byte、SRC2record11472byte、SCN3record16384byte、201record964800byte、Range1MiB境界・suffix/HEAD。case件数やコードcoverageで網羅性合格を認定していない。', '', '本レビューのPASSは文書構造監査だけ。意味的な仕様全件確定、PGPT完了、環境利用承認、IT開始可能、IT合格を意味しない。SS補足の内部例外graph/生成要素/詳細constructor等はPTへ分担し、最終PT同source証跡を開始前に確認する。特定旧source/PID/原本への限定操作を新ITへ再利用しない。', '', '追加の残件：'+str(report['counts']['open_issues'])+'件OPEN。詳細は[543](../540_実行・管理/543_未確定・不足・開始依存.md)。設計/期待値が未確定なら該当assertionをNOT_JUDGEDのまま保持し、独立確定範囲だけ進める。']
write('550_レビュー/551_仕様書自己レビュー結果.md','\n'.join(reviewlines))
# v2は同一JSON編集正本から意味監査/シナリオ本文を派生生成。
from audit_v2 import render as render_v2
render_v2(ROOT, OUT, report, errors)
# 派生文書のlocal link/明示anchorも検査（snippet原文のMarkdownはescape済み）。
from urllib.parse import unquote
link_errors=[]
for file in OUT.rglob('*.md'):
 for label,url in re.findall(r'\[([^\]\n]+)\]\(([^)\n]+)\)',file.read_text()):
  url=url.strip('<>')
  if url.startswith(('http:','https:','codex:')):continue
  path,sep,anchor=url.partition('#')
  if not path:continue
  target=(file.parent/unquote(path)).resolve()
  if not target.is_file():link_errors.append(str(file.relative_to(ROOT))+': '+url)
  elif anchor and target.is_relative_to(OUT) and f'id="{anchor}"' not in target.read_text():link_errors.append(str(file.relative_to(ROOT))+': anchor '+url)
report['local_link_errors']=link_errors
if link_errors:
 errors.extend(link_errors);report['result']='FAIL'
report['errors']=errors
(OUT/'data/validation-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False,indent=2))
if errors:raise SystemExit(1)
