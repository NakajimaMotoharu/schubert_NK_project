# 公開Journal・親期限 原九単体テスト仕様

source6b53efeec87f3ec36a840dd8e7759656cb4aee5c、HEAD553eccb277a9dce27fc4b0b5edb2234e4c410f5c。群17680、開始1/3/6pp cap10・fresh78/残22。主F03、P017-10/P004-04参照費0。NK-OPS-001、MQ001/002/009/010・SYS004、UI231/251、SS321/342/343、SSC125/130、元781/2497～98/3315を継承する。

原BrokerJournalEvidenceTest322行全七、ArtemisParentDeadlineTest110行全二を改変せず実施。PT_DEFAULT。前者は手書きvendor2.56公開JSON/固定UUID/公開非秘密SHA256だけ、OS journalを読まない。provider欠落は自分の隔離JUnit JVMのregistryだけをtry/finallyで順序復元し、復元後全配列一致とabc既知SHA256をassert。外部provider/鍵/署名/credentialに触れない。後者は注入Guard/ThreadLocal・自分のThread一個/start/joinだけ、実broker/Core/JMS/DB/network/Root/VM/実時計/Unit/permitを呼ばない。元wholeや拒否対象の分割ではなく独立の原二suite、旧別source17ab成功を再演成果として流用しない。

|原Test ID/method|入力と独立oracle|
|---|---|
|BROKERSTART003/allThreePrimaryVendorEventsBoundToActualGenerationAndExactBytes|三vendor行・boot/invocation/cursor/time、entries3・独立JCA rawSHA・固定redacted表示|
|BROKERSTART003/emptyOldMalformedDuplicatedOrErrorCannotProveRecovery|旧世代/異unit/priority/JSON member/重複/UTF8/4MiB+1/null、固定IOException/NPE。証拠欠落を復旧成功にしない|
|bj2478001AnchorMetadataAndExactByteBoundariesRejectForeignOrMissingEvidence|固定cursor/monotonicと65536/65537境界、欠落/異vendor拒否|
|bj2478002CanonicalAndStrictJsonBoundariesDoNotNormalizeUnavailableEvidence|正規JSON/終端LF・UTF8/null/空/孤立surrogate、固定IOException|
|bj2478003ClosedHistoryRequiresIndependentCursorTimeAndCanonicalDigest|独立NKJOURNAL1 member順/hex構成とJCA SHA、全4行・anchor/cursor/time/hashの不一致拒否|
|bj2478004CryptoProviderOutageIsRedactedAndRegistryRestored|自分のJVM provider欠落、固定redacted例外、finally全順序復元、abc標準vector|
|ISSBROKERSTOP001/issbrokerstop001ActualStopEventNeedsSameBootInvocationWholeIntervalAndExactBytes|公開停止行、同boot/invocation/区間1234567..1234568/一entry・独立SHA、範囲逆転や異metadata拒否|
|EXPARENT005/eachExchangeBorrowsActualRemainingAndNeverRoundsUp|5e9/1999999999/1e6/999999/1/0ns、2000/1999/1ms・未満拒否・退出2000|
|EXPARENT005/exceptionExpiryNestedAndOtherThreadNeverEscapeOwnerLifetime|例外/期限切れ/入子/null/別自己Thread。固定IOException/NPE、入子callback未実行、別thread/退出2000|

並行=元別Threadの非継承、再送=この純粋証拠codec/期限借用では非該当（実JMS再送を認定しない）。正常/境界/例外/異常/nullを元assertionで確認、expectedをProductionから作らない。

全Main ArtemisManagementReadinessClient324行を今回確認、BrokerJournalEvidence全体は3315等の同byteレビューを再利用しMain初期化も純値と確認。Source二/全九physical=Code四/NoCode五、未到達コードも分母。旧15775/15904の全Source proof/counter保持、exec union0。原XML/session/CRC/全四held・六native/Root不在と独立oracleをpostで照合する。

command `python3 -B tools/quality/pg11123_checked_python_entry.py tools/quality/pg17680_public_journal_deadline_nine_pt_v1.py`。正常compile14216同source六jar/JDK25.0.4と既qualified reporterを使用、source/Test/input/OS/JDK/branch/HEAD/time/command/exit/XML/exec/hashはmanifest保存。正式1964/53・歴史17/190・工数null・新受入0/QA051final/全HOLD不変更。
