# NK-OPS-001：PG460限定退役・Caddy NSS結果

対応仕様330、SS342343/SSC181/QA047、BUG685686687/YKT490491492。Production source8e97eb9138828010926cd47fd10868d8a2d54f11、同署名PG459/027を維持、dirty工具とclass SHAは下manifestに別記。実行日2026-10-05 JST、記録のない秒時刻は補完せず、収集日時と実行日時を区別する。

安全証跡：`evidence/provisional/PG460-nss-pair-v1/manifest.json`、SHA256 **5319a59963b4cd670044040a6c88ff8a5ce103d4a0df674840733a84b8527c2c**。Test ID毎の固定flag/hash・command・環境・退出値・独立oracle・非合格履歴を収録。raw原本/NSS/gshadow/dump/owner/permit/spy/credentialはGit外私有に保持。

| Test ID | 実結果・退出 | 証明範囲 |
|---|---|---|
| PAIR460-PEERS | 14assert/0 | 実Root→ordinary/同親/info5/世代を拘束、入力改変を拒否 |
| PAIR460-POST | 278assert/0・Werror0 | literal16→13、全13欠落/未知/全phase/型付き3退役順、旧保持8を保全 |
| PAIR460-NATIVE | isolation72788/verify5538/正規退役61229 actual0 | 真正M/A/DB、281全14列/23business/原本pending/Backup/Transfer不変、全9kernel空、全owned正常帰還、INVALID同epoch/13非intent、新start/permit/DDL0 |
| NSS460-LITERAL | host-v3 25assert/0・Werror0 | group/gshadow対象memberだけ、他member/password/admin/行構造/primary契約 |
| NSS460-FIXTURE | native-fixture-v3/session44293 32assert/0（host25を含む） | 実gpasswd --root、私有fixture literal前後/自動backup、実NSS不変 |
| NSS460-NATIVE | v3/session91620 actual0 | root同期before-image後、実gpasswd対象だけ除去、UID993/GID978/groups978、全13startup byte/inode/281原値/原本Backup不変、全scope正常帰還 |
| NSS460-RESTART | 03:20:02一度発行、結果未受入 | 親471458/271136…・元03:50:02期限、ready/TLSだけで全親成功化しない |
| CHR460-A01 | 実TLS待ち、未実行 | 共通Current driver、固定baseline title一箇所DIF001/QA045だけ差分、全CHR gate代用0 |

非合格：recover-v1は未定義引数`recover`拒否actual1/変異0、正規退役は無引数v2で別記。NSS fixture-v1はBUG687（gpasswd -R=rootという誤り）actual1、実対象変更0、--rootへ是正してv3を新only閉classに配置。旧失敗は残し合格へ加算しない。

BUG686/YKT491はpost13の全対象独立判定とnative当世代全後条件で限定修正完了。BUG687/YKT492はfixture/native管理mainの用途別確認・再発防止32assert・実管理0で限定修正完了。BUG685/YKT490はNSS原因確定と是正まで実証、**新親全体/DONE/intent正常退役/outer0or10未受入のため対応中**。旧BUG544/YKT388はOS停止や今回の限定退役で解決認定しない。

Production PT追加0、全Production coverage100/正式認定更新0。正式run24/1964PT53scope/48.3%は維持。次は同親へ再付着し新世代Caddy/kernel/同peer/TLS/DONE/全outerと実CHR、同source/run nativecoverage及び正式品質へ進む。
