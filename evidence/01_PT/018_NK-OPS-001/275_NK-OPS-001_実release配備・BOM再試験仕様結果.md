# 実release配備・BOM再試験（PG382/383、未受入）

関連NK-OPS-001/DAT009/OPS009/UI212/251/253/SS343 SSC096/110/112、272/274。

FULLBOM009: 新exact2path `config/effective/backup-profile.json` / `backup-age-recipient` の独立public byteをFixtureへ配置し、JCA SHA256で期待hashを計算。署名/BOMのbyte hash/全集合・metadata不変。未知private-key/unapproved/alias3pathと改変byteを拒否。合成owner/RO fixtureでありnative承認ではない。Bootstrap clean9PT F/E/S0/static0、2026-09-30 10:26:03 JST/17.550sec、pg383-bom-layout.log。固定source全6と真正VM同再試験を別に行う。

PG382固定source `ba50a5452f44e289ee0844c0ebeaedc8da81e808` は全6 clean2537PT/371suite F/E/S0/static各0/class mismatch0、10:16:04 JST/13:02min/exit0。manifest `evidence/provisional/PG382-backup-expiry-wiring/manifest.json` SHA `4e505169fa10a69882b6ff06ea415a7906660816aa61fdae39e7f268a25c4fe4`。未網羅B/L/M/C=265/1091/248/23（Bootstrap37/13/5/0、API3/32/4/0、Web1/25/4/0、Batch224/1021/235/23）。正式100%/53scope/実NKは未認定。

真正Maven thin-JARを組立：177artifact/61dependency/23migration、原manifest39079byte/hash `a0ad8008a93c350d9ff88443b28b7464663ae0c338fe76a207cedef6048f226c`。CLI ANSI混入BUG339は無装飾batch-mode/style.color=neverのlist再生成（10:18:01/1.155sec）で解消、assemblerのstrict座標/全JAR集合/共有target hash一致を維持。先行partialはGit外privateの`pg381-release-partial-ansi`へ保全。Source Unit/Target収録BUG337は実組立成功で確認、VM全BOMは別。

独立OpenSSL3.5.5 Ed25519署名/検証成功。鍵custodyはclient private0700内secret600、server/Gitへ秘密鍵を転送しない。固定public DER44byte/SHA `3378dbf29039d9fd0194f8c949a8793f00aff460bfeb6c69aba492498f4de221` はcandidate外root0700/400へ配置。detached64byteもruntime tree外root0400。VMのProduction verifierは同M/A・全8停止後にfixed pin原byte署名を実検証成功、続く全BOMはBUG340のapproved2path反映漏れで拒否。未承認candidateを保持、approval/current/DB変更0、permit0。これはnative Morning/Backup成功ではない。

VM生存QEMU11690、genuine Source Unit8をloaded/inactive/PID0へ配置。原Unit一式とMorning旧8drop-in・Backup旧pgpt309.confをroot専用領域へ保全。BUG338途中配置をresetせず後半だけ続行。Morning/Backupの追加profileはJaCoCo0.8.15/同source classbyte採取と明示保存run resumeだけ、Root gateや任意classpathへ置換しない。Coverage用Backup追加RWは専用非秘密leafのみでIT/運用profileへ流用しない。

V023前DB dumpはGit外VM private/root600（412095byte）、pg_restore目録読取成功。業務/session/電文/log行0、gamesの2行は既定V004 seedで全literal・created_at一致をmigration直前に再検証。既存durable run/activation/cutoffを削除・resetしない。専用schubert_migration+Flyway13.4でvalidate→pending023だけ→migrate→validate、repair/clean/manual履歴挿入禁止。実適用はまだNOT-RUN。実Morning→Backup両step/DB再読/marker/request/全Unit終端/失敗・timeout・resumeもNOT-RUN。

再現tool草稿/実logはGit外 `/home/mini/codex/project1/work/pgpt-runs/PG379/` に保持：Pg381TrustedDeployment.java（VMにjavacなしのためclient25でcompile、server25で実行）、pg381_install_inputs.py（途中停止原版保持）、pg381_complete_inputs.py、pg381_place_release.py。sourceは後続のsanitized tool/evidenceへ収録し、秘密・dump・private keyを含めない。command/source/tool/hash/exit/実値を後続native manifestで確定する。
