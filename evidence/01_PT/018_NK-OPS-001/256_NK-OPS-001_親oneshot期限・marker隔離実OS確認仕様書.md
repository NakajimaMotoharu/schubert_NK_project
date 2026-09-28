# NK-OPS-001 親oneshot期限・marker隔離 実OS確認仕様（PG373）

対象はBUG-322/SSC-107/YKT-254の親全体30分とhard-timeout後の所有条件。RD OPS-009/BAK-001、UI251、SS341§5–6/342§4/343。既存Production Unit/mainを触らず、隔離Linux PG/PT VMの明示的なtest-only transient Unit（`schubert-nk-pgpt-372-hardtimeout.service`）に`Type=oneshot`、`TimeoutStartSec=2s`、`KillMode=control-group`、`SendSIGKILL=no`を指定し、`flock`内でsleep12を実行する。markerは同名の専用tmpfs directoryへ事前作成する。2秒は30分の時間短縮fixtureでありProduction親受入には算入しない。

| Test ID | 操作・独立期待 |
|---|---|
| PT-OPS-MTIME001 | `Type=oneshot` start途中で2秒を超えたらtest-only Unit Result=timeout・非成功、MainPID0/leaf終端。公式systemd.serviceのoneshot/start deadlineとSS341の境界に基づく |
| PT-OPS-MTIME002 | 事前root0600 markerはUnit hard-timeoutだけでは消えない。状態をmarkerの存在とOS statで確認 |
| PT-OPS-MTIME003 | 親test lockはprocess終端後に別短命`flock -n`から再取得できる。lock解放だけで次回許可しないことを独立に確認 |
| PT-OPS-MTIME004 | test-only Unitをreset/unloadし、専用marker/lock/dirだけを削除。元`schubert-nk-morning-controller.service`はloaded/inactive/PID0で不変更 |

独立oracleは[systemd.service(5)](https://man7.org/linux/man-pages/man5/systemd.service.5.html)のoneshotと`TimeoutStartSec`、SS341/342/SSC107のmarker/次回拒否条件。`systemd-run --wait`の終了code、fresh `systemctl show`、root専用directory実file、別process `flock -n`を別々に採る。秘密・Invocation ID・raw Unit journalは保存しない。OS/systemd/JDK/branch/source commit、コマンド、終了code、期待/実際、片付けと未実測条件を257/manifestへ保存する。VM試験用Unit成功をProduction Unitや実parent受入へ読み替えない。
