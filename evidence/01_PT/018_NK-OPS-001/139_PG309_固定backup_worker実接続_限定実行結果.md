# PG309 固定backup worker 実接続：限定結果

2026-09-28 JST、dev-foundation、c44c9fc3a後の保存source。仕様138、SSC092/SS3416.1/3436.6、BAK/BKO/OPS009/UI251/NK-OPS-001。正式run24/1964PT/53scope・48.3%は更新しない。

Bootstrap24（BREQUESTCRED/BACKCRED/SERVICEID）、Batch32（BREQ/BREQFILE/UNIT）とworker関連24（BWORK/DBCP/ARCHPROC）がfailure/error/skip0・静的0。異なる限定実行を一つの正式runへ合算しない。request/files/probe/snapshot変更subject全6counter missed0。BWORKはhost24PTと同jar/hashの隔離native025実測JaCoCoを標準ExecFileLoaderで合成し、Worker line99/method19/class1/branch64・NativePorts line23/method13/class1、全6counter missed0。除外なし。全Production security回帰は次の固定sourceで実施する。

実行commandは各module `mvn -B -o -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository test -Dtest=<manifestのsuite> jacoco:report spotbugs:check`、Java25.0.4/Maven3.9.12。追加前format拒否/fixture compile/独立oracle・静的失敗はmanifest hashへ保全し合格へ算入しない。新inventorycanary初回2error（literal Batch数と共有package owner漏れ）→明示4group/owner/各独立8method/prefix、Batch476/OPS内Batch189の予定inventoryへ是正、105canary PASS。品質期待値は変更しない。

BUG272: 古代Tokyo offsetは+09:18:59、lowerUTC0000-12-31T14:41:01Zと直前/old15:00UTCのliteralを用い既存命名を維持。BUG273: 固定targetをnamed factoryにし旧null port constructor互換を保持。BUG274: copy invariant先行＋worker取得後finally消去、全IO/unknown/close・heap0確認。BUG275: SS必須の固定Linux path3methodだけEXACT portability annotationを既存規約同様に根拠付きで指定。全体抑制やcoverage除外なし。各BUG/YKTは直接限定再試験済・横断回帰待ち、BUG271/SSC091は親M/A未結線なので継続中。

## PT-OPS-NATIVE-025

Ubuntu26.04/systemd/隔離VM marker pgpt-r2-20260927-01。hostOS設定は変更しない。新固定schubert-nk-backup.service＋Production Worker main、専用NSS uid992/gid977/groups977・986、自己proc/MainPID/Invocation/cgroup/zeroCapabilities/NoNewPrivileges、root非秘密request→systemd credential→tmpfs0600 copy→実pg_dump/list→heap/file消去/readback/unlink/sync→全close→fresh code0を実測。root requestは読戻し一致、dump600/part700/new-only、全Unit Processes空と前後stableを実Probeで確認。15:25:35～36 UTC起動/成功、停止後MainPID/ControlPID0、固定kernel cgroup不存在、原本request retireを独立root fixtureで確認。

初期native classpath不足でcompile失敗、cold/stopped Unitがsystemd GCでGetUnitProcesses unavailableになるfixture失敗は成功へ代用しない。Production read-only Probeはfailclosedのまま維持し、test rootでは固定cgroup2 namespaceでexact NoSuchFileException＋state前後一致を独立確認した。一般IOを不存在と見なさない。Production親にもこのcold/停止後契約を真正root観測で接続する必要がある。

native classpathはPG309 Batch/Bootstrap jar優先＋旧隔離dependency fixtureで、release BOM/親M+A/current permit/DB両step/3artifact manifest/7世代/全backup総budgetは未認定。実業務Web/API/R2/R3/CHRへ読み替えない。dump・秘密copy・pgpass・raw値はVM privateのみ。host recovery keyは移動しない。VM dated partとworker.execは保全し同一new-only runを再実行しない。

対応Test ID→class/method/入力・独立期待値は138と各fixtureのliteralに固定し、実行suite/hash・coverage・source inventory・不合格log hashを [manifest](provisional/PG309/manifest.json) に格納。request/Unit32のXMLは後続cleanで失われたためlog/元限定counterを記録し、XMLを存在すると主張しない。計画済み全回帰で再取得する。sanitized logは同directory、raw DB dump等をGitへ格納しない。
