# 156 実release・rootDB結線 PT仕様（未実行）

Program NK-OPS-001 / NK-BAT-001。RD SYS002/004・OPS009・DAT009、UI212/251/253、SS331/341/343 §9.1/11.1、SSC095096、PG-D314、BUG291/YKT224。実装前の仕様。限定成功や未実装をPASSへ算入しない。

対象: StartupReleaseManifest.verify（公開claimsの実file一致でauthorityではない）、ReleasePayloadVerification（保持release全集合・byte/ZIP/SQL）、RootReleaseAdmission（fixed root入口/private ctor）、MorningDatabaseSession.Session.beginBackup（mandatory root admission/schema）。既存sha256/read-only原本利用は保持する。

| Test ID | 独立入力/操作・期待値・観点 |
|---|---|
| PT-OPS-BOMPROFILE-010追補 | 正規shared版に別storage/protocol/bootstrap版GAV＋異なるlibを追加、一般GA別versionも追加→拒否。期待版の同GAV各role同byteは従来どおり通る。lib配下深い階層はfixed thin layoutで拒否。 |
| PT-OPS-FULLBOM-001 | test-only literal release/JSON/ZIP・SQL、独立JDK SHA256/固定CRC vector、実FDを保持。全payload＋祖先＋2管理fileの正確集合、公開immutable版/digest/六列期待だけを全close後に返す。|
| PT-OPS-FULLBOM-002 | null/空/未知・extra/missing/サイズ/hash/VERSION/SHA256SUMS、本文を実alter→拒否、秘密diagnostic/cause0。実DBから期待を作らない。 |
| PT-OPS-FULLBOM-003 | typed UID/GID/mode/ACL/type/nlink/devino・RO/admitted namespace・alias・symlink/hardlink・current/祖先置換→拒否。synthetic policyと実native factoryを混同しない。 |
| PT-OPS-FULLBOM-004 | 同一held manifest→parse→全treeの全取得/read/EOF/position/close故障と既知・未知複合。全owner一度close、未知identity保持、不明scopeを成功化しない。 |
| PT-OPS-FULLBOM-005 | API同梱SQL名/byte/欠落/余分/重複ZIP entry、nested/shaded sharedclass・列挙外Class-Path→拒否。literalCRC normal/CRLF/BOM第一行/後続BOM/UTF8で固定Flyway13.4 primary比較、SHAとCRCを混同しない。 |
| PT-OPS-FULLBOM-006 | all shared jar各role、declared lib完全集合、同GA版shadow/深いlib・未知dir→拒否。適合するthin配置だけ通る。 |
| PT-OPS-FULLBOM-007 | 割込・真の4並行read・namespace前後mutation・独立owner。各scopeの入力と結果混線なし。 |
| PT-OPS-FULLBOM-008 | 実native読取port/固定host-view factoryの拒否と、隔離VMの真正root/fullBOM正例を分別。同一class hashで補完するまでnative未網羅を除外しない。 |
| PT-OPS-ROOTBOM-001～008 | public claims/任意reader/boolean/行からauthority生成不可（公開API反射も確認）、固定RootContext→固定原本execute内fullverify→全postcheck/close完了後private ctor。OS/JDK/版不一致、null、全close/未知、current/原本変更、割込/並行、ordinary root拒否、実VMroot正例を別記。 |
| PT-OPS-MDB-001～008追補 | 既存3arg原本参照専用constructorはbegin repository/SQL前に拒否。Production opaque root admission付きのみ現在原本/fullBOM/schemaをrole/advisory後・両begin前に検証。null/不一致/全投影故障/known-unknown cleanup/commit ambiguity/外国thread/失効/並行は非成功・handle不返却、borrowed/schema・owned connectionの解放契約を維持。 |

fixtureは隔離一時dir/公開synthetic ZIP/独立六列schema row・roleDB。期待hashは実装methodを呼ばずJDK独立計算、SQL CRCは固定literal vector＋installed Flyway一次実装を使う。固定署名はRFC8032公開vector、実配備の秘密鍵・raw token/password/DB dumpはGitに保存しない。

実行commandはJDK25.0.4/Maven3.9.12/固定repositoryの対象module `test`＋JaCoCo0.8.15/report＋SpotBugs4.10.4.0/check。target commit/branch/OS/version/終了code/各Test ID input/expected/actual/coverage/BUG/SSCと退避XML/hashは実行後manifestへ追記。全line/method/class/branch100%、全negative/例外/並行・独立oracleを要求、unknown native/未実行は未合格。source共用security/fullBOM/Morning接続変更の横断gateでは全6回帰、同run全採取前に次source/testを変更しない。

署名publisher・activation M/A/全Unit終端/INVALID、元Native027のpending原本resume、実worker/3archive/7gen/whole-parent30分、permit/main/実NK CHRは別の未達必須条件。本PTを全起動/R2/R3・IT/ST完了の代用にしない。
