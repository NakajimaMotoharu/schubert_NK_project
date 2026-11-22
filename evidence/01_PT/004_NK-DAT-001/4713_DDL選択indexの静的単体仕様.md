# NK-DAT-001 選択indexの静的単体仕様

WBS-P004-01.02/2、PT-DB-005-STATIC-INDEX。承認正本SS331 §§4, 6–9、UI241／242、DAT-002／006／009、V004／005／017／026。対象はV001～030の製品SQL。SQL実行とDBへの接続は不要。

| 対象 | 独立期待値 |
|---|---|
| Session、質問、通知 | SS331のキー順・降順・部分条件。現行ユーザーのsessionは未失効だけ。質問所有者／管理者の検索は未削除だけ、削除側の別indexは削除済みだけ。 |
| Outboxと検索 | 送出の `status, next_attempt_at, id`、PENDINGのlease部分index。質問本文とログmessageは `gin_trgm_ops`、質問は削除済みを含めない。 |
| 受付参照とBatch | 受付技術表は `question_id`。Batch SUCCESSの日・step一意制約は更新履歴を保持し、現定義では両Backup stepを例外とする。 |
| 異常5通り | 質問の方向逆転、lease条件喪失、GIN演算子class喪失、Backup例外一件欠落、受付参照列誤りはすべて拒否する。 |

`python3 -B evidence/01_PT/004_NK-DAT-001/input/42376_selected_index_contract.py src/schubert-nk-api/src/main/resources/db/migration`。指定11 indexの静的条件だけを判定する。PostgreSQLでの適用、権限、constraint実行、query plan実測、正式P004の終了判定は別証拠を要する。
