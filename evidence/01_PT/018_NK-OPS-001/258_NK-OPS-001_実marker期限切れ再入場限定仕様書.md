# NK-OPS-001 実marker期限切れ再入場限定PT仕様（PG374）

対象はProduction `BackupStartIntentFiles.requireClear/begin` とPGPT専用 `NativeBackupTimeoutResidualProbe`。RD OPS-009/BAK-001、UI251、SS341§5–6/343§6.15、SSC107、BUG322/YKT254。Production親全体・M/A・Backup Unit/原本は対象外。source基準は実行時manifestに固定する。

| Test ID | 事前条件・操作 | 独立期待値（SS/OS契約由来） |
|---|---|---|
| PT-OPS-MTIME005 | VM instance-id、実効root、専用`/run/schubert-nk/pgpt-374-backup-intent` root0700/tmpfsで空、元Morning Unit inactive/PID0を検査。Production同byte classを別classpathのprobeから`hold`し、test-only oneshot `TimeoutStartSec=2s`で終了させる | 固定`backup-start.intent`空/root0600/regular/link1が公開され、Unitはtimeout・main PID0/ControlGroup空となる。client exit0は期待しない |
| PT-OPS-MTIME006 | timeout後の同専用rootを新processの`check`で開き`requireClear`を呼ぶ | `RESIDUAL_REFUSED`固定状態、exit0（拒否の成功）。marker inode/属性不変、次の仕事は0件 |
| PT-OPS-MTIME007 | test Unitのreset-failedと専用marker/空directoryのみを検査後に撤去し、元Morning Unit再照会 | test-only state/path不存在。Production backup-request/Morning Unit/原本/credential不変更 |
| PT-OPS-MTIME008 | invalid instance/mode/非root等の固定probe前提検査 | Production操作前に失敗閉鎖し、既存pathへ触れない（既存PG356とhost静的確認に限定。今回未実行なら未実行と明記） |

Commandと環境、対象commit、hash、各exit/result、入力、期待/実際、coverage、関連BUG/SSC、redacted outputを259とmanifestへ一意に保存する。生journal、Invocation ID、credential、session/tokenはGitへ入れない。ProbeはProduction JARへ含めない。今回のtimeout/再入場は専用test directoryであり、真正Morning同一M/A・current原本・子Unit/実30分・外部Web/API・CHR受入には算入しない。fixture失敗時に手動修復せず状態を記録してから対象の安全性を確認する。
