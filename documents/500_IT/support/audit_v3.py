"""継続依頼021417412基点の監査集計。文書JSON以外へアクセスしない。"""
import json,collections

def render(root,out,report,errors):
 d=out/'data'
 def rd(n):return json.loads((d/n).read_text())
 def wr(n,x):(d/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
 baseline=rd('continuation-baseline.json');p=rd('cases.json');cs=p['cases'];ix={c['id']:c for c in cs};sc=rd('scenarios.json');changes=rd('case-changes.json');cts=rd('contracts.json')
 active=[c for c in cs if c['lifecycle']=='ACTIVE'];new=[z for z in changes if z.get('epoch')=='CONTINUATION_20261102'];oldids=baseline['legacy_case_ids'];ledger=[]
 for tid in oldids:
  c=ix[tid];done=c.get('review_epoch')=='CONTINUATION_20261102'
  ledger.append({'test_id':tid,'status':'REVIEWED_PENDING_DECISION' if done and c['decision_issues'] else ('REVIEWED_SPECIFIED' if done else 'NOT_YET_REVIEWED'),'scenario_ids':c.get('scenario_ids',[]),'contract_ids':[x['id'] for x in cts if x['test_id']==tid],'decision_issues':c['decision_issues'],'source_condition_ids':c['ss_condition_ids'],'execution_state':'NOT_EXECUTED'})
 stats={'baseline':{k:baseline[k] for k in ['active_cases','active_assertions','explicit_scenarios','historical_SUPERSEDED']},'current':{'active_cases':len(active),'active_assertions':sum(len(c['assertions']) for c in active),'explicit_scenarios':len(sc),'historical_SUPERSEDED':sum(c['lifecycle']=='SUPERSEDED' for c in cs)},'new_cases':sum(z['action']=='ADD' for z in new),'rewritten_cases':sum(z['action']=='REWRITE' for z in new),'consolidated':sum(z['action']=='CONSOLIDATE' for z in new),'old137_reviewed':sum(x['status']!='NOT_YET_REVIEWED' for x in ledger),'old137_remaining':sum(x['status']=='NOT_YET_REVIEWED' for x in ledger),'execution_state':'NOT_EXECUTED','overall_state':'IN_PROGRESS'}
 wr('continuation-audit.json',stats);wr('legacy137-review.json',ledger);report['continuation']=stats
 lines=['# 継続監査の実績・完了条件（021417412基点）','', '**全体はIN_PROGRESS。小区切り・commit・構造PASSで終了しない。** 全IT結果NOT_EXECUTED。','', '| 指標 | 基準 | 現在 |','|---|---:|---:|']
 for k in stats['baseline']:lines.append(f'| {k} | {stats["baseline"][k]} | {stats["current"][k]} |')
 lines += ['',f'今回新規{stats["new_cases"]}、書換{stats["rewritten_cases"]}、統合{stats["consolidated"]}。旧137caseの意味再監査済{stats["old137_reviewed"]}、未処理{stats["old137_remaining"]}。', '', '| 旧Test ID | 再監査状態 | 明示SC | 判断待ち |','|---|---|---|---|']
 for x in ledger:lines.append('| '+x['test_id']+' | '+x['status']+' | '+', '.join(x['scenario_ids'])+' | '+','.join(x['decision_issues'])+' |')
 lines += ['', '完了条件：SS全件意味レビュー・未読/未分類/作成可能未作成0、旧137caseレビュー済み、独立ケース追加、性能/ミドルウェア追加、入力/期待/証拠対応、判断待ちと開始依存分離、自己レビュー。未達項目があるため正常完了を宣言しない。']
 (out/'550_レビュー/553_継続監査実績・完了条件.md').write_text('\n'.join(lines)+'\n')
 f=out/'501_IT仕様書一覧.md';s=f.read_text();a=s.find('再監査では53case');b=s.find('判断待ちと工具未実装',a)
 if a>=0 and b>=0:s=s[:a]+f'継続監査中。有効{len(active)}case・{stats["current"]["active_assertions"]}Assertion・明示{len(sc)}SC。旧137caseの未処理{stats["old137_remaining"]}。'+s[b:]
 if '[553]' not in s:s+='\n[553](550_レビュー/553_継続監査実績・完了条件.md) に021417412からの追加・書換と旧137caseの処理を継続記録する。全体はIN_PROGRESS。\n'
 s=__import__('re').sub(r'継続監査中。有効\d+case・\d+Assertion・明示\d+SC。旧137caseの未処理\d+。',f'継続監査中。有効{len(active)}case・{stats["current"]["active_assertions"]}Assertion・明示{len(sc)}SC。旧137caseの未処理{stats["old137_remaining"]}。',s)
 f.write_text(s)
