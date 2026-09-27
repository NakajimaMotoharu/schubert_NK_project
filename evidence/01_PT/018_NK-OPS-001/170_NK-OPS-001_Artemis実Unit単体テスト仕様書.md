# 170 Artemis実Unit：単体テスト仕様

Program NK-OPS-001/NK-MQ-001。Production `src/deployment/systemd/artemis.service`、Test `ArtemisServiceUnitTest`、VM NATIVE033。RD SYS002/004・OPS009、UI251/253、SS321§1/2/13・341§2/4・342§4/7・343§4/5、SSC100～103。これは実broker起動/clean journalや全8親停止の仕様書ではない。

| Test ID | 入力/操作 | 独立した期待と根拠 |
|---|---|---|
| PT-OPS-ARTUNIT001 | Production Unit原byteを読取り、固定dependency・identity・instance・ExecStartを行単位検査 | SS342§4 `After/Requires=schubert-nk-cleanup.service`、SS342§7 root・専用account、vendor instance実entryのみ。fake `/bin/true`/依存無視なし |
| PT-OPS-ARTUNIT002 | LoadCredential・Unit-private read-only bind・禁止設定を検査 | SSC103固定root sourceとprivate runtime path、`SetCredential`/PassEnvironment/他role passwordなし。秘密実体は読まない |
| PT-OPS-ARTUNIT003 | stop/start/resource/JVM設定を完全literal比較 | SS342§7：Restart on-failure、5/600、start120s/stop60s、KillMode control-group、SendSIGKILL no、MemoryMax2G、FD65536、Xms768m/Xmx1024m/Direct256m/Metaspace192m |
| PT-OPS-ARTUNIT004 | hardening/書込領域・host secret mutation禁止を行単位検査 | SS342§4/7・SSC103：専用data/log/tmp/lockのみRW、zero capability、private/strict、no ExecStartPre/StopPostによるhost property変更 |
| PT-OPS-NATIVE-033 | 隔離VM marker・専用UID/実instance/原本3SHAを事前照合、Unitを非起動install、daemon-reload/verify、`systemctl show`のId/loaded/固定policyを実測 | 実Unitとしてloadedでpolicy一致。Cleanup `not-found`なら`artemis.service`は起動しない。template検査/loadedとbroker readinessは分離。秘密source/content/Journald/raw InvocationIDはGitへ格納しない |
| PT-OPS-NATIVE-034 | 既存Artemis認証fileを内容非表示で形式/所有確認し、hash済み4行だけを固定root600 sourceへ新規複製。専用UIDのtest-only transient systemd Unitに同じLoadCredential/read-only bindを与え、UID・private mount inode/owner/mode・内容SHAだけを比較 | schubert-artemis UID994、private mount inodeはhost既存fileと異なり、private content SHAはroot sourceと一致。raw hash properties/InvocationIDをGitへ出さない。test-only transientは本物の`artemis.service`起動・Cleanup依存・broker readinessの代用にならない |

前提：Java25.0.4/Maven3.9.12、isolated Ubuntu26.04 VM/systemd。実行command・source commit/hash・終了code・coverage（Unit fileはJaCoCo対象外）・静的解析・実測/未実行・BUG/SSC・evidence path/hashは171/manifestへ記録する。純configにはJava line/branch coverageを捏造せず、Java test失敗/skipped/not-runを成功数に含めない。負例は固定外dependency/別path/fake/秘密環境のいずれも検査失敗。実broker起動はreal Cleanupとcredential sourceが揃うまで保留し、`--ignore-dependencies`を使わない。
