# NK-OPS-001 Publication限定復旧・管理所有回収仕様

関連UI251/SS343 SSC266・SS353、QA047、451。対象Main769/VM1292/boot3d69、失敗Root1456のINVALID・permit・publication intent3entry、owner/launch無し。old Root成功/旧normal closeを期待値にしない。

|Test ID|入力・操作|独立期待値|
|---|---|---|
|PT-OPS-PUB1487001|手書きINVALID epoch/permit・空intent、実FD/synthetic root/tmpfs。型付きreadRevokedはdataだけ、canonical observeQuarantine/retire/dirsync|epoch/permit全byte不変、元同intentのみ退役、owner/Pair/launch/ISSUED履歴を創作しない|
|PT-OPS-PUB1487002|928全IO位置のfault、missing/null・foreign/余分/非空marker、whole-stopまたはM/A proof欠落、post-unlink未知|修正前故障の拒否、別namespace変更0、同M/Aが証明できる時だけ厳密quarantine。Production expected生成0|
|PT-OPS-PUB-OWNER-KERNEL-001|現PID/UID/GID/ticks/cgroup/tasks/FD/lock、二journal POSIXと一perfdata FLOCK|POSIXは現FD、perfdataは同PID固定mmap/同devino/rw-s/offset0/32KiB・994979/600/nlink1、M/Aは実FD保持。FDを発明しない。実v3復旧は未実行|
|PT-OPS-PUB-HANDOFF-001|実管理父子92297/92323・固定source/fulloriginal・actualM/A/同backend/advisory/単一Bus・十Ref/current二読|信頼済みinputは存在/hash一致、handoff出力だけnew-only。PID/ticks/argv/UID/FD等の連続再検証後、耐久一回予約→子→父の普通pidfd TERM。service/epoch/intent/DBwrite0|
|PT-OPS-PUB-HANDOFF-PEER-001/002|独立SQL numeric境界2/2147483646、actualhost(inet)、TCP4/IPv4-mapped TCP6 word endian、両FDinode/port|localhost127のみ、両端一意一致。golden5432/port1/65535、null/unknown/native::1/foreignIP/不正hex/長さ/0port/余分を拒否。DNS/ネットワーク設定変更0|
|PT-OPS-PUB-HANDOFF-POST-001|pidfd terminal後/proc reap有限観測、別new-only独立全closing|本人/DBpeer/advisory/M-A/旧Bus0と全24DB/full32/187/原本Backup/native/current二読不変、新metadataRef正常close。旧actor/旧metadata close/旧Root結果はUNKNOWN/failed維持、再signal0|

command・source・hash・結果は660へ対応。固定JDK25.0.4、当Main qualifiedABI/helper JARf0584b…、Java WerrorとPython工具の独立normal/boundary/negativeを用いる。27,616assertは工具fixtureでProduction PT件数へ加算0。coverage451四100は不変更、当primitive/回収だけで全leaf/正式/IT/STを完了にしない。
