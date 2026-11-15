"""Record source manufacture/review without promoting unexecuted SDK PT or coverage."""
from pathlib import Path
import datetime, hashlib, json, re

r=Path.cwd(); b=r/'evidence/01_PT/018_NK-OPS-001'; e=b/'evidence/PG33710-pgcopy-source-pt-unrun-review-v1'; p=r/'evidence/01_PT/019_NK-MIG-001'
sha=lambda x:hashlib.sha256(x.read_bytes()).hexdigest()
dump=lambda x,v:x.open('x').write(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
checks=json.loads((e/'source-only-checks-v2.json').read_text()); review=json.loads((e/'source-only-review-v2.json').read_text())
assert checks['actualExit']==review['actualExit']==0 and review['actualTestExecution']==0
main=r/'src/schubert-nk-bootstrap/src/main/java/dev/codex/schubert/nk/migration/PostgresMigrationCopyPort.java'
test=r/'src/schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/migration/PostgresMigrationCopyPortTest.java'
assert all(sha(r/k)==v for k,v in checks['inputHashes'].items())
assert len(re.findall(r'@Test\b',test.read_text()))==24
refs=[]
for name in ['PostgresCopyTextEncoder','CurrentScenarioFileMapper','CurrentScenarioEntryMapper','AudioMigrationMap']:
 f=main.with_name(name+'.java');s=f.read_text();lines=s.splitlines()
 copy=[(i+1,x.strip()) for i,x in enumerate(lines) if 'new ArrayList<@Nullable String>' in x]
 guards=[(i+1,x.strip()) for i,x in enumerate(lines) if '.size()' in x and ('width' in x or 'CURRENT_COLUMNS' in x)]
 assert copy and guards and copy[0][0]<guards[0][0]
 refs.append(dict(path=str(f.relative_to(r)),sha256=sha(f),ownedCapture=copy,widthGuard=guards,disposition='SOURCE_ONLY_NONAPPLICABLE_OWNED_COPY_PRECEDES_CHECK_NOT_DYNAMIC_RETEST'))
dump(e/'owned-width-source-horizontal-review.json',dict(actualExit=0,relatedBug='BUG3003',relatedYkt='YKT2532',targets=refs,newPortHash=sha(main),futureNegative='PGCOPY005 capture-changing row/empty/width+-1/null row; NOT_RUN_HOLD',runtimeTests=0))
cases=[
 ('six fixed tables','six independent SQL commands and six hand-authored wire rows; actual count1/end1/inactive/no cancel'),
 ('empty dataset','writes0/end1/count0/inactive'),
 ('null target/table/rows','fixed IAE; SDK calls0'),
 ('unknown/case/namespace/whitespace table','fixed IAE before SDK; no dynamic identifier'),
 ('six widths+-1/empty/null row/capture changes','fixed IAE based on owned snapshot, SDK calls0'),
 ('autoCommit true','fixed SQL exception before unwrap'),
 ('readOnly true','fixed SQL exception before unwrap'),
 ('attribute SQL/runtime/Error','original primary identity; unwrap/start/cancel0'),
 ('unwrap null/SQL/runtime/Error','null fixed SQL; thrown identity preserved; start0'),
 ('manager null/SQL/runtime/Error','null fixed SQL; no start/cancel'),
 ('copy start null/SQL/runtime/Error','null fixed SQL; unowned handle cancel0'),
 ('initial inactive','fixed SQL; writes/end/cancel0'),
 ('every write position x three primary types','exact primary; subsequent writes/end0; active handle cancel once'),
 ('invalid surrogate/NUL','IAE; active handle cancel once; no accepted row count'),
 ('end SQL/runtime/Error','original primary; failure-only cancel when active'),
 ('end count -1/0/2/MAX for one row','fixed SQL; no success'),
 ('active after end','fixed SQL; cancel once and check inactive'),
 ('primary three x cleanup three','first primary same identity; one ordered suppressed cleanup'),
 ('cleanup same primary identity','no self-suppression; rethrow original'),
 ('active query faults/cancel remains active','original primary with cleanup fault; no cleanup success inferred'),
 ('callback input mutation/null field','owned snapshot unchanged; SQL NULL marker retained in literal wire'),
 ('borrowed connection/repeated normal call','commit/rollback/close/set attributes0; independent second handle'),
 ('redaction/public vectors','fixed redacted toString; explicit six SQL/column widths; no data in logs'),
 ('8 workers/64 tasks','each literal wire/count; future5 seconds; finally shutdownNow/await10; NOT_RUN_HOLD')]
doc='# PgJDBC COPY API・独立期待値・24件対応仕様\n\nProgram NK-MIG-001、PostgresMigrationCopyPort.copy/snapshot/cancelOwned/requirePg/requireManager/requireCopy/toString。RD MIG003/005/006・MIG-DAT005・TST、UI223/242/254、SS311/331/343・SSC417。仕様148と併用する。\n\n'
doc+='全件の事前条件は将来のSDK実行許可、Java25、既定42.7.13 ABIの正式確認、秘密を含まない合成fixture、借用write transaction。現在はSDK jar読取・compile・実行を許可しないため実行commandなし、全24件NOT_RUN_HOLD。型確認・動的結果・coverage・NPE排除の受入は未完。@Disabledや除外で合格にしない。\n\n'
doc+='|Test ID / method|入力・操作|独立期待値・観点|結果|\n|---|---|---|---|\n'
for i,(a,c) in enumerate(cases,1):doc+=f'|PT-MIG-PGCOPY{i:03d} / pgcopy{i:03d}|{a}|{c}|NOT_RUN_HOLD|\n'
doc+='\n期待値はSSの明示六列リストと手書きSQL、合成rowから独立Pythonで作ったUTF8 wire hex、明示call履歴を使用し、production methodからexpectedを生成しない。証跡PG33710のcorrected-independent-six-copy-command-vectors.jsonとindependent-future-pt-row-wire-vectors.jsonへ対応する。SQL delimiterのPG復号後は09、NULL markerは5c4e。原・現SQLは全byte同一で、BUG3001は誤検知取り下げ。意図的に二重化した別合成negativeだけ5c74/5c5c4eとして拒否した。これはDB実行や実PTではない。\n\n'
doc+='公式API source照合は[PGConnection REL42.7.13](https://raw.githubusercontent.com/pgjdbc/pgjdbc/REL42.7.13/pgjdbc/src/main/java/org/postgresql/PGConnection.java)、[CopyManager](https://raw.githubusercontent.com/pgjdbc/pgjdbc/REL42.7.13/pgjdbc/src/main/java/org/postgresql/copy/CopyManager.java)、[CopyIn](https://raw.githubusercontent.com/pgjdbc/pgjdbc/REL42.7.13/pgjdbc/src/main/java/org/postgresql/copy/CopyIn.java)、[CopyOperation](https://raw.githubusercontent.com/pgjdbc/pgjdbc/REL42.7.13/pgjdbc/src/main/java/org/postgresql/copy/CopyOperation.java)、[PostgreSQL17 COPY](https://www.postgresql.org/docs/17/sql-copy.html)。ソース上の契約確認のみでSDK ABI実測ではない。コピー済vendor sourceは格納しない。\n\n'
doc+='接続認証・same-peer・排他・TX期限・rollback・資源後条件・未知結果の隔離はcaller側残条件。COPY cancel呼出しのソースがあっても実DB回収成功は未確認であり、再送を発行しない。性能・large dataset・実同時入力変更・DB永続化・migration/cutback・IT/STも未受入。\n'
(p/'149_PgJDBC COPY API・独立期待値・24件対応.md').open('x').write(doc)
result='# PgJDBC COPY 製造source確認結果・PT未実行\n\n2026-11-15、dev-foundation、source前HEAD7b2f17f40bfff283913a30a6fe4ab8329d9d8031。実行環境/時刻/command/exit/hashはPG33710/source-only-checks-v2.json、独立source判断はsource-only-review-v2.json。整形GJF1.36.1とCheckstyle14.3のJava source parseは終了0・指摘0。旧途中結果も保存し、新24Testを一度も起動していない。\n\nSDK ABI/compile、NullAway、SpotBugs、semantic PMD、全体build、動的PT24、実Driver/DB/nativeはNOT_RUN_HOLD。line/method/class/branch/instruction coverageはすべてnull、PASS数0。旧Coreef461eba/Unita48eec60の全1050は新POM変更前の歴史資格として保持し、新port・新POMへ流用しない。旧105Java source byte不変はレビュー済みだが、新依存グラフ全体の受入を意味しない。\n\nBUG3001/YKT2530は表示escape誤読による誤検知取り下げ、source修正実績0。BUG3002/YKT2531はfuture fixture初期化順をsource是正し型compile/PT待ち。BUG3003/YKT2532はowned capture後の幅検査へsource是正、未来PGCOPY005を追加し、既4Mainの非該当根拠をsource-only水平確認、動的未完OPEN。BUG3004/YKT2533の誤った旧vector異常前提は原・現同値正例と独立合成負例で是正、metadata source review限定で閉鎖し製品PT成功に数えない。\n\n価格1/3/8pp cap9はこのsource製造・PT source・強化レビュー段のみ。未実行SDK/PTの残工数を0としない。後続費用は元P019/全451費用に含む未確定内訳として保留、追加二重課金0、今回段完了を工程完了/工数完成率に換算しない。正式1964PT/53scope、正本184/625、元190新0、工数率nullを維持。\n'
(p/'150_PgJDBC COPY製造source確認・PT未実行結果.md').open('x').write(result)
stamp='\n\n2026-11-15 SSC417 source段: '+result.split('\n\n',1)[1]
for name in ['documents/400_PGPT/430_構成・追跡/431_Module・Program一覧.md','documents/400_PGPT/420_環境/421_開発環境・toolchain構築記録.md','documents/400_PGPT/450_品質/451_Build・静的解析・coverage方針.md']:
 with (r/name).open('a') as f:f.write(stamp+'\n')
ledger=r/'documents/900_OTHER/910_台帳'
for name,ids in [('915_障害表.md','BUG3004'),('916_横展開管理台帳.md','YKT2533')]:
 with (ledger/name).open('a') as f:f.write('\n\n2026-11-15 '+ids+'限定結果: 現行状態CLOSED（source-only metadata review修正のみ）。PG33710/source-only-review-v2.json終了0で原/現六SQL同値、09/5c4e正例と独立合成5c74/5c5c4e負例、future24本文literalを照合。旧3412失敗/元snapshotは保全。BUG3001/YKT2530の誤検知取り下げを維持し製品修正・PT PASS・coverage増分0。BUG3002/YKT2531とBUG3003/YKT2532はsource是正済・型/動的未実行OPEN。後続commitとsource-stage joinへhashを結合。\n')
for name in ['915_障害表.md','916_横展開管理台帳.md']:
 with (ledger/name).open('a') as f:f.write('\n\n2026-11-15 SSC417未完明示: BUG3002/YKT2531（future manager初期化順）、BUG3003/YKT2532（owned capture後幅検査）はsource-only修正とGJF/CS/強化レビュー済み。PG33710/owned-width-source-horizontal-review.jsonに既4Main非該当根拠とhash、149仕様に全24ケース/独立期待を記録。型compile/SDK/PT未許可で再試験未実施、両障害の動的閉鎖はOPENのまま。BUG3001はWITHDRAWN_FALSE_POSITIVEで修正実績ではない。\n')
print(json.dumps(dict(actualExit=0,planned24='NOT_RUN_HOLD',actualTests=0,coverage=None,sourceDocsWritten=True)))
