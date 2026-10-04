# 署名027・固定Caddy配備仕様（PG456／SSC178）

対象：NK-OPS-001、`ReleasePayloadVerification`／`ReleasePayloadVerificationTest`、`AssembleReleaseFixture`、`Pg387TrustedDeployment`、`Pg455ReleaseSchemaToolTest`、`Pg456SignedMigration`／同Test。根拠：RD NK-OPS-001/NK-DAT-001/NK-WEB-002、UI241/242/251、SS331/341/342§3/343§3、回答済QA048/050、SSC178、PG-D372。これは隔離PG/PT VMの配備依存であり、runtime permit発行・業務ready・IT/ST認定ではない。

## 独立期待値と試験

- FULLBOM006：許容するnested pathは署名済み `systemd/caddy.service.d/schubert-nk-startup-policy.conf` の一つ。別名、suffix、他daemonのdrop-inは拒否。既存literal ZIP/CRC/BOM fixtureと全payload hash/解放後条件を照合する。実行は次の同source全6回帰、未実行を合格にしない。
- SCHEMA455：明示025はSCHEMA+25=26、明示027はSCHEMA+27=28。既存PG408の固定旧sourceだけ24を維持。027でその例外を借用しない。026/028/空/省略形式は期待値を変更せず拒否。工具11assert、Production PT分子0。
- MIG456-PROFILE：手書きcanonical BackupProfile、025→027以外及びhost/hash等の変更拒否、入力byte不変更。旧Backup/profile app値を新sourceへ合わせて書き換えない。
- MIG456-SQL：独立literal27 SQLと旧25 byte、SCHEMA行と各version/rank/name/successを照合。checksum expectedは独立 `CRC32("select N;")`、Production/Flywayメソッドでexpectedを生成しない。26件要求・旧SQL改変を拒否。実SQLは旧25署名artifact一致と主Flyway checksumから独立に構成し、DB観測件数をoracleへしない。
- MIG456-CADDY：手書き2 placeholder→literal `10.0.2.15:55160` / 同bind vector、欠落/余分/空/nullを拒否。VM実IPは隔離QEMU interfaceに固定、Production siteの判断ではない。

## 実配備の事前条件・操作・後条件（未実行）

外部工具入口は固定PG456 releaseのsource40hexと署名manifest64hexのみ。現在の隔離instance、全9Unit終端・kernel空・job無、M/A/専用DB advisory所有、未送達request/intent無、現在bootのINVALID及び保全済み同原本pending/full DB graph、旧PG430 signature/BOM/current approvalを再認証する。新candidateは全署名/BOMを認証してhost RO化、027を明示する。既存SAVEがあれば再実行・自動修復せず隔離する。

保全：251行14列を完全比較、V001～025の全23既存table（業務20＋batch_runs＋Inbox/Log progress）の全column/全rowを順序固定JSON長さframe hashで比較。原本全byte/metadata及び全sealed Backup byte/metadataを前後比較。private0700新保存先へ0600 dump/profile/config/旧stop-only policy/metadataを保存しfsync/readback、Git/raw通常logへ出さない。

Flywayはmigration専用role、target027、clean禁止、pending026/027だけ、旧checksum validation後に2migration。後条件は28履歴完全一致、新参照table空・4constraint検証済・index有・Web SELECT/INSERT/DELETEとUPDATE不可・Backup SELECT・App/Batch直接参照不可・Batch cleanup実行可/App不可・既存expires_at NULL契約。これらをPG/PT配備合格と区別して確認する。

Caddyは既存distribution configの固定SHA `66177d46fa761acb07208065db9b0274cb1b12c02ac43b9bfc9857b698b1ccfe` と旧SSC101 stop-only policy SHA `3710be0c023a4bbbf3a8f095cd2d91c5b97b40ed76056ddd4ff433d4f4e066bc`・root metadata・単一entryを確認。他drop-inは拒否。署名templateの固定renderをroot:caddy0640へatomic配置、署名単一startup policyをroot:root0644へ配置し、既存stop-only fileを私有SAVEへrecoverable atomic move（同内容及びmetadata事前保存）する。その承認済TimeoutStop30/SendSIGKILLnoは新policyに包含。daemon-reloadと全終端を確認し、原本/BOM再検査、schema-only profileとapproval/currentを切り替える。未知途中状態は修復・元raw/run復元をしない。原本やBackupの再生成0、permit発行0。

配備後のCaddy validate/cold profile/本人socket/公開CA TLS/login200、同Morning→API保持Web→Caddy→intent→原本DONE→全正常closeは318の実経路で別確認する。BOM/工具assert/DB件数だけでnative合格・coverage100にしない。

## 実行・証跡

host JDK25.0.4、`javac -Xlint:all -Werror`、current6 target/classes＋保存済みruntime dependency＋JaCoCo0.8.15/ASM9.10.1/SpotBugs annotation4.10.4。工具の出力はWorkPG379/pg456-tools-v2へ新規作成、3main testを同classpathで実行。実結果321、全6source/run/coverageは次fresh captureへ追記する。native配備commandは署名candidate固定後に `Pg456SignedMigration <source40hex> <manifest64hex>`、未実行。BUG662/YKT467の正式同source再試験も当全回帰へ統合する。
