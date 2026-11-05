# Session監査writer JDBC port単体仕様

Program NK-AUT-001、SessionAuditWriter.<init>/write、WBS-P007-02、RD AUT004/MON004/DAT009、UI226/252、SS314 §12/351 §4/332、880。原群1/3/7pp cap10、原WBS価格/受入条件不変更。sourceはTest freeze後commitで記録、normal Main28af318d0198fe7432ca6fcd234d3fabbfd10173（PG19740 NullAway正常・PG19742六SB0）を全Main/POM/JAR hash一致確認の上再利用する。別sourceのMain成功は移さない。

fixture=独立memory JDBC Proxy、borrowed ConnectionはprepareStatement以外の操作を拒否、statementはsetObject/setLong/setString/setNull/executeUpdate/closeだけ許容。一fixture一Map/List、共通stateless writerをown2workerへ渡す。時刻2034-06-12T01:02:03.456789Z、actor17/target41、非session用の合成message/correlation UUIDだけ。IPはOptional.emptyと固定address byteから作るv4/v6（DNS/実socketなし）。session ID/key/token/password/実DB/JMS/Root/VM/native/認証・失効操作0。

| Test ID | class/method | 目的・入力/操作・独立期待値 |
|---|---|---|
|AUT-SESSION-AUDIT001|SessionAuditPortTest.closedReasonEventsHaveLiteralAuditFields|6閉reasonのliteral enum対応、0000と冪等Logout0200、固定SQL/六bind/JSON三keyのみ/UTC値。DDLとSS314/351から独立に固定した期待、productionからexpected生成0|
|AUT-SESSION-AUDIT002|SessionAuditPortTest.missingIpv4AndIpv6HaveIndependentLiteralBindings|SQL NULL VARCHAR、127.0.0.1、2001:db8:0:0:0:0:0:42の字句期待。過去IP・架空remoteへ代替しない|
|AUT-SESSION-AUDIT003|SessionAuditPortTest.affectedRowCountMustBeExactlyOne|更新-1/0/2を全拒否、SQLState40001/固定文言、close一回/六bind、Connection commit/closeなし|
|AUT-SESSION-AUDIT004|SessionAuditPortTest.preparationFailuresPropagateWithoutBorrowedTransactionOperations|SQL/Runtime/Error各prepare失敗の同一identity、statement未取得/close0・bind0・業務success不可|
|AUT-SESSION-AUDIT005|SessionAuditPortTest.executionFailuresStillCloseTheStatementOnce|execute各SQL/Runtime/Error同一identity、close一回/borrowed connection不操作|
|AUT-SESSION-AUDIT006|SessionAuditPortTest.closeFailuresCannotBecomeSuccessfulReturn|正常execute後の各SQL/Runtime/Error close故障も非成功、同一identity/一回close|
|AUT-SESSION-AUDIT007|SessionAuditPortTest.distinctCleanupFailuresRemainInTheOriginalFailureGraph|毎組freshな3×3primary/secondary、Java TWRのprimary保持・suppressed厳密一件/同一secondaryを期待。Errorがgraphに保持されてもcaller fatal mapping/再送/rollbackは未受入|
|AUT-SESSION-AUDIT008|SessionAuditPortTest.aliasedProviderFailureIsRecordedAsNonSuccessWithOriginalCause|execute/close同一ThrowableのJDK addSuppressed自己抑制拒否をIAE/cause原identity・非成功として記録。これを正常監査/全fatal伝播のPASSにしない。Java resource semanticsの観測とcaller契約を分離|
|AUT-SESSION-AUDIT009|SessionAuditPortTest.twoOwnedWorkersKeepIndependentStatementsAndValues|2worker/同stateless writer/別JDBC state、5秒有限getで独立reason/六bind/close一回、共有fixtureやworker result順序依存なし|

Null契約: security package-infoの@NullMarkedでconnection/client/messageId/correlationId/at/reason/resultはnonnull、actor/targetは検証済正数のcaller契約。欠落clientはOptional.empty/SQL NULLで実JUnit検証する。追加で実pinned Main JARへ呼出すcompile-only canaryのpositive0と七Java-null引数のNullAway拒否を計画する。canaryはProductの実呼出し・暗号・session生成をせず、九JUnit/coverageへ加算しない。raw DB credential/session/tokenを保存しない。

