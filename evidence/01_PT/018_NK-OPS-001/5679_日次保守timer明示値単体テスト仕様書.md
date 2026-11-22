# NK-OPS-001 日次保守timerの時刻精度・遅延

PT-OPS-MAINT-PREBOOT001-T03。SS342 §4.4、SS341 §2、UI251 §2、AVL-001／OPS-003、BUG-3579／YKT-2814。対象は `src/deployment/systemd/schubert-nk-maintenance.timer.template` の `[Timer]` と明示した接続先。

| 観点 | 入力と操作 | 独立期待値 |
|---|---|---|
| 明示設定 | 現候補のtimerをstrictな重複検査付きで読む | SS342 §4.4の時刻に加えて `AccuracySec=1min` と `RandomizedDelaySec=0` が一つずつある。従来の接続先、導入先、追い付き再実行禁止を維持する。 |
| 異常 | 片側ずつ欠落、異なる値、同値で重複させた合成入力を読む | 6通りをすべて拒否する。 |
| ツール読取 | `systemd-analyze timespan 1min 0` の単位変換を比較する | 60,000,000µs、0µs。 |

ローカル環境で `python3 -B evidence/01_PT/018_NK-OPS-001/input/42370_daily_timer_settings.py src/deployment/systemd/schubert-nk-maintenance.timer.template /usr/bin/systemd-analyze` を実行する。受入対象は設定の静的契約のみ。元の時刻境界T01/T02は別候補だったため元証拠を保持する。service本体、運用排他、60分監視、実機のUnit起動・停止は親仕様5677の確認を要する。
