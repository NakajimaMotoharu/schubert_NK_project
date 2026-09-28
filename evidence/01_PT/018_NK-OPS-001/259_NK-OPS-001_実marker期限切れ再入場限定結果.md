# NK-OPS-001 実marker期限切れ再入場限定PT結果（PG374）

仕様[258](258_NK-OPS-001_実marker期限切れ再入場限定仕様書.md)。2026-09-29 JST、branch `dev-foundation`、Production source `32bf8ce9fd40545f74aeb2785fdbd03637e9f89f`（PG372 sourceと同一、PG373は文書のみ）。VM instance-id固定`pgpt-r2-20260927-01`、kernel7.0.0-31-generic x86_64、systemd259、JDK25.0.4。対象はPGPT-only probe＋同sourceからbuild済みProduction Batch/Storage bytecode。Production JARへprobeを追加していない。

| Test ID | 期待 | 実測/判定 |
|---|---|---|
| PT-OPS-MTIME005 | Production classがtest-only root0700にmarkerを公開しoneshot2秒期限で停止、marker空/root0600/regular/link1残存 | `systemd-run --wait` client exit1、Result=timeout、約2.264秒、ExecMainCode1/Status143、MainPID0、ControlGroup空。marker root0600/regular/link1/size0/inode8772で残存。PASS（test-only） |
| PT-OPS-MTIME006 | 別process再入場は残存markerを拒否、inode不変 | `check`が`RESIDUAL_REFUSED`/exit0、再statでもinode8772・属性/size不変。PASS（test-only） |
| PT-OPS-MTIME007 | test-only状態/path撤去、元Morning不変更 | 専用Unit reset-failed後not-found/PID0、専用marker/rootとVM stage3 jarを個別削除・directory rmdir、元`schubert-nk-morning-controller.service` loaded/inactive/PID0、Production `/run/schubert-nk/backup-request`空。PASS |
| PT-OPS-MTIME008 | invalid instance/mode/非root拒否 | 今回は未実行。合格数へ算入しない |

Host初回`javac --release 25 -Xlint:all -Werror`はSpotBugs annotation JARをclasspathから欠きexit1。対象JARを加えた再compile exit0。これはProduction障害ではなくtool classpath不備であり、失敗を成功に数えない。Batch jar SHA-256 `2c94c0383fe2bb288bb6a2e6a44f00073f20efd39ec5295ab5f2726dba7f6816`、Storage jar `52f5aa6061881ae8bd7205e936d5803a2006a23463e5c5eca8b700007b86a2b7`、probe class `d4965bd1bd2373e6b26e2424c9eaf7a63123bb2cacc4f45aaf31ed04b84701d2`、probe jar `4b435edf4e3d4c7caaebed5f263bfa83a33c55f955202863748a1ae1953067a2`。転送後VM hash一致。Sanitized command/入力/期待・実際/exit/hash/関連BUGはmanifestへ保存し、生journal/Invocation ID/秘密はGitへ入れない。

PG374は追加Production sourceなし、Production6再run/coverage再認定なし。直近PG372 fixed source2,509PT/369suite F/E/S0/static0は別run。今回のtest-only markerは真正Morning M/A・current原本・Backup Unit/worker、実30分、Production次回入場を通していない。既存`MorningControlScope.withClearIntent`にはM下・原本前の残存marker拒否PT（MCTRL014）があるが、外部`MorningProcessMain`はまだそのscopeへ接続されていない。BUG322/SSC107/YKT254は対応中、R2/R3/実NK CHR/全coverage100%には算入しない。
