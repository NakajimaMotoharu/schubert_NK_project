# NK-OPS-001 保守lockfile検証単体テスト仕様書

MaintenanceFileLock / RD OPS-009・AVL / UI251 / SS311・341 §3・343 / SSC-049・PG-D-147。親root controller内部の固定file adapter。親の停止・実backup・DB引渡し/全朝batchを完了としない。

## 1. Fixture・独立oracle

隔離した一時/run相当→schubert-nk→maintenance.lockへ実NOFOLLOW保持inode・実LinuxFileLockを接続する。PT seamでUID/GID0・tmpfsを合成し、それ以外の実属性とliteral期待mode0755/0600・nlink1・size0を検証する。公開factoryの実環境では非rootをIO前に拒否する。root権限を得たりhost /runへ書いたりしない。実際のroot/tmpfiles配布はITで別確認。native errnoと属性faultはpackage限定portから注入しProductionでexpectedを生成しない。

| Test ID | MaintenanceFileLockTest.method | 入力・操作と期待 |
|---|---|---|
| PT-OPS-LOCK-001 | admittedRealLock | 合成root属性＋実inode/flock、callback値/外部flock20・解放後0、内容不変 |
| PT-OPS-LOCK-002 | contentionAndIndependentInvocations | 外部保持/同時32でcallback1回だけ、失敗側0回、後続再取得 |
| PT-OPS-LOCK-003 | rootAndFilesystemPolicy | effectiveUID、owner/group/mode、ACL、FS type/read-only、dev不一致を無操作拒否 |
| PT-OPS-LOCK-004 | inodeAndAttributePolicy | symlink/directory/hardlink/nonempty、null/欠落/未知型属性を無操作拒否 |
| PT-OPS-LOCK-005 | replacementAndPostconditions | lock/run/app directory交換、処理後mode/ACL/identity変化を拒否し元FDをclose |
| PT-OPS-LOCK-006 | ioAndCloseFailures | open/属性/ACL/FS/close失敗、callback IOException/runtime/null、固定診断/全所有回収 |
| PT-OPS-LOCK-007 | constructorAndNativeBoundary | 全dependency/null、固定公開factory・native NIO属性/FS、非root正規拒否 |
| PT-OPS-LOCK-008 | fixedProvisioningContract | SS343§6.15の`maintenance`/`startup`/`backup-request`/`cleanup-request`とM/Aを含むtmpfiles固定7pathを独立literalで型/mode/root/boot限定・非truncate/非delete照合。BUG-318/YKT-251の3dir欠落をRED→GREENで確認し、実boot生成は隔離rootで別途検証。現役VM `/run` には再実行しない |

## 2. Gate・証跡

BUG-142/YKT-112: 固定/runはUI251/SS341の必須配置であり可変設定へ変えない。MaintenanceFileLock.create単一methodのDMI_HARDCODED_ABSOLUTE_FILENAMEだけEXACT annotationで理由・owner・PG gate/配置変更時の再reviewを記録する。PT007は固定literal/非公開constructor/単一限定annotation/provided依存をsource contractで検証し、coverage/private状態へ介入しない。報告の静的指摘0はこのレビュー済み1件を明示した後の未解決件数であり、無条件に抑止ゼロとはしない。

BUG-141/YKT-111: 実NIOのreadonly oracleは`/proc/mounts`の/dev/shm・/sys各一意mountのro/rwと独立照合する。/sysをcontainer設定だけで常時ROと仮定しない。policyのreadonly拒否は003のliteral synthetic3 inodeで維持する。access ACLが対象でありdefault ACLによる将来のfile生成権限は本read-only admissionだけで検証済みとしない。

Batch module選択試験と全reactor clean verify、line/method/class/branch100%・NullAway/SpotBugs・Spotless。022 OPS証跡scopeへ独立PT-OPS-LOCK IDsとbatch class coverageを追加する。019所属/欠落/failed/flaky/skipped canaryも同期する。command、OS/JDK/tool、source/run/branch、時刻/exit、期待/実際、coverage、BUG/SSC、manifest/hashを006へ記録する。未実行・failed・途中結果を合格へ含めない。
