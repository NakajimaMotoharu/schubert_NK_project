# NK-BAT-001 root manifest reader 単体テスト仕様書

PG169/SSC062（先行c2da887a）。NK-BAT-001/BAK/BKO/OPS009/UI251/SS311・341§6.7・343§5.3。仕様先行後に実装、正式PT-WEB-20260913-13/source82055460で16件認定。BUG195/SSC063のclose優先順位・横展開と未完了残候補は048参照。

対象 .file.BackupManifestReader constructor/read/全内部method・IO/安全close。fixtureは公開合成artifact-manifest.json（964byte）、directory 20260913-000002-12345678-9abc-def0-8123-456789abcdef、専用UID2000/GID2001、rootUID0/GID0を非特権metadata adapterで区別する。実Linux FD/IOとsynthetic root入場を混同しない。独立期待値は公開JSON/SSbyte規約とliteral値。productionをexpectedに呼ばない。

正式13/source82055460で下表16件を認定（047/048）。Production追跡: constructor2/全field invariant→BAT228/237/240、readと所有scope全lambda→BAT226～241、directory/capture/metadata→BAT228～231/234/237、readFile→BAT232/234～236/238、decode→BAT226/227/233、guard→BAT234/236/237、NioIo.attributes/open→BAT240/241。全method/line/branchを同JaCoCo XMLへ追跡し、inline lambdaも除外しない。

| Test ID | class/method | 目的・前提・入力/操作・独立期待値 |
|---|---|---|
| PT-BAT-226 | BackupManifestReaderTest.canonicalRootManifest | 独立964byte goldenをroot所有として読み、固定完全handle/time/3file size/hashをassert。Production encodeによるexpectedなし。 |
| PT-BAT-227 | BackupManifestReaderTest.nameAndFullHandleBinding | nameのpart/区切り/大小/長さ/別runと両完全handle全属性を改変し拒否。同じ真正bundleだけ許可。 |
| PT-BAT-228 | BackupManifestReaderTest.directoryAndOwnerContracts | root/child mode/uid/gid/link/size/同device/RW、unsigned32境界とeffectiveUID前後を確認。 |
| PT-BAT-229 | BackupManifestReaderTest.manifestMetadataAndAcl | MANIFEST全9属性のnull/型/値、root0/0600/regular/link1/1～4096/ACLなしを全拒否。 |
| PT-BAT-230 | BackupManifestReaderTest.rootAndChildRebinding | root/childの保持中/再open時差替え、属性変更をfail closed、別未対象generation不変更。 |
| PT-BAT-231 | BackupManifestReaderTest.manifestReplacementAndMutation | 保持manifest書換え/rename/symlink/hardlink/同名別inode/mtime/ctime改変を拒否。 |
| PT-BAT-232 | BackupManifestReaderTest.sizeAndReadBoundaries | 1/4096/4097、zero/短縮/過長/position不整合/EOF不整合、size前後、split reads。 |
| PT-BAT-233 | BackupManifestReaderTest.canonicalByteRejection | canonical codec不正を固定StorageIoExceptionに限定、別真正内容はfull binding不一致で拒否。 |
| PT-BAT-234 | BackupManifestReaderTest.everyIoFailure | 独立に数えた全native/IO出現点へ1つずつfault、非成功/所有close/借用root継続を確認。 |
| PT-BAT-235 | BackupManifestReaderTest.closeFailurePrecedence | read primaryとclose IO/Runtime/Error複合、fixed診断とunknown identity、到達回数・suppressed件数をassert。 |
| PT-BAT-236 | BackupManifestReaderTest.timeAndInterrupt | 30分直前/一致/超過/逆転/wrap、全clock地点interrupt・最終clock内割込、flag保持。 |
| PT-BAT-237 | BackupManifestReaderTest.nullAndUnknownProviders | constructor/API/port null、未知Runtime/NPE/Errorを正常化しない、buffer消去とredaction。 |
| PT-BAT-238 | BackupManifestReaderTest.borrowedRootAndClosed | readerはrootを閉じず、closed root/child/entry/失敗後呼出を成功へせず、owned resource解放。 |
| PT-BAT-239 | BackupManifestReaderTest.concurrentSerializedReaders | 同instance64呼出を直列化し不変結果、一方のfault後も他caller状態を汚染しない。 |
| PT-BAT-240 | BackupManifestReaderTest.readOnlyNativeAdapters | 実Nio adapterが元byte/属性を読み、write/chmod/chown/unlink/rootcloseなし、秘密値を記録しない。 |
| PT-BAT-241 | BackupManifestReaderTest.independentTraceAndDownstream | reader実返却の公開run/name/sizeをtrace化し独立期待と比較、別段ArtifactVerifier照合を実行して役割分離。 |

正常/異常/境界/全例外/null/再利用/並行・全branchを網羅する。failed/flaky/skipped/not-runは合格へ算入しない。全line/method/class/branch100%、NullAway/SpotBugs/Spotless、独立collector inventory/trace negativeを要求。既知実装違反は修正前915、共通原因916、上位設計はSSC/QA分類で先行登録。

JDK25.0.4/Maven3.9.12/Linux/工具は421。選択Batch-am PT→全clean verify→020/019/018の38scopeで確認する。command/branch/対象commit/日時/exit/入力/expected/actual/全coverage/BUG/SSC・sanitized traceとhashは047/evidence/manifest.jsonへ記録する。実dump/age/secret/master/sessionを格納しない。

本部品はroot所有claimの読取りのみ。root生成/真のdump・tar・age/永続確定/7世代/DB pair全成功/親OS lifetime/実NKCHR/IT/STを完了としない。
