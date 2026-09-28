# 226 NK-OPS-001 固定tmpfs名前空間 PT結果（PG351）

状態: 限定PT完了。BUG-318/YKT-251の設定修正は確認済みだが、実boot/Production Unit起動は未認定。

2026-09-28 JST、branch `dev-foundation`、source/test/config commit `71e209d86ec4fb0ba8f30947938b640f54e727e2`。正本・Test ID・環境・期待値は[225](225_NK-OPS-001_固定tmpfs名前空間_単体テスト仕様書.md)。候補byte SHA-256 `27ccf8ae530a1ca83c2a8b2e7aa391d739757b2768c2ac76312d7ef834776e95`、VM staged byteも同値。

- 修正前 RED: LOCK008で1PT/F1、従来4行に対し独立SS期待7行。最初の`-am`指定は依存moduleでテスト0/exit1（試験自体未実行）なのでREDに算入しない。
- 修正後選択: `MaintenanceFileLockTest`8PT F/E/S0、Batch SpotBugs0、exit0。Java本体は不変更、選択coverageは全Batch4指標の合格値にしない。
- Batch影響回帰trigger: boot設定7行はBatch root admission全経路に共通なので同module全suiteを実行。`./mvnw -o -q -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository -Dnk.pt.repository=/home/mini/codex/project1/work/pgpt-foundation -pl src/schubert-nk-batch test spotbugs:check jacoco:report`、Java25.0.4/Maven3.9.12、exit0、713PT/86suite F/E/S0/SpotBugs0。Batch全体JaCoCo missed branch15/line235/method92/class12（instruction1108）なので100%不可。JaCoCo XML SHA-256 `69a776a6b8317a686569a190777ddadf979b0d988db443ae1fed83fe30f6c895`。Java Production sourceは変更0。
- VM隔離root: TMP001の`--boot`実行2回ともexit0、7path root:root、親0755/子4dir0700/2lock0600。2回目も7path inode同一・lock size0/nlink1。3追加dirのACLは基本3項のみ。TMP002は`--boot`なしexit0でroot下`/run/schubert-nk`不存在。VM systemd259、実`/run`はtmpfs、実backup-requestは先行PG350の空root0700をread-only確認。Morning/Backup Unit inactive/PID0。現役`/run`へのtmpfiles再実行0回。
- Host非rootの隔離root探索はfchown 7件拒否/exit73。権限不足をPASSに数えず、VM root隔離結果で評価した。

独立native観測のsanitized原本は`evidence/provisional/PG351-tmpfiles/output/native-summary.md` SHA-256 `9fdc2e7cededb9803f609952d4a6bbec5459a07df493ff7121e31c7cf3be56f4`、同manifest SHA-256 `38d939cb770e68eb16c6fa73e64454eb7f399ae53bb74174b98c7552f2b4d846`。manifest内の2file hashを再照合済み。Gitへ秘密、raw session、credential、runtime request payloadは保存しない。正式全6/53scope・実起動/CHR/coverage100%を主張しない。
