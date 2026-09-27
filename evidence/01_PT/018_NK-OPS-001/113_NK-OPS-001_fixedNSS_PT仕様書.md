# 固定service NSS PT仕様書（PG298・未認定）

Program NK-OPS-001、Bootstrap.FixedServiceIdentity.resolve/Value/NativeQuery。RD SYS-002/004・OPS009、UI212・251、SS311/342/343、SSC088、D04/05。固定getentのpasswd/同名primary group/schubert/schubert-read/APIのみschubert-webを独立照合し、暗黙全membershipを採用しない。

| Test ID PT-OPS-SERVICEID | 目的・事前fixture/入力操作・独立期待値 |
|---|---|
| 001 | literal passwd/group API999:981→980,981,982,986、WEB998:980→980,982,986。固定argv順、sorted immutable、診断redact |
| 002 | 全固定row欠落/余分/別名/重複/改行欠落/shadow marker違い拒否 |
| 003 | UID/GID 1～4294967294、0/先頭0/符号/overflow/未知値拒否 |
| 004 | primary不一致/重複group拒否、member欄の任意追加で明示groups不変、initgroups使用0 |
| 005 | ASCII byte上限1024成功（15byte prefix+1008member+LF）、1025/control/空/null拒否、Value constructor invariantと防御copy |
| 006 | 固定query clear環境/exit/timeout/interruption/起動失敗で非成功、秘密継承0 |
| 007 | stdio/process各所有close障害とunknown優先、戻り正常化禁止 |
| 008 | 32並行独立結果、実未配備hostで正当拒否、factory/native境界 |

期待値は本testのliteral公開NSS vectorから作りproduction resolverで生成しない。VM native016は実getentによるAPI999:981とWEB997:980を別独立fixtureへ照合（単体syntheticWEB998はVM値と混同しない）。再送/DBは非該当、並行・例外・null・境界は上記。command/環境/source/hash/coverage/結果は114とprovisional/PG298-299/manifest.json。新規TDDのfixture修正はProduction仕様違反ではなくBUG対象なし。全起動gate/正式認定は未達。
