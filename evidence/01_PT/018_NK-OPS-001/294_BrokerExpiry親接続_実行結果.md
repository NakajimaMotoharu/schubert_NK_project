# Broker・Expiry親接続 実行結果

2026-09-30実装前、SSC125/293。新接続・外部live/Expiryは未実行・未認定。修正前BUG369のみread-only再現済み：凍結Source `ffd276e5a86df2d5da077d4f7d1e6f97bdeb73a5`（PG392）と実systemd18property、Type=simple/Restart=on-failure/Remain=noを既存parserがMALFORMED_STATE拒否。終了code0（期待した拒否を独立確認）、start/stop/credential/permit発行0。input `/home/mini/codex/project1/work/pgpt-runs/PG379/pg393-broker-type-repro.input` SHA256 `5137cd6d1f3094bc003744dfd8449a92567f5265168169b4a8c8c9021fb17a0f`、確認log `pg393-broker-type-repro-confirmed.log` hash `d304ee69d85d925f50ebfcfc4195365e241057e54f794597dda81e41a990566b`。初回再現scriptがwrong例外型を待ち終了1となったlogはrepro.logへ保持し、再試験合格に算入しない。全byteはworkに保持・Gitへ生manager出力を転載しない。

旧VM currentPG392/全親子終端・Cleanup active-exited保持・namespace空/INVALID・permit0・旧原本/成功Backup/DB保全。PG393全6はSource7bb8b1b45で進行中、security契約の全回帰を凍結して完了/collector後にSSC125のSourceを修正する。別freshは未完了activeのため不可、正常全起動を捏造doneで解除しない。
