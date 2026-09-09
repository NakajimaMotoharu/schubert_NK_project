# NK-OPS-001 Linux flock 単体テスト仕様書

LinuxFileLock、RD OPS-009/AVL、UI251、SS311/341 §3/343、SSC-049/PG-D-146。shared storage低位capabilityの部分PT。root配布/認可/停止/実backup/親全体は未実装・別gate。

## 1. Fixture・期待値

保持済み一時regular fileをOwnedTransferDirectoryのcallbackから渡し、libc flockとutil-linux2.41.3のflockが互いに競合することを独立確認する。固定flags=LOCK_EX|LOCK_NB（2|4）、open=O_RDONLY|O_CLOEXEC、競合errno11だけOptional.empty。FD寿命はcallback内、最後のclose完了まで結果を外へ返さない。JDK public FFM、Linux amd64/x86_64/aarch64固定ABI。native故障はpackage-privateの狭いcall portで注入し、反射/private coverage操作はしない。生FD/pathは結果/ログに保存しない。

## 2. Test ID

| ID | LinuxFileLockTest.method | 操作・独立期待値 |
|---|---|---|
| PT-OPS-FLOCK-001 | nativeRoundTrip | 実保持inodeで獲得、callback値・内容不変、close後再獲得 |
| PT-OPS-FLOCK-002 | externalFlockInteroperability | Java保持中のutil-linuxは20、外部保持中Javaはempty/callback0、解放後成功 |
| PT-OPS-FLOCK-003 | fcntlIsNotFlock | FileChannel.lockを保持してもflock獲得可能。実flock競合は拒否し代用不可を実証 |
| PT-OPS-FLOCK-004 | callbackFailureAndClose | callback IO/runtime/null結果でもFDを閉じる。close故障時成功にしない、秘密canary非露出 |
| PT-OPS-FLOCK-005 | nativeErrorsAndFlags | open失敗・flock11/4/9/22/37・close失敗、固定flags/各close回数/呼出順 |
| PT-OPS-FLOCK-006 | inputAndPlatformContracts | null/path/FD表記/overflow/未知OS・ABI/欠落symbolをIO前に拒否 |
| PT-OPS-FLOCK-007 | concurrentSingleWinner | 同inode32同時呼出し、保持中1成功/31競合、解放後再獲得。別fileは独立 |
| PT-OPS-FLOCK-008 | retainedInodeAndDescriptorLifetime | 元path置換でも保持inodeだけをlockし、借用元FDを閉じない。CLOEXECと例外時回収、後続操作可能 |

## 3. Gateと証跡

実行はStorage module8 PT、6 Java moduleのline/method/class/branch100%とNullAway/SpotBugs/Spotless。callback/errno全分岐、null/負値/境界をliteral oracleで確認。OPS001/002の既存8 PTとは別Test ID、Program全体完了とはしない。正式run/source/branch/時刻/環境/command・exit/結果/coverage/BUG・SSC・manifest/hashを004へ記録する。source freeze後の全体run/証跡を使用し、正式40以前へ遡って算入しない。
