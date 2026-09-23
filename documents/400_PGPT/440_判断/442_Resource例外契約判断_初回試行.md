# Resource例外契約判断（PGPT-PMO-20260923-01）

2026-09-23、W02a。判断対象はBUG-195/206、YKT-154/162、SSC-063。これは残契約の**責務別判断**であり、全対象の実装修正・横展開再試験・台帳完了ではない。根拠はSS314 §7.2.3～4、SS341 §7.3、SS312/324、既存017/048および下記親実測。RD/UI変更なし。補助agentはAstra/highのread-onlyレビュー、親はSol/medium指定でprobeを実行した。実モデル設定は機械確認できない。

ここで確定するのは各責務に適用する**設計契約と検証順**である。「非該当」はBatch型の未知provider例外identityを外部へそのまま出す規則が非該当という意味であり、close故障や固定Infrastructure失敗の追加PTが不要という意味ではない。未実測のcode違反候補は障害確定と区別する。

## 不変条件と適用判断

| 責務・対象 | 適用/非該当、次の独立確認 |
|---|---|
| `InspectorLockHandoff.execute/scalar` | BUG195/YKT154のunknown非正常化を適用。callback body、JDBC close、finally再取得は別の失敗段階。SQL/IO単独は固定Failure、未知Runtime/Errorは同一性を維持し、再取得は必ず試みる。全close・lock確認前に値を返さず、借用Connectionのcommit/rollback/closeをしない。SS341 §7.3/SSC063へ限定補足が必要。 |
| Web `JdbcWebSessionStore`＋`EncryptedWebSessionRepository` | BUG195/206、YKT154/162の次優先候補。`read`のprovider getter IAEを不正rowへ誤変換すると、`load`がhash限定DELETE→不在へ進み得る。実不正row＋ResultSet.close SQL/Errorでも同じ危険。SS314 §7.2.4は不正rowの削除commit後のみ不在、resource失敗は固定障害と明記。未実測につき修正済みと扱わない。 |
| API認証4class/5併合catch：`LoginAttemptRepository`2、`AdminCommandAuthenticator`、`AuthSessionRevocationService`、`LogoutInboxService`各1 | Batchと同じ「provider IAE identityを外部へ必ず保持」は契約上非該当、認証Infrastructure固定化が適用。codeがそれを守るかはprovider IAE/不正projection/正当0102/close SQLの4区別を既存PTへ追加して判定する。BUG167/YKT128の固定変換を削らない。 |
| APIの低位JDBC・借用TX・audit・Outbox、Web `WebLogOutboxRepository/Dispatcher` | SQL、commit/rollback、close、結果確定を分離。上位Infrastructure固定化と低位unknownのidentity要件を混同しない。`Scenario/Media/User/LogQuery` Repository、各AuditWriter、Inbox/Outbox/認証サービスを群ごとに反例確認する。確定拒否や成功へresource失敗を降格しない。 |
| JMS `OutboxJmsSender/ArtemisRequestSender/WebLogMessageSender` | 送達未確認、重複確認、markSent、rollback、closeを分離。固定送信障害を維持し、同一Throwableのrollback再送とduplicate＋close失敗を追加PT。無条件の共通ResourceScope置換は非該当。 |
| IO/保守API | `TransferStartupProbe/UsageScanner/HeldProbeFileIo/TransferRootInspection/ScenarioReadyFileInspector/HeldTransferFileIo/ScenarioFileWriter/AssetManifestLoader/InspectorCredentialLoader/InspectorApplication/LargeResultReader`は所有scope候補。`InboxCleanup/NonAuthenticationInboxInspector/QuestionMutationInboxInspector/InspectorDatabaseConnections/InspectorProcess`はPROTECTEDとSTORAGE_FAILURE/非zero終了の別契約。MISSING＋closeを正常な不在・再生成にしない。既存File系の認定scope以外は未確認。 |
| private memory/JDK | 外部provider body/close再送の一般契約は非該当。`ResponseSnapshotCodec/OperationFingerprint/RequestLogDetails/SessionAttributeCodec`等の固有失敗契約は残る。017/048 §3の既存非該当根拠はその限定範囲だけ維持。 |

## 親による独立代表反例

公開dynamic JDBC proxyだけで、Handoffの最初の3 queryを正当値として返し、4回目のlock再取得prepareStatementから合成SQLExceptionを投げた。callback bodyは固定マーカーの`IllegalStateException`、対照は`IOException`。期待はSS341 §7.3の「未知Runtimeを正常化しない」から独立に定めた。Production methodでexpectedを作っていない。DB、credential、secret、実sessionは使わない。

実行は2026-09-23 JST、`dev-foundation`/source HEAD `69479c71`、JDK25.0.4。probe sourceは `/home/mini/codex/project1/work/PMO/20260923/ResourceHandoffProbe.java`（SHA-256 `02757c10d218a8bec15d0bb07b1f93ab07192eb76eae10ac5f298110bcd092a2`）、対象class SHA-256 `6fc8ffa34d00601438d3d88ee2a56dbb064074863b8824cb6d8dcad8e8d1c322`。command:

```text
/home/mini/codex/project1/work/toolchain/jdk-25.0.4/bin/javac -cp src/schubert-nk-batch/target/classes -d /tmp /home/mini/codex/project1/work/PMO/20260923/ResourceHandoffProbe.java
/home/mini/codex/project1/work/toolchain/jdk-25.0.4/bin/java -cp /tmp:src/schubert-nk-batch/target/classes ResourceHandoffProbe
```

exit0のprobe観測: unknown body＋再取得SQLは`InspectorLockHandoff.Failure`、元例外との同一性false、suppressed0。これは期待の同一`IllegalStateException`に反する。対照の既知IOException＋再取得SQLは期待どおり固定Failure。出力は秘密値を含まず `/tmp/pgpt-pmo-20260923-handoff-probe-1.log`、SHA-256 `509b33d46b4437ee55f90327ff0d44bcb2f9842c884ff639babf6b6f30080406`。BUG195/YKT154の継続範囲として扱い、新BUGへ重複採番しない。probeは正式PT/coverageではなく、既存PT-BAT-032/034/035/036へ移植・再実行が必要。

## 後続の最小実装単位と未確定点

1. Handoff 1class：SSC063/SS341へbody/close/再取得の優先順位を補足。未知body＋再取得SQL、同一未知body/close、SQL＋close Error、既知対照の4反例とcallback回数・close回数・lock後条件をPT-BAT-032/034/035/036へ追加してから修正。現在の実測は最初と対照だけ。
2. Web session 2class：provider getter IAE（DB値正常）と不正row＋ResultSet.close SQL/Errorを独立PTへ。期待はresource固定障害・削除なし。SS314の既存oracleを変更しない。
3. API認証4class/5catch：provider/projection/0102/closeの固定Infrastructure区別をPTで実測し、個別に非該当根拠を保存。catchの一律縮小はしない。
4. JMS/残IO/低位JDBC：送達・不在・保護・確定errorの状態変化を伴う境界から順に。検索一覧だけではYKT完了にならない。

「unknown body＋別unknown reacquire」「unknown body＋fatal cleanup」の優先順位、Infrastructure境界でErrorまで固定化してよい範囲は未確定。全一般framework化・仕様期待値の緩和を採用しない。
