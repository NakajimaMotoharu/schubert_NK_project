# 225 NK-OPS-001 固定tmpfs名前空間 PT仕様（PG351）

状態: 限定PT。Production外部Morning/Backup/Cleanup起動、実boot、R2/R3は未認定。

| 項目 | 契約 |
|---|---|
| Program / 対象 | NK-OPS-001、`src/deployment/tmpfiles/schubert-nk-maintenance.conf`、`MaintenanceFileLockTest.fixedProvisioningContract` |
| 関連正本 | OPS-009、UI251、SS341/343（特にSS343§6.15、SSC-089/092/104）、BUG-318、YKT-251 |
| 事前条件 | Java25/Maven3.9.12・systemd-tmpfiles259、Gitの同一候補byte。隔離VMの実`/run`は変更しない |
| fixture | repoの固定tmpfiles候補、VMの新規空 `/tmp/pg351-tmpfiles-root` と `/tmp/pg351-tmpfiles-no-boot-root`。秘密・原本・Unit実体を置かない |

| Test ID | 操作・入力 | Productionと独立した期待値・算出根拠 |
|---|---|---|
| PT-OPS-LOCK-008 | `MaintenanceFileLockTest.fixedProvisioningContract`。設定非コメント行を全列比較し、lock所有試験も実行 | SS343の4dirとSS341の2lockを固定7行で列挙。親`/run/schubert-nk`0755、子`maintenance`/`startup`/`backup-request`/`cleanup-request` root:root0700、M/A lock root:root0600。全行boot限定`!`、上書き/削除rule0。従来の4行だけではFAIL。Production設定をexpected生成に呼ばない |
| PT-OPS-TMP001 | VMの未使用隔離rootへ候補をcopyし、`sudo systemd-tmpfiles --create --boot --root=<隔離root> <候補>`を実行、7pathの種類/mode/owner/inodeをread-only確認。もう1回だけ隔離rootで同commandを実行 | SS343由来の7pathだけが生成され、3追加dirは0700 root:root、M/Aは0600 root:root。再実行前後でinode不変・fileにpayload0。隔離rootは実`/run`ではない。tmpfs条件はVMの実`/run` mount観測と区別する |
| PT-OPS-TMP002 | 別の未使用隔離rootで`--boot`なしの`--create --root`を実行 | `d!`/`f!`は非boot時に1件も生成しない。`/run/schubert-nk`不存在。既存実M/Aを試験用に開放・修復しない |

異常・境界: 欠落3dirを最初のREDで検出。設定の追加/重複/順序・mode/owner/型/`!`誤りはLOCK008の全列比較でFAIL。VM systemdの権限不足でHost非root試行はexit73となり、成功扱いしない。隔離rootでの再実行はboot構文とinode継続を確認するだけで、現役VMに適用可能との承認ではない。symlink/ACL/metadata異常は各Production ownerの既存拒否PTに委ね、既存原本repairを許さない。

実行command、source commit、Coverage、結果、evidence hashは[226 実行結果](226_NK-OPS-001_固定tmpfs名前空間_実行結果.md)と`evidence/provisional/PG351-tmpfiles/manifest.json`を参照。構成fileだけの変更でJava Production coverageに新しいclass/method/branchはない。Batch全suiteと静的解析を影響回帰として行い、正式全scope・4指標100%には代用しない。
