# G13.07 Main CP参照なしfixtureの単一利用責任5件

2026-10-25 15:44 JST、G13_FIXTURE_CONSUMER5_SOURCE_V1/source64446不変更。開始.5/2/5pp・cap10、fresh06:43:30UTC使用2/残98/reset1793513544/secondarynull。fresh現在窓残10以下/取得不能等で保全、旧累計80/90停止は使わない。

Mainを呼ばないJDBC/consumer fixtureを架空Mainへ結び付けない。完全pathの全直接Test consumerを固定class graphから逆引きし、全consumerに既知の同一canonical/cost担当がある5件だけその試験支援責任をprimary候補とする。これはMain CPからの担当ではなく、明示したconsumer責任である。複数担当/consumerなし/未知担当/曖昧symbolの場合は登録しない。

source rootは`src/`。

|source|primary/cost|全直接consumer（当module内、*.java）|
|---|---|---|
|schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/messaging/inbound/FatalIsolationFixture.java|WBS-P005-03|CommittedTerminalAdmissionContractTest,FatalIsolationConsumersContractTest|
|schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/security/AdminAuthFixture.java|WBS-P007-03|AdminCommandAuthenticatorTest|
|schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/cleanup/HandoffJdbcProbe.java|WBS-P004-04|InspectorLockHandoffTest|
|schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/file/CompletionJdbcProbe.java|WBS-P017-04|BackupBundleCompletionTest|
|schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/repository/BatchJdbcProbe.java|WBS-P017-07|CleanupRepositoryTest,CleanupTerminalRepositoryTest|

元9386v3 graph/9246正常snapshot/9522のsource責任を固定hashで参照、元18件のMain CPなし理由と反射等のruntime不確定を保持する。Producerは全1910Test classのsymbol graphを利用し、postは保存した全class bytesを別途読み、SourceFile/identity/CPと原hashを確認して全consumer集合を再構築する。表は独立parseしたexpectedで、同basename別module/consumer欠落・追加・担当相違/unknown/primary-cost/現byte/実行成功捏造の反例を確認する。

製品Testを実行せず、5を実行PT/coverageへ数えない。target compile/load/init/JUnit/JDBC/DB/VM/Root/cohort/native/鍵/intent/permit/配備/Unit/サービス/遠隔操作0。公開sourceと保存classfileのbyte読取/工具vectorだけ許可、拒否操作の再試行なし。旧成功/Currentbaseline/oracle変更0。

見込Java1769→1774/1789/Test804→809/824/残20→15、限定944→949。独立確認後だけ計上し、全method/RD/UI/SS/TestID/oracle/終了依存やPGPT工数率へ転換しない。費用G13.07一回、共有fixture各consumerへ再加算0。元941943/481484/見積受入意味・正式1964-53/17-190/工数null/QA051final/全current auditHOLD/全actualHOLD維持。保存後も残15根拠と独立普通PGPTへ継続、小群/報告/PMO返信待ち停止なし。
