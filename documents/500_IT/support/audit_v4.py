"""全SSの工程配分/個別bindingと継続自己レビューの派生表示。文書JSONだけを処理する。"""
import json,collections,hashlib,pathlib,re

def read(out,n):return json.loads((out/'data'/n).read_text())
def put(out,n,x):(out/'data'/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def esc(x):return str(x).replace('&','&amp;').replace('<','&lt;').replace('>','&gt;').replace('|','\\|').replace('\n','<br>')
def prepare(root,out):
 rows=read(out,'ss-semantic-review-v3.json');co=read(out,'conditions.json');ci={c['id']:c for c in co};scope={x['id']:x for x in read(out,'semantic-review-scopes-v3.json')};bindings=[b for b in read(out,'bindings.json') if not b['id'].startswith('B3-')];bb=read(out,'semantic-review-bindings-v3.json');bindings+=bb
 cases={c['id']:c for c in read(out,'cases.json')['cases']};ss=read(out,'scenarios.json')
 # bindingsはIDだけを正本として現在のSC/assertion集合へ再解決。レビュー済みhash差はrenderで別拒否。
 for b in bb:
  for link in b['links']:
   c=cases[link['test_id']];link.pop('spec_status',None);link['route']=c['route'];link['scenario_ids']=c['scenario_ids'];link['assertion_ids']=[a['id'] for a in c['assertions']];link['case_spec_status']=c['spec_status'];link['evidence_profiles']=sorted(set(e for a in c['assertions'] for e in a['evidence']));link['extent']='STAGE_ALLOCATION_WITH_EXPLICIT_CONTRACT_SLICES'
 for r in rows:
  z=ci[r['condition_id']];p=scope[r['review_scope']];a=r['primary_allocation']
  z['semantic_status']='REVIEWED_ALLOCATION';z['semantic_review_ref']='ss-semantic-review-v3.json#'+z['id'];z['classification']={'FINAL_SOURCE_RECONCILIATION':'OPEN'}.get(a,a);z['coverage_extent']='START_DEPENDENCY' if a=='FINAL_SOURCE_RECONCILIATION' else ('PROCESS_REVIEW' if a=='NOT_APPLICABLE' else ('UPPER_STAGE' if a=='ST_OT' else 'CONTRACT_SLICE_AND_PT_ALLOCATION'));z['reason']=p['review_reason']+' IT: '+p['it_obligation']+' PT/残句: '+p['pt_remainder'];z['binding_id']=r['binding_id'];z['review_scope']=r['review_scope']
  # 原文引用を保持し、句分割で末尾句点等を追加しない。
  text=z['text'];parts=[text] if text.startswith('|') or '\n' in text else re.split(r'(?<=。)',text);parts=[x for x in parts if x]
  r['clauses']=[{'clause_id':z['id'].replace('SSCOND','SSCLAUSE')+'-'+str(i+1).zfill(2),'source_text':t,'stage_allocation':a,'coverage_extent':'PARTIAL_CONTRACT_SLICE_AND_REMAINDER_ALLOCATION' if r['direct_contract_ids'] else 'STAGE_ALLOCATION'} for i,t in enumerate(parts)]
 put(out,'semantic-review-bindings-v3.json',bb);put(out,'ss-semantic-review-v3.json',rows);put(out,'conditions.json',co);put(out,'bindings.json',bindings)
 put(out,'assertion-trace.json',[{'condition_id':z['id'],'classification':z['classification'],'coverage_extent':z['coverage_extent'],'blocked_by':z['blocking_issues'],'binding_id':z['binding_id'],'contract_ids':z['contract_ids'],'semantic_status':z['semantic_status'],'review_note':z['reason'],'execution_state':'NOT_EXECUTED'} for z in co])

def render(root,out,report,errors):
 def rd(n):return read(out,n)
 def wr(n,x):put(out,n,x)
 def md(n,lines):(out/n).write_text('\n'.join(lines)+'\n')
 cs=rd('cases.json')['cases'];ix={c['id']:c for c in cs};active=[c for c in cs if c['lifecycle']=='ACTIVE'];sc=rd('scenarios.json');sx={s['id']:s for s in sc};ct=rd('contracts.json');co=rd('conditions.json');ci={c['id']:c for c in co};rows=rd('ss-semantic-review-v3.json');scopes=rd('semantic-review-scopes-v3.json');links=rd('semantic-review-bindings-v3.json');issues=rd('issues.json');cont=rd('continuation-audit.json');source=rd('continuation-source-v3.json');b=rd('continuation-baseline.json')
 def ck(v,m):
  if not v:errors.append('V4 '+m)
 ck({r['condition_id'] for r in rows}==set(ci),'全SS review集合')
 ck(len(rows)==len(ci),'review ID重複')
 for r in rows:
  z=ci[r['condition_id']];ck(r['source_sha256']==z['text_sha256'],r['condition_id']+' review原文hash');ck(''.join(x['source_text'] for x in r['clauses'])==z['text'],r['condition_id']+' 残句欠落');ck(r['review_state']=='REVIEWED',r['condition_id']+' review未了');ck(r['remaining_authorable']!='UNCREATED',r['condition_id']+' 作成可能未作成')
  if r['primary_allocation'] in ['IT_CASE','PT_AND_IT_CONTRACT']:ck(bool(r['binding_id']),r['condition_id']+' 実結合bindingなし')
 for r in links:
  for x in r['links']:
   c=ix[x['test_id']];ck(c['lifecycle']=='ACTIVE','historyを実行binding');ck(set(x['scenario_ids'])==set(c['scenario_ids']),x['test_id']+' review SC drift')
 for f in rd('field-oracles-v3.json'):ck(bool(f['bindings']),f['id']+' UIFIELD unbound')
 for c in active:
  ss=[s for s in sc if s['test_id']==c['id']];ck(ss,c['id']+' 明示SC0')
  for s in ss:
   ck(s['execution_state']=='NOT_EXECUTED',s['id']+' 実行混入')
   if s['type']=='競合':ck(s['repetitions']>=100,s['id']+' SS354競合反復不足')
   ck(s['assertion_evidence'],s['id']+' evidence0')
 # 未確定値を実行可能・PASSへ自動変換しない。レビューの適用入力hashを固定した自己レビューが別に必要。
 state=rd('self-review-v3.json') if (out/'data/self-review-v3.json').exists() else {'status':'IN_PROGRESS','completion_criteria':[]}
 current_hashes={n:hashlib.sha256((out/'data'/n).read_bytes()).hexdigest() for n in ['cases.json','scenarios.json','contracts.json','semantic-review-scopes-v3.json','ss-inventory.json','field-oracles-v3.json','config-bindings-v3.json','conditions.json','ss-semantic-review-v3.json','semantic-review-bindings-v3.json','default-it-crosscheck.json','issues.json','http-input-bindings-v3.json','interface-fixture-v3.json','inspector-fixture-v3.json','schema-oracle-v3.json','baseline.json','continuation-source-v3.json','continuation-baseline.json','authoring-rejections-v3.json','review-findings.json','layouts.json','run-template.json','config-oracle.json','design-update-qa051-v3.json','ss-semantic-unassigned-v3.json','../support/render_validate.py','../support/audit_v3.py','../support/audit_v4.py','../510_方針・準備/511_基本方針・工程境界.md','../510_方針・準備/512_結合構成・環境・データ.md','../510_方針・準備/513_工具・故障注入準備仕様.md','../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md','../510_方針・準備/515_継続監査のfixture・probe・故障注入準備仕様.md','../540_実行・管理/541_Codex実行・判定・証跡・再開.md','../540_実行・管理/542_NG・修正・再試験・回帰.md']}
 if state['status']=='REVIEW_COMPLETE_WITH_B_C_D':
  ck(state.get('reviewed_input_hashes')==current_hashes,'自己レビュー入力hash drift')
 completed=state['status']=='REVIEW_COMPLETE_WITH_B_C_D' and state.get('reviewed_input_hashes')==current_hashes and not errors
 stats=cont['current'];stats['active_cases']=len(active);stats['active_assertions']=sum(len(c['assertions']) for c in active);stats['explicit_scenarios']=len(sc)
 cont['overall_state']='SPECIFICATION_EXTENSION_COMPLETE_WITH_B_C_D' if completed else 'IN_PROGRESS';wr('continuation-audit.json',cont);report['continuation']=cont
 perf_ids=[c['id'] for c in active if c['domain']=='performance'];new_ids=[c['id'] for c in active if c['id'] not in b['active_case_ids']] if 'active_case_ids' in b else [z['test_id'] for z in rd('case-changes.json') if z.get('epoch')=='CONTINUATION_20261102' and z['action']=='ADD']
 mid_ids=['IT-DB-001','IT-DB-002','IT-DB-003','IT-MQ-001','IT-MQ-002','IT-MQ-003','IT-MQ-005','IT-MQ-006','IT-MQ-010','IT-MQ-020','IT-MQ-030','IT-MQ-031','IT-MQ-033','IT-MQ-034','IT-MQ-035','IT-NET-001','IT-TX-001','IT-TX-002','IT-TX-003','IT-TX-004','IT-TX-005','IT-TX-006','IT-TX-007','IT-TX-008','IT-TX-009','IT-TX-019','IT-TX-030','IT-TX-050','IT-TX-051','IT-TX-052','IT-TX-053','IT-TX-054','IT-FILE-010','IT-FILE-011','IT-FILE-012','IT-FILE-052','IT-OPS-007','IT-OPS-013','IT-OPS-020','IT-OPS-021','IT-OPS-028','IT-OPS-029','IT-OPS-044','IT-OPS-045','IT-OPS-046','IT-OPS-048','IT-OPS-055','IT-OPS-056','IT-PERF-044','IT-PERF-046','IT-OPS-057']
 perf={'cases':len(perf_ids),'scenarios':sum(s['test_id'] in perf_ids for s in sc),'new_case_ids':[t for t in perf_ids if t in new_ids],'new_cases':sum(t in new_ids for t in perf_ids),'case_ids':perf_ids,'execution_state':'NOT_EXECUTED'}
 mid={'cases':len(mid_ids),'scenarios':sum(s['test_id'] in mid_ids for s in sc),'case_ids':mid_ids,'new_case_ids':[t for t in mid_ids if t in new_ids],'basis':'実在する単一hostの確定点/所有/復旧責務の選定集合。failure全直積・HAを追加しない。MQ005/006は新規caseでなく既存へSC追加。','execution_state':'NOT_EXECUTED'}
 wr('middleware-selection-v3.json',mid)
 dimensions={'case_families':len(active),'explicit_scenarios':len(sc),'assertions':stats['active_assertions'],'historical_SUPERSEDED':sum(c['lifecycle']=='SUPERSEDED' for c in cs),'parameter_rows':{'UI_field_oracles':len(rd('field-oracles-v3.json')),'config_data_rows':len(rd('config-bindings-v3.json')),'config_headers_excluded':25},'repetition_plans':[{'scenario_id':s['id'],'repetitions':s['repetitions']} for s in sc],'planned_scenario_invocations':sum(s['repetitions'] for s in sc),'worker_and_data_dimensions':{'source':'scenarios.json.initial_state/load_plan','rule':'worker/client/data件数は各SCの入力列。case/SC/Assertion/反復単位へ加算しない。入力が語彙別のため合計worker数/合計data件数で網羅率を出さない。'},'performance':perf,'middleware':mid}
 wr('measurement-dimensions-v3.json',dimensions)
 wr('phase-states-v3.json',{'specification_extension':cont['overall_state'],'all_case_specifications_confirmed':False,'PGPT_complete':False,'IT_execution_possible':False,'IT_result':'NOT_EXECUTED','reason':'B条件は未確定、C最終SS/release/PGPT/464照合とD工具/環境/権限/HOLD未解消。設計承認・構造PASS・PT成功から状態を昇格しない。'})
 audit=rd('semantic-audit.json');audit.update(result='REVIEW_COMPLETE_WITH_B_C_D' if completed else 'IN_PROGRESS',all_ss_allocation_reviewed=completed,all_ss_semantic_coverage_certified=completed,coverage_certification_scope='設計基点の工程配分/全残句レビューと具体IT sliceの仕様。全blockをIT充足/PASSとする認定ではない。B該当predicateは未確定、C/Dは実行前依存。',all_cases_executable=False,product_tests_executed=False,performance_detail=perf,middleware_detail=mid,review_result_ref='self-review-v3.json',raw_blocks_reviewed=len(rows),raw_blocks_unread=0,raw_blocks_unclassified=0,authorable_uncreated=0,legacy_case_statuses={},not_applicable_policy='runtime入力でない管理/履歴/根拠のみ。normative引用値は元SS/PT/ITへ再配分。',note='初期4275＋QA051承認12＝4287は原文棚卸しblock数で要件数ではない。各blockの複数句を工程配分、直接IT sliceはPARTIALを維持しPT残句/C/STOTを明示。')
 audit.pop('all_ss_semantic_coverage_certified',None);audit['all_ss_semantic_review_completed']=completed;audit['all_conditions_have_explained_stage']=completed;audit['all_authorable_it_contracts_specified']=completed;audit['all_case_specifications_confirmed']=False;audit['counts']['raw_blocks_not_semantically_confirmed']=0;audit['counts']['raw_blocks_partially_reviewed']=sum(bool(r['direct_contract_ids']) for r in rows);audit['block_status']=dict(collections.Counter(x['semantic_status'] for x in co));wr('semantic-audit.json',audit);report['semantic_result']=audit['result'];report['semantic_review_scope']=audit['coverage_certification_scope']
 # 原文block対応のリンク先は共通binding。同じ値を複数正本に転記しない。
 docs=collections.defaultdict(list)
 for r in rows:docs[pathlib.Path(r['document']).name[:3]].append(r)
 gaps=[{'document':rs[0]['document'],'block_count':len(rs),'reviewed':len(rs),'unread':0,'unclassified':0,'authorable_uncreated':0,'allocations':dict(collections.Counter(x['primary_allocation'] for x in rs)),'contract_slice_blocks':sum(bool(x['direct_contract_ids']) for x in rs),'decision_ids':sorted(set(k for x in issues if x['status']=='OPEN' and x.get('state_class')=='B' and any(cid in {r['condition_id'] for r in rs} for cid in x.get('condition_ids',[])) for k in [x['id']]))} for no,rs in docs.items()]
 wr('block-audit.json',gaps);wr('coverage-gaps.json',[x for x in issues if x['status']=='OPEN'])
 lines=['# 残不足・文書別の意味監査結果','','全SSの原文をレビューし、工程配分と残句の対応を[535](535_SS全件の工程配分・残句レビュー.md)・[構造化台帳](../data/ss-semantic-review-v3.json)へ記録した。blockは要求数ではない。直接IT slice以外を全充足へ自動昇格せず、内部全値/PT、上位STOT、最終source Cを分ける。B/C/Dを解消したことも意味しない。','','| SS | 原文block | レビュー | 未読/未分類/作成可能未作成 | IT slice接続block | 残判断 |','|---|---:|---:|---|---:|---|']
 for z in gaps:lines.append('| SS'+pathlib.Path(z['document']).name[:3]+' | '+str(z['block_count'])+' | '+str(z['reviewed'])+' | 0 / 0 / 0 | '+str(z['contract_slice_blocks'])+' | '+', '.join(z['decision_ids'])+' |')
 lines+=['','旧137caseは全件再監査。新規51caseを独立契約から追加し、基準196の統合/履歴化は0。未採用Journal追加案2件は既存MQ005/006へSC追加として記録し、ケース新規に加算しない。','', '## 残る外部判断・開始依存','','A（作成可能未作成）の残りをB/C/Dへ便宜移管しない。今回抽出したAは具体case/SC/準備仕様へ反映した。以下はレビュー済みの条件単位の残件。','','| ID | 区分 | 判断/準備 | 影響case |','|---|---|---|---|']
 for x in issues:
  if x['status']=='OPEN':lines.append('| '+x['id']+' | '+x.get('state_class',x['type'])+' | '+esc(x['required_decision_or_evidence'])+' | '+', '.join(x['affected_test_ids'])+' |')
 lines+=['','判定predicate単位の影響は[issues.json](../data/issues.json)のaffected_predicates。C/Dは未準備・未完了のまま、工具名を実在commandとしない。BのあるSCは仕様確定/実行可能にしない。'];md('530_追跡/534_残不足・文書別再監査.md',lines)
 lines=['# SS全件の工程配分・残句レビュー','','正本：[原文条件](../data/conditions.json)、[全件レビュー](../data/ss-semantic-review-v3.json)、[レビューscope](../data/semantic-review-scopes-v3.json)、[SC/assertion binding](../data/semantic-review-bindings-v3.json)。同じ設計値は条件/ケース正本を参照し、二重編集しない。','','全24SS/4287blockを読了した。文書・行・SHA・変更IDを保持。句を分けても要求件数の認定には使わない。IT sliceの残句は以下のPT/上位/工程依存へ配分。期待結果そのものは各caseの値・件数・時刻・code・非更新条件と個別証拠を参照する。単なる節番号/関連名の一致をITの合格へしない。','','| review scope | 原文block | 実結合の確認 | PT内部/残句と工程境界 |','|---|---:|---|---|']
 for p in scopes:lines.append('| '+p['id']+' | '+str(len(p['source_condition_ids']))+' | '+esc(p['it_obligation'] or p['review_reason'])+' | '+esc(p['pt_remainder'] or p['final_source_gate'])+' |')
 md('530_追跡/535_SS全件の工程配分・残句レビュー.md',lines)
 # source/preparation/レビューの新巻を一覧へ接続、古い途中報告を現在状態として残さない。
 f=out/'501_IT仕様書一覧.md';t=f.read_text();t=re.sub(r'継続監査(?:中。有効\d+case・\d+Assertion・明示\d+SC。旧137caseの未処理\d+。|：有効\d+case・\d+Assertion・明示\d+SC、旧137再監査済み。)',f'継続監査：有効{len(active)}case・{stats["active_assertions"]}Assertion・明示{len(sc)}SC、旧137再監査済み。',t);t=t.replace('全体はIN_PROGRESS。','最終状態は553と554を参照。')
 for label,link in [('515','510_方針・準備/515_継続監査のfixture・probe・故障注入準備仕様.md'),('535','530_追跡/535_SS全件の工程配分・残句レビュー.md'),('554','550_レビュー/554_全SS意味監査・継続自己レビュー.md')]:
  if '['+label+']' not in t:t+='\n['+label+']('+link+')\n'
 t=t.replace('family/SC/Assertion/反復の別集計、意味レビューはPARTIAL','family/SC/Assertion/反復の別集計とB/C/D別意味レビュー');f.write_text(t)
 f=out/'530_追跡/531_SS条件対応・網羅性.md';f.write_text(f.read_text().replace('以下の4275block表','以下の4287block表'))
 # 551/553は過去の基準192/途中文言を最終自己レビューへ統一。
 summary=['# 継続監査の最終自己レビュー','','全ITはNOT_EXECUTED。実行・環境起動・配備・PG/SS変更0。','', '**'+('仕様書拡充・全SS工程配分レビュー完了（B/C/Dあり）。' if completed else '自己レビュー継続中。')+' PGPT完了・IT実行可能・IT合格は別状態。**','','| 指標 | 021417412基準 | 現在 |','|---|---:|---:|']
 for k,v in cont['baseline'].items():summary.append('| '+k+' | '+str(v)+' | '+str(stats[k])+' |')
 summary+=['',f'新規{cont["new_cases"]}／旧case書換{cont["rewritten_cases"]}／統合0／基準case履歴化0／純増{len(active)-b["active_cases"]}。既存49履歴は実行対象へ加算0。旧137は全件再監査、残るBはSC/判定項目単位。',f'有効case仕様状態：確定{sum(c["spec_status"]=="CONFIRMED" for c in active)}／Bあり{sum(c["spec_status"]!="CONFIRMED" for c in active)}。SC：確定{sum(s["spec_status"]=="CONFIRMED" for s in sc)}／Bあり{sum(s["spec_status"]!="CONFIRMED" for s in sc)}。全case C/Dで現時点実行不可。','',f'性能・容量{perf["cases"]}case/{perf["scenarios"]}SC（今回新規{perf["new_cases"]}case）。選定ミドルウェア/部分失敗{mid["cases"]}case/{mid["scenarios"]}SC。選定IDと確定点はmiddleware-selection-v3、値違いは同family SCへ。前回代表9/18を全体完了とはしない。',f'UI field parameter{dimensions["parameter_rows"]["UI_field_oracles"]}行／config{dimensions["parameter_rows"]["config_data_rows"]}行、予定SC反復単位{dimensions["planned_scenario_invocations"]}。worker/client/data件数はSC入力を別管理し、case数へ加算0。','','## 完了条件','','| 条件 | 判定/根拠 |','|---|---|']
 for x in state.get('completion_criteria',[]):summary.append('| '+x['criterion']+' | '+x['result']+' / '+esc(x['evidence'])+' |')
 summary+=['', '基準196の旧137は書換・再監査、他の既存14caseへ追記/期待訂正（continuation-comparison-v3）。新規とは別計上、作成中不採用案2件は新規/履歴49に加算0。', '', '旧137の内訳は121仕様確定・16条件判断待ち。レビュー未処理0、全caseは実行開始不可。', '', '## 残判断と開始依存','','QA051の二点承認待ちはmain7147で解消。Bはmenu/log_searchの個別caller/cardinality、監査category、field error HTTP、diskBLOCKの外部分類/解除、stream超過code、Transfer先行予約、poolborrow、RPO式、Media検証責務、UUID総試行回数、wait伸長、通知cutoff等。[543](../540_実行・管理/543_未確定・不足・開始依存.md)とissuesの影響SC/predicateで追跡。未確定の期待値を現行実装へ追従しない。','', 'Cは最終SS/承認変更/release artifact/PGPT同source完了/464/trace/QA051承認済比較仕様と未完の実装/比較試験の再照合。Dは専有環境・全T工具実装/校正/fixture生成・権限/承認/HOLD。必要準備の具体仕様は515。原失敗/Unknown所有を削除・再送して解消0。','', 'IT/ST/OT：IT=SS実結合、ST=UI外部全体、OT=RD検収。性能/容量/復旧/securityの既定IT維持。共用は同source/env/fixture/計測窓を説明できるrawだけ、上位合否の転記0。','', '設計正本origin/main `'+source['design_commit']+'`。今回終了側の実装補助source dev-foundation `'+source['implementation_reference']+'`。初回ce284/中間4746・2aef、未配備Production6b53、歴史native/正式1964は混同しない。最新参照460はPGPT未完了/外部所有HOLD。QA051未回答の旧表記より7147c428の承認を優先、他HOLDと実装/比較未完は維持。','', '自己レビューは同一作成者で独立承認ではない。構造PASSは文書JSON/参照/集合/式のみ、製品試験/意味の全block一括PASSではない。レビュー是正の履歴はreview-findings.json、全SSは534/535。']
 for n in ['551_仕様書自己レビュー結果.md','553_継続監査実績・完了条件.md','554_全SS意味監査・継続自己レビュー.md']:md('550_レビュー/'+n,summary)
 report['counts'].update(case_records=len(cs),cases=len(active),assertions=stats['active_assertions'],spec_confirmed=sum(c['spec_status']=='CONFIRMED' for c in active),spec_pending=sum(c['spec_status']!='CONFIRMED' for c in active));report['implementation_reference_source']=source['implementation_reference'];report['initial_implementation_reference']=rd('baseline.json')['implementation_source'];report['document_review_state']=cont['overall_state'];report['result']='PASS' if not errors else 'FAIL'
