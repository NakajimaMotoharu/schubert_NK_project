# 213 NK-OPS-001 Morning明示同run再開・単体テスト仕様書

Program ID: NK-OPS-001。対象: `MorningResumeAdmission.execute/create`、`MorningControlScope.executeResume`、`MorningDatabaseSession.Session.requireConsistent`。関連RD OPS-009、UI251、SS331 §3.12、SS341 §11、SS343 §6.13/6.15、SSC-055/094/105、BUG-317/YKT-250、PG345。Production外部mainへの接続、実VM保留原本の再公開、固定8 Unit/backup/Cleanup/permitの実実行は本限定仕様の対象外であり、成功を代用しない。

| Test ID | 事前条件・fixture・入力・操作 | 独立期待値・算出根拠 |
|---|---|---|
| PT-OPS-MRESUME001 | 固定run/activation/cutoff UUID・時刻、手書きevent、fake M内のDB/File owner、明示runを再開 | DB owner取得後にfile resumeが行われ、DB/File保持中に参照確認・continuation、closeはFile→DB。SS343 §6.15の全区間排他をevent literalで検証 |
| PT-OPS-MRESUME002 | 原本resumeがIOException | DB取得後の原本障害で後続0、File/DBが閉じる。原本を修復しない |
| PT-OPS-MRESUME003 | 既存DB参照identity不整合 | DB/File保持で照会失敗、固定8停止・後続0、ownerを閉じる。SS331 §3.12 |
| PT-OPS-MRESUME004 | 原本が別runを返す | 参照照会0、後続0、固定非成功。requested UUIDを別runへ取り替えない |
| PT-OPS-MRESUME005 | 完了済activation原本 | 完了情報をそのまま後続へ渡し、旧成功を今回の成功へ推定しない。SS343 §6.13 |
| PT-OPS-MRESUME006 | null run/continuation、重複activation UUID | 副作用前の契約拒否又はDB/File未開始、偽の識別子を発行しない |
| PT-OPS-MRESUME007 | 並行continuationをlatchで停止 | 停止中にDB/File ownerが同時保持され、所有を早期解放しない |
| PT-OPS-MRESUME008 | root再検査・後続失敗/異常値 | 失敗/unknownを成功に転換せず、後続二重実行0、所有を閉じる |
| PT-OPS-MRESUME009 | DB接続失敗をFile ownerより前に注入 | 原本のopen/resume/公開0。修正前BUG-317の再発防止反例 |
| PT-OPS-MDB013 | fake JDBCの既存参照true/false、null、Session脱出 | 同run整合trueのみ通過、false/null/失効Sessionを拒否。`RunReferenceRepository`の戻値を独立に設定 |
| PT-OPS-MDB014 | 実PostgreSQL V018、固定runで当日batch履歴生成、同run同cutoff・+1秒・翌JST日照会 | 原cutoffと同JST業務日は整合true、翌業務日はfalse。SS331 §3.12のbusiness_date oracleを手計算。秒単位の原本cutoff一致はfile graphの別契約とし、DBへ過大な期待を置かない |

既存`MorningControlScopeTest`11件も順序・失敗閉鎖の関連回帰とする。正常/境界/異常/例外/null/並行/同run再開を上記で扱う。固定UUID/手書きevent/実DBの独立JST日付で期待値を作り、production methodをexpected生成に呼ばない。NPEはpublic contractのnull拒否としてだけ期待し、catchして正常扱いしない。coverage除外なし。実行command、環境、source commit、4指標、結果、証跡path/hashは214とmanifestへ記録する。限定試験で実root/M/DB/Fileを同時に走らせたとは主張しない。
