# BUG-007 修正前再現

- 発見日: 2026-09-04
- 基準: commit `a4cd40c`に修正前起票後、PT-IDEM-007/008のDB境界testを追加した作業tree
- 期待: `request_inbox.response_body_encrypted`が1,050,001 byteならSQLSTATE `23514`
- 実際: INSERTが成功し、JUnitは`Expected SQLException, nothing thrown`でFAIL
- 実行結果: `DatabaseMigrationTest` 15件、failure 1、error 0、skipped 0
- 原因: V003のCHECKがAES-GCM最小overhead（28 byte超）だけを検査し、SS 324 §6の1,050,000 byte上限を欠いていた
- 修正: commit `dcc90fe`でDB CHECKとJava guardを追加
- 再試験: Run `PT-IDEM-20260904-01`で29/28/1,050,000/1,050,001 byte境界をPASS

Raw ciphertext、key、DB dumpは保存していない。
