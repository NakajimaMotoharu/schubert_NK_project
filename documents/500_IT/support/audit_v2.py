"""仕様データだけの派生生成・整合監査。製品/DB/MQ/OS serviceへアクセスしない。"""
import json,collections,pathlib,os

def render(root,out,report,errors):
 d=out/'data'
 def rd(n):return json.loads((d/n).read_text())
 def wr(n,v):(d/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
 def md(n,lines):(out/n).write_text('\n'.join(lines).rstrip()+'\n')
 def e(x):return str(x).replace('&','&amp;').replace('<','&lt;').replace('>','&gt;').replace('|','\\|').replace('\n','<br>')
 p=rd('cases.json');cs=p['cases'];ix={c['id']:c for c in cs};sc=rd('scenarios.json');sx={s['id']:s for s in sc};ct=rd('contracts.json');cx={x['id']:x for x in ct};co=rd('conditions.json');ci={x['id']:x for x in co};changes=rd('case-changes.json');base=rd('baseline.json')
 active=[c for c in cs if c['lifecycle']=='ACTIVE']; reviewed=[c for c in active if c['semantic_review']=='CONTRACT_REVIEWED'];legacy=[c for c in active if c['semantic_review']=='LEGACY_PARTIAL']
 def ck(ok,msg):
  if not ok:errors.append('V2 '+msg)
 ck(len(sx)==len(sc),'SC ID重複');ck(len(cx)==len(ct),'contract ID重複')
 for x in ct:
  c=ix[x['test_id']];ck(c['lifecycle']=='ACTIVE',x['id']+' inactive');ck(set(x['scenario_ids'])==set(c['scenario_ids']),x['id']+' SC集合不一致')
  ck(bool(x.get('source_clauses')),x['id']+' exact clauseなし')
  for cid in x['condition_ids']:ck(cid in ci,x['id']+' condition不明')
  for z in x['source_clauses']:ck(z['quote']==ci[z['condition_id']]['text'],x['id']+' 原文drift')
  ck(c['ss_condition_ids']==x['condition_ids'],x['id']+' case条件集合不一致')
  for s in [sx[k] for k in x['scenario_ids']]:
   ck(s['initial_state'] and len(s['steps'])>=6,s['id']+'具体入力/操作不足')
   aids={a['id']:a for a in c['assertions']};ck(set(s['assertion_ids'])<=set(aids),s['id']+' assert不明')
   ck({z['assertion_id'] for z in s['assertion_evidence']}==set(s['assertion_ids']),s['id']+' assertion/evidence不一致')
   for z in s['assertion_evidence']:
    ck(z['predicate']==aids[z['assertion_id']]['expected'],s['id']+' predicate drift')
    ck(not z['implementation_oracle'],s['id']+' 実装oracle混入')
   ck(s['execution_state']=='NOT_EXECUTED',s['id']+' 実行状態混入')
   if s['decision_issues']:ck(s['spec_status']=='PENDING_DECISION',s['id']+' TBD確定扱い')
 for c in legacy:ck(c['spec_status']!='CONFIRMED',c['id']+' legacy確定扱い')
 for c in cs:
  if c['lifecycle']=='SUPERSEDED':ck(c['superseded_by'] in ix and ix[c['superseded_by']]['lifecycle']=='ACTIVE',c['id']+' 不正redirect')
 ck(all(z['semantic_status']!='FULLY_COVERED' for z in co),'block全充足の誤宣言')
 counts={'case_records':len(cs),'active_cases':len(active),'historical_superseded':len(cs)-len(active),'added_cases':sum(x['action']=='ADD' for x in changes),'rewritten_families':sum(x['action']=='REWRITE' for x in changes),'consolidated_old_ids':sum(x['action']=='CONSOLIDATE' for x in changes),'deleted_ids':0,'active_assertions':sum(len(c['assertions']) for c in active),'historical_assertions':sum(len(c['assertions']) for c in cs if c['lifecycle']!='ACTIVE'),'explicit_scenarios':len(sc),'explicit_assertions':sum(len(c['assertions']) for c in reviewed),'scenario_repetitions_total':sum(s['repetitions'] for s in sc),'legacy_cases_without_explicit_scenario_table':len(legacy),'contracts_reviewed':len(ct),'contract_slices_fulfilled_spec':sum(x['spec_coverage']=='FULFILLED_SLICE' for x in ct),'contract_slices_undetermined':sum(x['spec_coverage']=='UNDETERMINED' for x in ct),'raw_blocks_partially_reviewed':sum(bool(x['contract_ids']) for x in co),'raw_blocks_not_semantically_confirmed':sum(not x['contract_ids'] for x in co),'executed':0}
 domains={dm:{'cases':sum(c['domain']==dm for c in active),'assertions':sum(len(c['assertions']) for c in active if c['domain']==dm),'explicit_scenarios':sum(ix[s['test_id']]['domain']==dm for s in sc),'legacy_cases':sum(c['domain']==dm for c in legacy)} for dm in sorted({c['domain'] for c in cs})}
 types=dict(collections.Counter(s['type'] for s in sc))
 mid_ids=['IT-DB-001','IT-DB-002','IT-DB-003','IT-MQ-030','IT-MQ-031','IT-NET-001','IT-TX-030','IT-OPS-020','IT-OPS-021']
 middleware={'selected_case_ids':mid_ids,'cases':len(mid_ids),'explicit_scenarios':sum(s['test_id'] in mid_ids for s in sc),'selection':'DB未確定/確定・MQ送達不明・片方向・component確定後停止・後段起動拒否。journal破損/全boot詳細はlegacy不足。'}
 performance={'cases':len({s['test_id'] for s in sc if ix[s['test_id']]['domain']=='performance'}),'scenarios':sum(ix[s['test_id']]['domain']=='performance' for s in sc),'load_scenarios':sum('load_plan' in s for s in sc),'capacity_scenarios':sum(ix[s['test_id']]['domain']=='performance' and 'load_plan' not in s for s in sc)}
 audit={'performance_detail':performance,'middleware_detail':middleware,'kind':'SEMANTIC_SPECIFICATION_REVIEW','result':'PARTIAL_WITH_OPEN_ITEMS','counts':counts,'domains':domains,'scenario_types':types,'scenario_types_by_case':{t:sorted({s['test_id'] for s in sc if s['type']==t}) for t in types},'contract_status':dict(collections.Counter(x['spec_coverage'] for x in ct)),'block_status':dict(collections.Counter(x['semantic_status'] for x in co)),'legacy_case_statuses':{c['id']:'PARTIAL_UNFULFILLED' for c in legacy},'not_applicable_policy':'工程管理/内部PTの候補分類は初版のまま。個別意味レビュー未了を適用外として隠さない。','all_ss_semantic_coverage_certified':False,'all_cases_executable':False,'product_tests_executed':False,'note':'FULFILLED_SLICEは選択契約に判定可能な仕様あり。IT合格/原文block全契約の充足/SS全件網羅を意味しない。未展開legacyと残blockは未充足を含む。'};wr('semantic-audit.json',audit)
 report['counts_v2']=counts;report['semantic_result']=audit['result'];report['result']='PASS' if not errors else 'FAIL'
 # SC全文を各case本文の直後へ挿入。同一canonical JSONから生成し転記正本を作らない。
 names={'interface':'521_インターフェース.md','transaction':'522_トランザクション・データ.md','security':'523_認証・権限・セキュリティ.md','file':'524_ファイル・メディア・Range.md','operations':'525_運用・復旧・監視.md','async':'526_MQ・非同期・容量.md','performance':'527_性能・資源・Logout混在.md'}
 for domain,name in names.items():
  f=out/'520_ケース'/name;text=f.read_text();text=text.replace('全件NOT_EXECUTED。','全件NOT_EXECUTED。SUPERSEDEDは旧ID履歴。PENDING_REAUDITは具体シナリオ再監査待ちで、仕様確定・実行可能へ算入しない。',1)
  for c in [x for x in reviewed if x['domain']==domain]:
   lines=['','### 契約再監査と具体実行単位',''];x=next(x for x in ct if x['test_id']==c['id']);lines += [x['previous_gap'],'',x['independence_reason'],'','契約：`'+x['id']+'`。判定可能範囲は[533](../530_追跡/533_契約別意味監査.md)のsliceに限定。']
   for sid in c['scenario_ids']:
    s=sx[sid];lines += ['',f'<a id="{sid.lower()}"></a>',f'#### {sid} / {s["parameter_key"]}','',f'種類：{s["type"]}、反復：{s["repetitions"]}、状態：{s["spec_status"]}/NOT_EXECUTED。','','```json',json.dumps(s['initial_state'],ensure_ascii=False,indent=2),'```','',f'実入口：{s["entry"]}。故障/競合：{s["injection"]}。待機：{s["wait"]}。','']
    lines += [f'{i}. {v}' for i,v in enumerate(s['steps'],1)]
    if 'load_plan' in s:lines += ['','負荷計画（値は共通計画にこのSC入力を優先）：','','```json',json.dumps(s['load_plan'],ensure_ascii=False,indent=2),'```']
    lines += ['','| Assertion | 個別証跡path（attempt root相対） | 判定predicate |','|---|---|---|']
    for a in s['assertion_evidence']:lines.append('| '+a['assertion_id']+' | '+e(', '.join(a['artifacts']))+' | '+e(a['predicate'])+' |')
    lines += ['', '再開：'+s['resume']+' 必須工具：'+s['tool_state']+'、[514](../510_方針・準備/514_追加fixture・工具・負荷計測仕様.md)。']
   # next case boundary直前に挿入
   anchor=f'<a id="{c["id"].lower()}"></a>';start=text.index(anchor);end=text.find('\n<a id="it-',start+len(anchor));end=len(text) if end<0 else end
   text=text[:end]+'\n'.join(lines)+'\n\n'+text[end:]
  f.write_text(text.rstrip()+'\n')
 lines=['# 契約別 意味監査・直接トレーサビリティ','', '編集正本： [contracts.json](../data/contracts.json) / [scenarios.json](../data/scenarios.json)。期待結果とSCの判定predicateは同一canonicalから生成。全件NOT_EXECUTED。','', 'これは原文blockを丸ごと充足させる表ではない。FULFILLED_SLICEは下記で選択した契約の仕様成立、UNDETERMINEDは判断待ち。未展開legacy・原文の残契約は[534](534_残不足・文書別再監査.md)。','']
 for x in ct:
  c=ix[x['test_id']];lines += [f'<a id="{x["id"].lower()}"></a>',f'## {x["id"]} {x["scope"]}','',f'仕様充足：**{x["spec_coverage"]}** / 実行NOT_EXECUTED。 [対象case](../520_ケース/{names[c["domain"]]}#{c["id"].lower()})','', '**初版の不足と独立性**','',x['previous_gap'],'',x['independence_reason'],'','| SS条件ID・節/原行 | 契約の原文（固定commit） |','|---|---|']
  for z in x['source_clauses']:lines.append('| '+z['condition_id']+' / '+e(z['section'])+' L'+str(z['line'])+' | '+e(z['quote'])+' |')
  lines += ['','| 具体SC/入力 | 実結合 | 判定Assertion | 個別証拠 |','|---|---|---|---|']
  for sid in x['scenario_ids']:
   s=sx[sid];lines.append('| '+f'[{sid}](../520_ケース/{names[c["domain"]]}#{sid.lower()}) '+e(s['initial_state'])+' | '+e(x['route'])+' | '+','.join(s['assertion_ids'])+' | '+e([z['artifacts'] for z in s['assertion_evidence']])+' |')
  lines += ['', '判断待ち：'+(','.join(x['decision_issues']) or 'なし。工具/環境/PGPT開始依存は別。')+'。'+x['block_coverage'],'']
 md('530_追跡/533_契約別意味監査.md',lines)
 # 未充足を自動的にPT/適用外へ逃がさない。
 docnotes={
 '301':'設計一覧/採番は工程管理。SS対象24文書との集合は確認。管理文を実行要件数へ加算しない。',
 '311':'責務・module境界の全dependency禁止/許可を既存IFだけで充足にしない。class内部はPT、実adapter登録/各外部経路の部品責務はITの追加照合が必要。',
 '312':'複数stage時刻・reply/ACK・質問受付budgetの相対起点・OutboxSENT gateをREQ001に追加（ISS-TIME）。既存IT-TX016/ASY007の全byte/時刻fixture確定が残る。',
 '313':'全31HTTP formの入力/redirect/error dispatch/pagination境界がlegacy。ISS-HTTPFORMと実CSRF/controllerへの接続を継続確認。',
 '314':'Login probe/SavedRequest/Logout追加。API0102後local失効をSEC025へ追加。残りcurrent-row token競合・formatv1/v2・Cookie/security chain全経路が未確定/部分。',
 '321':'PAGE/FAILとdiskBLOCKを分離。12容量SC/ACK不明/権限/ready追加。全queue metrics/TTL5/10/0・temporary managementの実セキュリティ細部は既存case再具体化が残る。',
 '322':'codec byte全field/UTF8/NFC/overflow内部はPT。実BytesMessageの種別/property/body不一致・fatal routingの全入力はlegacy、wire全fieldをITへ複製せず対外結合境界へ選定。',
 '323':'64layoutの集合割当は維持、全offset/byte oracleの意味監査完了ではない。IFごとのdata入力とgoldenはISS-DATA。',
 '324':'AAD保存元・scope・ERROR再送・worker state・claim/lease/schedule追加。private lock256 hash衝突時のDB0をTX044へ追加。全28Inspector route、鍵rotate/cleanup厳密境界は残る。',
 '331':'物理DDL/index/grant・cleanup関数のsignature/roleは開始時最終schema照合。全V001～migrationの実結合/切戻しはlegacy。内部SQL全分岐のPTをITへ転記しない。',
 '332':'取消ERROR/削除triple/孤児cleanup/loglevel/hold/query1.5s追加。全検索predicate/ソート・count/list並行・相互ADMIN deadlockの実注入とexacterror oracleは残る。',
 '333':'ENOENT/UNAVAILABLE、公開UNKNOWN、startup A/B、media別容量、filename、30Range SC追加。inode namespace置換/同mount/全権限とstream21応答選択ISS-STREAMは残る。',
 '341':'再用fresh child/旧成功/世代/cleanup/Expiry/最終close追加。current permit/全typed intent・原本seal/durable resumeの全変化点はlegacy、過去source専用修復を新環境へ複写しない。',
 '342':'Caddy逆順停止/readiness/pool/maintenance負荷追加。全systemd hardening・host namespace/cgroup/Restart5s・600sec5回・boot権限の物理反例はlegacy。',
 '343':'config allowlist8/credential17と署名/current/catalog/rollforwardbackの全field照合は追加準備仕様に固定、実config caseはISS-CONFIG。歴史catalogを更新して合格にしない。',
 '351':'REQUEST原始→投影UK追加、全26metric/label/alerttimer・origin byte/instrumentationは既存LOGの再具体化が残る。ACTION/SECURITY二重監査種別はISS-AUDIT。',
 '352':'scope/AAD/実grantの追加。PBKDF2・GCM tag等内部はPT、実資格情報配布/鍵切替・redaction全露出点はlegacy。',
 '353':'DB/MQ/片方向通信/サービス後段失敗追加。単一host/HAなし維持。RPO文言矛盾ISS-RPO-DEFINITIONは未解決、restore承認HOLD維持。',
 '354':'既定IT全scopeを保持。ケース候補リンクだけで充足認定しない。QA050は9pairwise/実15分反復、normal比較45分、規定SLA/容量の未決は543。',
 '355':'CHR24/QA051/現環境権限をIT作成で解除しない。PT/CHR実施・承認は開始依存、IT PASSへ転記0。',
 '361':'RD→UI→SSトレースの最終版照合はIT開始依存。現仕様sliceからSSへの逆参照を追加、ST/OT要求充足の宣言は行わない。',
 '362':'PGPT完了条件/品質/HOLD/464は開始依存。性能・容量・復旧・securityを上位要件由来で除外0。QA050以外の観点も削除しない。',
 '363':'設計監査の旧PASSをIT仕様全充足へ転記0。横断矛盾/QAの承認済み範囲だけ引用し、旧実source限定成果と区別。',
 '364':'SS工程完了はPGPT完了/IT開始/IT合格とは別状態。最終SS/変更台帳差分の再レビュー必須。'}
 gaps=[];lines=['# 残不足・文書別再監査','', '**全SSの意味的充足は未認定。** 原文4275blockは棚卸し母集団であり要求数ではない。本文/表の一部を契約へ抽出したblockも全体はPARTIAL、未抽出はUNREVIEWED_BLOCK。初版のIT/PT+IT節割当は撤回し、履歴をlegacy-bindings-v1.jsonに隔離した。適用外/工程管理/開始依存の初版分類も意味レビュー済みとの認定には使わない。','', '| SS | block数 | 契約slice接続block | 再監査結果・残不足・工程配分 |','|---|---:|---:|---|']
 for doc in sorted({x['document'] for x in co}):
  rows=[x for x in co if x['document']==doc];n=pathlib.Path(doc).name[:3];lines.append(f'| SS{n} | {len(rows)} | {sum(bool(x["contract_ids"]) for x in rows)} | {docnotes[n]} |')
  gaps.append({'document':doc,'raw_blocks':len(rows),'partially_reviewed_blocks':sum(bool(x['contract_ids']) for x in rows),'status':'PARTIAL_OR_PROCESS_REVIEW','remaining':docnotes[n],'unreviewed_condition_ids':[x['id'] for x in rows if not x['contract_ids']]})
 lines += ['','## 次の具体作業','', '1. LEGACY_PARTIALのcaseを再読し、実行入口と入力が実名/値/データ版まで定まるかを確認。未確定はISS-DATA/HTTPFORM/CONFIG等へ影響SCを追加する。','2. 各source blockを契約sliceへ分解し、前提/分岐/非更新/確定点/観測を追加する。既存caseへ追加できる値差はparameter行へ、異なる再開条件は独立caseへ。','3. SS312受付budgetの未確定時刻、SS314 local終端の全controller接続、SS324全28Inspector、SS341-343所有/intent/current、SS351全sensor/labelを優先。PT詳細だけのものはPT ID/最終同source証拠へ対応付ける。','4. 一つのblockが複数契約を含む場合、slice充足率からblock全体をFULLへ昇格しない。残句レビューと理由を保存してから更新。','', 'TBD/不足はITの実測NGではない。契約レビュー済familyも工具未作成・開始依存により実行不可。最終releaseに対する全SS網羅はこの監査件数から確約しない。']
 md('530_追跡/534_残不足・文書別再監査.md',lines);wr('block-audit.json',gaps)
 # 531は構造表と意味表の境界を最初に明示。
 f=out/'530_追跡/531_SS条件対応・網羅性.md';s=f.read_text();s=s.replace('# SS条件対応・網羅性照合','# SS条件対応・網羅性照合\n\n再監査の判定正本は[533](533_契約別意味監査.md)・[534](534_残不足・文書別再監査.md)。以下の4275block表は構造棚卸し。初版の節単位IT充足は撤回済み。OPENのCONTRACT_SLICEにも部分対応はあるが、block全体充足へ加算しない。')
 f.write_text(s)
 lines=['# IT仕様書 再監査レビュー結果','', '2026-11-02 JST、Codex同一作成者の自己レビュー。独立承認/製品試験ではない。全IT実行状態NOT_EXECUTED。','', '**拡充・文書整合監査を実施。全SS契約の意味的網羅と全ケース仕様確定は未完了。IT開始不可。**','', '| 指標 | 前 | 後 |','|---|---:|---:|',f'| active case family | 192 | {counts["active_cases"]} |',f'| Assertion（activeのみ） | 605 | {counts["active_assertions"]} |',f'| 明示具体SC | 未台帳化・算定不能 | {len(sc)}（legacy {len(legacy)}caseは別途展開待ち） |',f'| 追加 / 書換family / 統合旧ID / 削除 | — | {counts["added_cases"]} / {counts["rewritten_families"]} / {counts["consolidated_old_ids"]} / 0 |',f'| 明示SCの判定項目 / 反復込み実行予定単位 | — | {counts["explicit_assertions"]} / {counts["scenario_repetitions_total"]} |',f'| 履歴SUPERSEDED / 履歴Assertion | 0 | {counts["historical_superseded"]} / {counts["historical_assertions"]} |',f'| 契約slice 仕様充足 / 判断待ち | 未評価 | {counts["contract_slices_fulfilled_spec"]} / {counts["contract_slices_undetermined"]} |','', '抽象case、SC、Assertion、反復数、worker/data量を混算しない。全体具体SC数はlegacy内の隠れた複数操作が未展開のため確定不能。履歴を含むrecord数をactive件数と誤認しない。','', '| 領域 | active case | Assertion | 明示SC | legacy展開待ち |','|---|---:|---:|---:|---:|']
 for dm,z in domains.items():lines.append(f'| {dm} | {z["cases"]} | {z["assertions"]} | {z["explicit_scenarios"]} | {z["legacy_cases"]} |')
 lines += ['', '明示SC種類：'+e(types)+'。ケースには複数種類を含むため種類件数はSC単位で集計、case総数へ加算しない。異常/境界/競合/復旧は注入と後条件を本文で確認。','', '## 意味的追加とレビュー是正','', '- 保存元M0のAADと現在M1のcorrelationを分離。QSS/QSD scope降格拒否、元ERRORcode保持、Login0200後IF003 probeを独立判定へ追加。','- commit前切断とcommit ACK喪失、同W/別Wのworker、finalD SENT前ACK禁止、file公開UNKNOWNとnative ENOENTだけの再生成を分離。','- PAGE上限はFAIL（新規9001）、disk90%はBLOCK。再監査中の誤期待値を是正。旧address容量caseはSUPERSEDED、実行対象の12SCはFAILへ修正済み。','- 起動probe A/Bの設計未規定byte patternを試験側で0x41/0x42へ固定する期待値を撤回。実probeの公開前rawを独立採取し、4800byte・A≠B・collision前後同一・非秘密で判定する。',
 '- role変更はsession失効を伴うため、Login probeの成功対照をrole変更なしidle延長へ修正。scope降格試験は同ownerの新Login contextを使う。','- Root/Backupの旧source限定記録を一般期待値の根拠にしない。具体承認条文へ差替え、元失敗/UNKNOWN保持を維持。','- Range15、6address、Transfer5+5、component停止6、QA050の値名差をfamilyへ統合。9pairwise QA050で容量×故障全pair/両due分布を保持。除外第三因子組を全充足と扱わない。','- 旧4275blockの一括bindingを意味充足から撤回。64layout集合一致も各byte/全分岐の意味的網羅とは分けた。','', '## 性能・負荷／ミドルウェア障害','', '性能の明示SCと負荷窓・繰返しは[527](../520_ケース/527_性能・資源・Logout混在.md)。ramp/burst、sync+async、20media+SCN10000、復帰残件、2時間soak、maintenance排他、SQLp95 1.5秒、QA050を追加。SLAは承認値だけ。平均だけ/失敗除外/独自劣化許容率で判定しない。','', f'性能/容量のレビュー済family {performance["cases"]}、明示SC {performance["scenarios"]}（load {performance["load_scenarios"]} / 容量 {performance["capacity_scenarios"]}）。選定middleware障害は{middleware["cases"]}family/{middleware["explicit_scenarios"]}SC。MQ/DB/network/OSの具体SCはDB001-003/MQ030-031/NET001/OPS020-029/TX030。全確定点の無差別直積を作らず、DB確定有無、送達確認有無、資源所有有無で選定。mockだけの合格不可。HAは追加0。','', '## 構造検査と意味レビュー','', f'文書構造：{report["result"]}（errors={len(errors)}）、[validation-report](../data/validation-report.json)。意味レビュー：PARTIAL_WITH_OPEN_ITEMS、[semantic-audit](../data/semantic-audit.json)。後者をPASSと表示しない。', '', '全SS原文blockの意味的全分解は未完。文書別残不足は[534](../530_追跡/534_残不足・文書別再監査.md)、旧caseの未展開はPREP-SEMANTIC。RPOの式、selectivity、commit注入、pool timeout、run-history境界は判断待ち。既存ISS群/HOLD/QA051/PGPT品質と464は維持。','', '## 工程・開始gate','', 'IT=SS実結合、ST=UI全体、OT=RD検収。性能/容量/復旧/securityの既定ITは保持。ST/OTとの証拠共用は同source/environment/入力/計測窓と要求の同一性を照合したrawのみ、上位工程の合否転記0。','', '仕様拡充済、PGPT進行中、IT実行不可、IT結果NOT_EXECUTEDを別状態で管理。最終SS/release artifact/同source PGPT完了証跡/要件トレース/464残件を再照合→差分case更新→review→工具/環境/権限/HOLD確認後にだけIT開始する。今回製品・PT・IT・配備・環境起動・PG/SS修正は0。','', '基準：origin/main `'+base['design_commit']+'`、前回との差分なし。実装補助：dev-foundation `4746c687515d0c268e86e69d130c0ce1294156d6`。前回ce284と本番報告6b53とは別source。']
 a=lines.index('## 意味的追加とレビュー是正');b=lines.index('## 性能・負荷／ミドルウェア障害')
 findings=['','| 指摘ID | 発見事項 | 是正/残不足 | 状態 |','|---|---|---|---|']
 for z in rd('review-findings.json'):findings.append('| '+z['id']+' | '+e(z['finding'])+' | '+e(z['action'])+' | '+z['status']+' |')
 lines=lines[:a+1]+findings+['']+lines[b:]
 md('550_レビュー/551_仕様書自己レビュー結果.md',lines)
 lines=['# ケース変更履歴（再監査）','', '正本：[case-changes.json](../data/case-changes.json)。旧版はGit `92d9c4891c193c8b5843df6bbd12a91a5c04d425`。削除IDなし、SUPERSEDEDを実行しない。','', '| ID | 操作 | 継続先/契約 | 理由 |','|---|---|---|---|']
 for z in changes:lines.append('| '+z['test_id']+' | '+z['action']+' | '+z.get('target',z.get('contract_id',''))+' | '+e(z['reason'])+' / SC: '+e(z.get('scenario_targets',[]))+' / '+e(z.get('parameter_selection',''))+' |')
 md('550_レビュー/552_ケース変更履歴.md',lines)
