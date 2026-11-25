# NK-OPS-001 run環境公開・同run再開・retire単体テスト仕様書

PG-D-154/SSC-049先行aa2baa3a。OPS-009/UI251/SS311/343 §6.11。batch.file.InspectorEnvironmentPublisher、共有EnvironmentInodePolicyと既存Reader。親OS lock/固定namespace/子終端/永続run原本はcaller契約であり合成成功扱いしない。

本表のPT-OPS-PUB-001〜003はInspectorEnvironmentPublisherTestのJava単体を一意に指す。678の旧公開工具の同名ラベルは、678の現行ORDPUB IDに対応する。

| Test ID | method | 入力・操作・独立期待値 |
|---|---|---|
| PT-OPS-PUB-001 | createAndRetire | 固定UUID/時刻→独立literal2行、0600/nlink1、part消失、target公開、retire後不存在、再retire成功 |
| PT-OPS-PUB-002 | sameRunAndDifferentRun | 公開済同run再同期はinode/content不変、別UUID/±1μs拒否で既存保持 |
| PT-OPS-PUB-003 | privatePartCollisions | empty/partial/完成/別cutoff/通常file/symlinkの既存partをCREATE_NEW拒否、target作成なし、外部inode不変 |
| PT-OPS-PUB-004 | permissionsAndNull | 9metadata型/欠落、type/UID/GID/mode/link/device/ACL/FS/null/empty/readonlyを検査前後で拒否。未admitで書込なし |
| PT-OPS-PUB-005 | boundedWrites | partial進捗、0/負/超過count/position不一致、初期/終期size違反、force/close失敗、110境界を独立byte長で検証 |
| PT-OPS-PUB-006 | replacementsAndRetention | root/part/target差替え、同byte別inode、hardlink/dir/symlinkを拒否。書込み保持inodeを別名前に誘導しない |
| PT-OPS-PUB-007 | createFailureMatrix | 新規経路の全metadata/ACL/FS/open/read/write/force/sync/close位置、複合故障と資源解放、部分file保全 |
| PT-OPS-PUB-008 | reuseFailureMatrix | 同run経路の全IO/同期位置、成功0に補完しない、target保持、原因/suppressed秘匿 |
| PT-OPS-PUB-009 | retireFailureMatrix | 同run検証/同名再確認/unlink/syncの全位置。開始不存在だけ成功、途中MISSINGは失敗、unlink後sync failureは不確定 |
| PT-OPS-PUB-010 | interruptionAndRuntime | 開始/途中/最終割込flag保持、未知runtime escape、全owned resource close、終了前の成功禁止 |
| PT-OPS-PUB-011 | concurrentInvocations | 同instance並行prepare/retireの直列化、同run inode再利用、異runは別targetへ混線しない、有限wait |
| PT-OPS-PUB-012 | nativeAndConstructor | 公開factoryの実非root拒否、Nio writer保持FD/force/close実行、null依存/closed root拒否。root寿命はcaller所有 |

Coverage4指標100%、NullAway/SpotBugs/format、既存EFILE8回帰で共通policy抽出の非互換0を確認。期待値はSS固定ASCII/Unix値・native後条件・独立全fault位置一覧、Production methodからexpectedを生成しない。実行command/OS/JDK/branch/source/結果/BUG/hashは018とevidence/manifest.jsonへ記録。failed/flaky/skipped/not-runを成功へ含めない。
