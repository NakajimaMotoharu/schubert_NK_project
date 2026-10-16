# 新親timeout・独立失敗認証

2026-10-16、Production7bb/PG3976/boot79a、BUG1332/YKT1098/QA047。元Root167140/INVbbcdb699/795724は21:02:52JSTにtimeout143、1800.072841秒。旧8208の失敗とは別に保存。同sourceの新observer改善だけでは今回の30分失敗を防げなかった。開始/親/root VMを再演せず、capture/readonly authenticationのみ実施。

元observer69058 actual0/12:02:54.561227Z、全十Ref正常返却。API807944/a2854d41、Web808319/2a74a4ca、Caddy808868/25aa7706のsame-owner/strictTLS login200は限定到達。Root失敗なので4252正常terminal/rows/seal・Browser/normal-owned/native後続はnot-run。旧/.done/observer0で正常を補わない。

| Test ID | 独立期待値・実操作 | 結果 |
|---|---|---|
| PT-OPS-CURRENT-FAILED-PARENT | literal PID1 start/failed＋Unit timeout143、canonical done同run/cutoff/act・0/10はdata-only、foreign/null/欠落/偽normal/重複/不正時刻拒否 | 純3試験/FES0、全host/全3payload静的0 |
| PT-OPS-CURRENT-FAILED-CAPTURE | fresh VM/forward/source/BOM/187署名、全24表・原本Backup/native/Unitの二読、管理lock0、変異0 | 4300/29047 actual0、private0c22c527、4actors/DB4/native56、原本・rows不変、1800.072841秒 |
| PT-OPS-CURRENT-FAILED-AUTHORITY | 全10 Unit/full32設定/実file、各ordinary NSS/UID/GID/groups/caps/NNP/exe/argv/cgroup/子0/全FD二読、権限発行0 | 4306/31002 actual0、private63269de9、全4詳細FD安定（Artemis173/Caddy7/API144/Web159）、startup37/native56、DB4/管理lock0 |
| PT-OPS-CURRENT-FAILED-PID1-DONE | 同新INVのPID1原本6record・job167140、Root/kernel空、現Unitとdone byte再読 | 4302/10106 actual0、private journal24e22836、done654073a05ac1101060b235c8dc1e058efb94f0884e4eb87613b7f182b199644a、normal/authority全false |

4306 startup=37 entry、permit9/owner9/launch18/epoch1、start intent0。33等の旧cohort件数を転記していない。元原本/Backup/DB・鍵/全native/旧成功失敗・Currentbaseline/stash7は保持。全24は安定観測で、正常runの独立post後条件合格ではない。raw DB/FD/原本/native/argv/stackはGitへ出さない。

SS287～289の旧cohort/Java固有literalを新Rootへ直接流用できないためSSC291を修正前draft起票。新instanceの現根拠→Java/epoch oracle literal固定・再compile→全189/32/37/56保存・fresh M/A/RODB/十Refのread-only inspect→設計only main→必要な同四owner逆順6停止/revoke/全scope正常/別freshpostへ進む。旧metadata keeper/既Caddy停止を回収対象へ混入せず、今回はCaddyも新世代で未停止。現段階のread-only証拠だけで回収権限を発行しない。

検査結果cache/scan省略/Root1800延長をしない最小性能是正候補は981に記録。原因/対策・新source必要PT/全回帰と実Root再発防止は未完。正式1964/53・旧17/190・工数null・QA051final/F03/CHR/全四100/451未完、Production PT追加0、通常単位で停止しない。
