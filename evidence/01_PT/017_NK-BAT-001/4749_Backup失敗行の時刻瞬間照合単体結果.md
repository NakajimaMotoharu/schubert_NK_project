# Backup失敗行の時刻瞬間照合の単体結果

2026-11-24 JST、PG43914。製品Core 23a7874f01b432a01256ee0e58823f8038fca59a、確定試験 a15240fbf7f6810b914ed07f3b075cf1ab7909d0。元UTC001の拒否を確認後、現新規3・既4すべて終了0、fail/error/skip 0。比較helperのL2/M1/B4は全到達、クラス全体はL60/65・M4/10・C1/1・B38/68。修正前と中間の実測は別保存。製品一源のPMD、対象三源の書式とCheckstyleは終了0。二fixtureのJDK interface loader生診断1件ずつを保存。正規Batch包装、現SpotBugs、実DB、451は残る。 [仕様](4748_Backup失敗行の時刻瞬間照合単体仕様.md) [証拠](evidence/PG43914-backup-jdbc-time-instant-correctness/manifest.json)
