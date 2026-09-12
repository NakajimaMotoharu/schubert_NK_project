# NK-BAT-001 永続record保存の単体テスト仕様書

BUG159/YKT124: BAT049の不存在再試行もdir sync1を必須assertし、実unlink後のsync故障→不存在再試行で再同期失敗を注入して非成功を確認する。正常不存在はunlink0/sync1。readのOptional.emptyとは別契約であり全read PTは無変更。

BAT047は実publish後の4fileをtarget/durable-record-traces/PT-BAT-047-{anchor,active,begin,done-10}.txtへcopyする。Production encode再実行でactualを生成しない。020はSS/PG156と共通の独立literalからinputを作り、実file byteとの完全一致・4file過不足0を検証してevidence/input・output/durable-recordsへ分離格納しmanifestへhashを記録。019は各欠落/余分/改変を拒否する。

独立call inventory（全位置を故障注入しowned reader/writer/entry残0、borrowed root保全）。attributes/ACL/filesystem/readonlyは各同回数。read=各7・openEntry3/close3・openRead/readClose各1/read2/readSize2。new=各13・openEntry8/entryClose8・reader2/read4/readSize4・create/publish/openWriter/writerClose/force/sync/write各1/writeSize2。reuse=各13・openEntry8/close8・reader2/read4/readSize4・openWriter/writerClose/force/sync各1/writeSize2・create/publish/write0。remove=各7・openEntry4/close4・reader1/read2/readSize2・unlink/sync各1。正常call集合/各回数をliteral oracleと一致確認してから全位置へ注入する。

BUG158/YKT123はBAT048のdone0/10合法長差、BAT052のmetadata2位置とread後増大を追加。既存4reader/publisherの非該当根拠と回帰はevidence/logs/BUG-158-YKT-123.md。負canaryは017の1＋019の19＝20件。仕様/探索だけを正式認定へ加算しない。

PG-D-157/SSC-055先行19e22eb4、OPS-009/UI251/SS311/343 §6.14。DurableRecordFiles、EnvironmentInodePolicy.durable。実装前仕様。実fixtureは隔離file/FFMで、root UID/GID・ACL・filesystem許可属性だけ明示合成する。実root配布の認定ではない。

| Test ID | DurableRecordFilesTest method | 入力・操作・独立期待値 |
|---|---|---|
| PT-BAT-046 | literalReads | 手書きanchor72/activation109/completion140・141、全4suffix/active、返却byte完全一致・独立copy・初回不存在だけempty・readは無変更 |
| PT-BAT-047 | newPublication | 新規private part書込/短write/force/no-replace/sync、実file byteとinode・mode・part消失、公開target集合、全型 |
| PT-BAT-048 | sameRecordReuse | 既存同byte force/syncのみ、inode/size/mtime不変・write/create/publish0。別byteは無変更拒否 |
| PT-BAT-049 | expectedRetirement | 同byte/元inodeだけunlink/sync、初回missingは冪等、別byteや途中消失拒否・他file保全 |
| PT-BAT-050 | nameContentAndNull | null依存/引数、空/alias/複数segment/未知suffix、型/名前ID不一致、invalid bytes、mutation0 |
| PT-BAT-051 | metadataAndFilesystems | 全9属性の欠落/型/値、root/file mode UID GID nlink size device ACL、local各種正系・tmpfs/remote/unknown/null/RO拒否 |
| PT-BAT-052 | boundedChannels | read/write zero/負/上限超/position不整合、null channel/writer、size前後/EOF/過長、短IO正常、closeも非成功 |
| PT-BAT-053 | namespaceAndReplacement | 保持inode/同名差替え/ctime/mtime/root/device、part競合/target競合、最終readback後差替え拒否。保全と他file無変更 |
| PT-BAT-054 | allReadFailures | 全native/IO呼出位置・callback前後MISSING区別・複合close、独立inventory回数に照合し全scope回収 |
| PT-BAT-055 | allWriteRetireFailures | 新規/同内容/削除の全native/IO位置、途中part/公開後不確実性を保全。全資源回収/borrowed root不close |
| PT-BAT-056 | interruptionsAndUnknownRuntime | 開始/途中/終端割込保持、非root拒否、未知runtime/NPE非正常、原因/秘密診断漏れなし |
| PT-BAT-057 | concurrencyAndNative | 同instance32操作の直列化/同内容再確認、複数instance競合のno-replace結果、native factory読取/IO動作（合成属性と区別） |

ExpectedはPG156と同じ手書き非秘密literalを使用しProduction encodeで生成しない。Production method対応: constructor/name/content→050/057、read/probe/readStable/readFile→046/051～054/056、publish/write/force/readback→047/048/051～057、remove→049/053/055/056、begin/directory/file/finishおよび共通durable policy→全該当試験。全line/method/class/branch100%、NullAway/SpotBugs/format、既存環境reader/publisher回帰、全reactor・collector・負canary・trace一意性を要求する。Reflection/private method直接呼出でcoverageを作らない。

独立native/IO fault inventoryは実装後reviewで具体回数を記載し、各位置の失敗とowned資源0・保全を検証する。探索結果だけを正式合格にせず、010とevidence/manifestへ実行日時/環境/branch/commit/command/exit/coverage/BUG/hashを記録する。未実行/failed/flaky/skippedは非合格。固定namespace/graph/親OS lock/子終了/GC/DB照会は未完了の別実装範囲。
