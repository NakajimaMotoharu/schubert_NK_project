# SSC328認証/session/再送JDBC graph単体仕様（元4073資格後に着手）

BUG1591/YKT1344/PG-D483/SS314354/SSC328、canonical main=db6b569df（設計のみ）。対象AuthInfrastructure.preserveFatal（WBS-P007-03）、SessionStoreException.preserveFatal（P015-01）、RevocationRetryCoordinator.preserveFatal/transaction（P015-05）。正常認証/session/再送backoff・wire/SQL/資源順は変更しない。現sourcef39/4073実行中は新Main/Testをまだ書かず固定、下記は後続の独立反例仕様である。

PT_DEFAULT：自己生成IOException/SQLException/RuntimeException/AssertionError objectだけ、最大5秒のJUnit自己worker上限、IO/DB/JMS/network/VM/Root/実keys/権限・permit/cohort操作0。SQLExceptionのnext/causeを通常Java APIで接続するだけで、実driver/SQLを実行しない。reflection/private field変更・Provider内部への侵入0。例外の秘密raw textをログ/manifestへ保存しない。visited処理やexpectedをProduction helperで生成しない。

|TestID|独立graph・期待|
|---|---|
|PT-AUTH-GRAPH328001|非fatal root→causeだけの元Error。返却/固定catalogではなく同一Error。cause/suppressed backedge重複があっても有限|
|PT-AUTH-GRAPH328002|root SQLException→next SQLException→cause元Error。nextのcycle/重複、Error無しなら有限帰還、Errorがあれば同一object|
|PT-AUTH-GRAPH328003|root直接Errorが最優先。root suppressed Errorとcause Errorの競合は既suppressed先を維持。plain非fatal/SQL next=nullも有限、null failureは境界NPEのまま正常成功にしない|
|PT-SESSION-GRAPH328001|SQL next先だけのErrorを同一objectで捕捉、通常SessionStoreExceptionへ縮退0|
|PT-SESSION-GRAPH328002|cause/suppressed/SQL next混合cycleを非fatalで有限、next先へのlate Error追加後は同一fatal。既cause/suppressedだけではfatalへ到達できない独立fixture|
|PT-SESSION-GRAPH328003|直接Error最優先、root cause Errorは既suppressed/next先Errorより先。既null boundary/非fatal/next=null契約を維持|
|PT-REVOCATION-GRAPH328001..003|上記session側三観点をRevocationRetryCoordinatorの同source helperへ別に検証。Session側成功の流用ではない。transaction既commit/rollback/close・RERUN005は後続全体で非回帰|

API helperはpackage-private入口、Web二helperも同package Testから呼ぶ。新Test三class/各3method、旧graph Test2method（Auth/Session）と六module基準12を保持。redはAPIとWebを分離する：APIが意図どおり失敗するとWebのtest依存先がreactor停止となるため、一度のredでWeb未実行を再現済みにしない。各redは全先行compile後に該当caseを実行し、失敗source/hash/XML/expectedとactualを保持。reactorで未実行の後段をPASSへ加点しない。

予定API赤inventory16/9（基準12＋旧Auth1＋新Auth3）、Web赤19/10（基準12＋旧Session1＋新Web6）、green23/12（基準12＋旧2＋新9）。赤の実件数は停止moduleまでなのでinventory満数とは限らない。red originalの意図したassertion差を独立回収し、compile/timeout/別例外を目的の反例としない。三Main最小PGはAPIにcause/SQL next、Web二つにSQL nextだけを追記、既順とvisited保持。red Test bytesをgreenで固定し、原全Main/Jar/XML資格・三helper全分岐と必要当source全4082/617（宣言検査後）/既domain非回帰へ接続する。

JMS linkedは三helperのJDBC入力責務に非該当。既四sender/dispatcherは別の四edge契約を持ち同source全体参照へ再結合する。一般application/JDBC catalog全域のYKT1323は本三箇所で完了扱いにしない。QA051final/実Root等HOLD・正式1964/53・17/190・工数null/PTALT代替0不変更。群開始見積り/command/source/run/日時・結果hashは元4073の原資格後の着手記録で確定、推定を実費/完了へ算入しない。

## 着手確定（2026-10-21 23:11JST）

元4073/6526/6528/当traceの真正0とsource固定解除を確認、群1623/WBS-P007-03主担当＋P015-01/05参照、.3/1/3ppを先行固定。新三Testclassの各001/002/003は表の同番号method（Auth auth328001/002/003、Session/Revocation graph328001/002/003）。Main/gates/旧oracle変更0、formatter55689終了0、定義/Scope/compile-first/赤assertion限定管理三0。

- AuthenticationJdbcGraph328Test SHA c73217cbaa48bfe70bfc1a03f25b8c23b8490ccc7fb1e3674070e6499786daf6
- SessionJdbcGraph328Test SHA 86ffb80768b51695b877a255aa1665c64e69f2bf6e8b0835f82df470892b7d7c
- RevocationJdbcGraph328Test SHA 1933a72138937489085e50e6f9388af72a568c0e3faa0a2dbe7a114b272edc89

固定PYTHONPATH/JDK25.0.4/Maven3.9.12で `python3 -B tools/quality/pg6534_jdbc_fatal_graph_selected.py api-red`、元終了後に同Testsource/oldMainで`web-red`、両原artifactを `pg6536_jdbc_original_red.py` で独立照合。API赤は10/6・目的F2、Web赤は17/8・目的F4を見込む（後段not-runを成功にしない）。見込みと違うcompile/timeout/別exceptionは目的反例としない。原赤保全後だけ三Main PG/同Testbytes green23/12へ。