実行=input001へ固定したproducer profile session_auditのprepare/static、Test source commit後run/postを新unused19780/19782/19788・独立post19790へ一度。静的解析はMain+新Testだけ、Main default NullAway不変更、HELD四のinit/probe0。全@Test九・正常/境界/例外/欠落/並行・whole normalphysical1のCRC/単exec-session/line-method-class-branch100を独立postで照合する。生PMD/raw/適用理由・parser失敗も保持し、未分類指摘を0へ変換しない。JDK25.0.4/Maven3.9.12/JaCoCo0.8.15/JUnit1.13.4、実branch/commit/command/終了/環境/XML/hashは040とmanifestへ。

未受入=実session発行/失効/認証/暗号/DB transaction commit-rollback・SQL実整合・API/Web/Root/VM/native/CHR/全451/PT正式/IT-STと親WBS終了。技術成分の証明だけで個別leafを閉じない。既PG19488 LogQueryAuditWriter八とPG18904 LoginAuditWriter七は別componentとして保存し再実行しない。

## 初回staticの是正

PG19780 compile0/19782 raw8中のlabel重複3をBUG2313/YKT2058へ修正前起票。旧Test/producer001/compile/rawはPG19782-historyへhash保全、JUnit未実行。操作traceのlabelだけ定数化し逆展開byte一致、SQL/JSON/外部期待値/九case不変更。新active producer003でunused19786compile/19787staticを行い、元19780/19782を上書き再実行しない。初回Unit19788/post19790は未使用のまま。

881へstatic19787 raw5の全個別context（worker3/ownMap1/definingJDBCloader1）を保存、Main0/適用0-CS0-parser0/抑制0、初回Unit未実行。Null compile工具002はpinned API/protocol/JSpecify jarと同一copy親POM/同一Main default compiler設定を使う。自己所有positive/negative各新moduleでcompileだけを一度、positive0/negative1とactual source七行のNullAway診断を照合する。systemPath一時fixtureモデルwarningは原文保持し、本番POMを変えない。独立postは全source/argv/OS終端/hash/診断行を再構成する。これは七Product実行やcoverage測定ではない。

## Null canary生成源のformat是正（BUG2314/YKT2059）

元002/19784 positivebuild1（継承Spotless不適合）/negative未実行をPG19784-failed-historyに保全、NullAway受入へ算入0。新004は固定GJF1.36.1で整形済005/006源を読み、七null literal tokenのpostformat行を期待診断集合とする。工具/テンプレートsourceとhashをfreeze後、新unused19794へ正負各compile一度、原parent/Spotless/NullAway/processor flagsは不変更。skip/quality緩和/古いmoduleの再実行0。PG19788九JUnit初回0・originalpost0とGit artifact追加独立post19790は別の結果として保存、nullablecanaryの是正でJUnitを再演しない。

最終計測closeは共通owned_port_closerを利用する。元postのlegacy optional producer descriptorがnullであることは原manifestに残し、19790追加独立postのGit-bound artifact（source112dd/producer003/全hash検証）だけをfallbackに用いる。nullを成功や任意pathへ補完せず、source/Git blob/current fileの三hash一致を必須とする。更新closerのhashを883へ記録し、Product/Null compileの成功再演はしない。

metadata close前の既存19790公開copyを検出したため、旧generic closerのunused-directory guardで停止（event3915は未消化・Product追加実行0）。既存postを削除/再作成せず、own post slotと公開dirの全file名集合・全byte SHA完全一致の場合だけ再利用するガードを追加した。一致しない場合は停止し、同じ証跡を上書きしない。開始eventと終了eventは引続き一回だけ記録する。

Null compile結果の補足ID: AUT-SESSION-NULL001=nonnull正例、002..008=connection/client/messageId/correlationId/at/reason/result各null（この順）。実source行・NullAway診断・manifest/source SHAをUnit evidenceのnull-contract-reference.safe.jsonで一意に結合。七負例は期待終了1のcompile検査で、九Product JUnitのFESへ加算しない。
