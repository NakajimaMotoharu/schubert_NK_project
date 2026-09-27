# 子の独立起動context PT仕様書（PG299・未認定）

Program NK-OPS-001、Bootstrap.ChildStartupContext.inputs/capture/verify/Observed/NativeIo。RD SYS-002/004・OPS009、UI212・251、SS311/342/343、SSC086～088、D04/05。実LinuxStartupAdmission root2FD admissionの後だけ用いる照合器で、単独で起動許可を発行しない。

| Test ID PT-OPS-CHILDCTX | 目的・fixture/入力操作・独立期待値 |
|---|---|
| 001 | 独立17行公開proof、literal boot/Invocation/PID42/ticks12345/A128/dev123/ino456/UID200/GID201/groups200,201,202/config c×64/release b×64。API/Web cgroup成功、unsigned最大dev/ino |
| 002 | 狭い2FD env 128～65535、欠落/未知prefix/大小文字alias/先頭0/同番号/INV zero・不正/null拒否 |
| 003 | 全proof attestationの独立変更、native A descriptor/identity、自己UID/GID/groups/cgroup/caps/NNP/hash差分を拒否 |
| 004 | stat field22の1/longMAX、5cap各非0/NNP0は観測するがverify拒否、snapshot不変 |
| 005 | proc/PID範囲/boot/stat/ASCII byte/4096上限/死状態/overflow/先頭0/UID不一致拒否 |
| 006 | required status各欠落・重複、4IDs不一致/未知/uint sentinel、groups重複/17件、cap形式/NNP不正拒否 |
| 007 | 全verify引数null、bytes/constructor null、unknown同一identity保持、32並行独立観測 |
| 008 | 実通常UIDのproc filesystem/boot/stat/status/cgroup/native uid読取、非存在PID拒否。通常processの観測だけで固定service proofを許可しない |

独立oracleは明示Linux text/golden、production encoderでexpected生成しない。Native017はhardened fixed API/Web名Unit、root実context/A/sealedcanonical→samePID setpriv→実子2FD/rootmetadata/seals/自己proc/NSS照合→proof早期close/A ready境界closeを確認。permit/root/Ops/schema/hashは公開fixtureなので全gateの証拠ではない。再送は非該当、null/境界/例外/並行は上記。固定proc private helperのDMI portabilityのみEXACT review、null/security/coverage抑制なし。116/provisional manifestに実command/source/coverage/証跡hash。
