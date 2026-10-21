# SSC330 original four counterexamples / four Main PG

Test-source964ba455a6c9d87ffcf38f9862bce79d26d6f0a4、両archivef8081c2418ec7e184c6915bc598de48a19a1771ba124a9eea9bb53fc041d8ccb。

|元job|真正結果|
|---|---|
|6562/97453 API赤|UTC15:49:26.877192～15:52:44.742105、終了1/phase0,0,1/9tests/5suites/F2/E/S/flaky0、後段6not-run|
|6564/66432 Web赤|UTC15:49:28.855337～15:53:09.747565、終了1/phase0,0,1/13tests/6suites/F2/E/S/flaky0、後段2not-run|

原read-red終了0/e39331468ca6095dd90d5dffabb729e3854e07828571eb14f2f538668120c8ab。両同source/TestHashes、1436事前予測001/002のExpected AssertionError対実固定startup exceptionだけ四件一致、各003の既直接順位/普通循環は成功。compile/error/timeoutを目的赤に変換0、後段not-runをPASSへ加点0。両元job終了・再演不要。

## PG-D487 / 実装

BUG1593/YKT1346/SSC330、SS312/342/354、design-only7fa7be822/PR194→main6dffaa0e0。四MainだけPG。APIの既TemporaryInfrastructureExceptionにJMS linkedとpure attachSecondaryを追加、WebStartupExceptionに同じmodule-local portを設ける。直接root Errorは割当より先に伝播、nested graphはcause/suppressed/JMSlinked/SQLnext FIFO identity visited。null/同一Throwable/suppression無効は1437の独立期待どおり、入力graphの一時参照を新catalogへ持ち越さない。

両readinessは既直接fatal選択を変更せず、今まで捨てた非Error close secondaryを一時attachし、最終catalog前に分類する。DB/consumer/context close各一回/後続開始0、正常固定診断/順序/Unit/業務ready/権限を変更しない。bootstrap/protocolへJMS依存やWeb→API依存追加0。API transactionの同port再利用は後続1625scopeであり、この四Mainで済んだことにしない。

元readiness二Test SHA301e5bbb/1bff3207は固定、新pure graph三method/API-Web各1classを1437から実装。green24/11/三phaseと6568原8511667/Jar/XML/当static/実counterは次実行、未実測はnull。旧source success/四counter/nativeへ合算0、全域/各domain/当全体/F03/正式は未受入。
