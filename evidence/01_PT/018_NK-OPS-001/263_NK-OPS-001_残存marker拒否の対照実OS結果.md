# NK-OPS-001 残存marker拒否の対照実OS PT結果（PG376）

仕様[262](262_NK-OPS-001_残存marker拒否の対照実OS仕様書.md)。2026-09-29 JST、branch `dev-foundation`、Production source `38c15df46`（Production class byteはPG372と同一）、VM Linux7.0.0-31-generic x86_64/systemd259/JDK25.0.4。PGPT-only probe `clear`を追加し、host javac25.0.4 `--release 25 -Xlint:all -Werror` exit0、転送JAR hash一致。対象はPT-OPS-MTIME009の1件だけ。

空の専用root0700で`clear`は`CLEAR_ACCEPTED`/exit0、entry0件。Production marker classの`begin`をtest-only oneshotで起動し、TimeoutStartSec=2s後にclient exit1/Result=timeout/約2.162秒/ExecMainStatus143/MainPID0/ControlGroup空。中間の空root0600/regular/link1/size0 marker inode8989を確認し、別process`check`は`RESIDUAL_REFUSED`/exit0、再stat inode8989不変。検証済みtest-only markerだけをunlink後、同rootの`clear`は再び`CLEAR_ACCEPTED`/exit0。したがって残存時の拒否はnamespace環境の恒常失敗ではなく、marker有無による差である。PT-OPS-MTIME009限定PASS。

専用Unitをreset-failed/not-found、専用marker/root/VM stage3JAR/空directoryだけ撤去。元`schubert-nk-morning-controller.service` loaded/inactive/PID0、Production backup-request空。元Unit/原本/credentialは不変更。test-only削除物は再build可能で、Production資産は削除していない。実親M/A/原本/子Unit・30分、実外部Web/API、CHRは未受入。Production source不変更につきProduction6再run/coverage再認定なし。PG372 2,509PT/369suiteは別結果、正式`PT-WEB-20260925-24`は不変。PG374 `MTIME008`のinvalid instance/mode/非root試験は依然未実行で合格へ算入しない。BUG322/SSC107/YKT254は対応中。

command/input/期待・実際/exit/OS tool/hash/未実行/関連IDはmanifestへ保存。systemd-runが返した生Invocation ID、raw journal、秘密情報はGit証跡へ保存しない。
