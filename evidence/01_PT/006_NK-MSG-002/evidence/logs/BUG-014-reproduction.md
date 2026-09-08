# BUG-014 修正前照合

- 発見: 2026-09-07、branch dev-messaging、既存実装HEAD 1f09031（ログ取込みPG/PT未commit変更は別範囲）。変更前V005とPT-DB-011をSS324 §12/332 §11.4へ照合した。
- 既存 `maintenance_cleanup_message_stores` はInboxを `expires_at < p_cutoff`、API/Web Outboxを `sent_at < p_cutoff` で削除する。Outbox保持7日の減算・lease保護条件はない。
- 既存 `DatabaseMigrationTest.verifyMessageCleanup` のrun cutoffは2026-09-02T00:00:00Z、SENT日時は2026-08-31T00:00:00Z。2日前に送信されたAPI/Web各1件の削除を、Inbox1件と合計3件の期待値としている。SSの独立期待値ではこのOutbox2件は保持対象である。
- Inbox predicateはPROCESSING以外とexpiresだけで、SSが削除禁止とするdecrypt/整合error・result reference不整合を識別しない。
- DB dump・row本文・credentialは取得していない。ここに記した日時/件数は既存合成fixtureの定数である。
- 既存DDL/PTの変更前にBUG-014/YKT-012を起票した。正本の保持仕様やCurrent baselineは変更しない。追加migration/境界PTと後続Batchの保護検証を完了するまで本件およびPGPTを完了扱いしない。
- 実PG再現（2026-09-07 08:02:21 JST終了、base865b2b7＋新規回帰test、Maven exit1）: `MessageStoreCleanupTest.sentRowsYoungerThanSevenDaysMustRemain` は独立期待`0|0|0|OK`に対して実際`2|2|0|OK`。run=2026-09-07、送信=09-05のAPI/Web各1件が削除された。合格算入外。
