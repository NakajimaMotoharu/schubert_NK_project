# Admission/Handoff残19・現在理由再認証仕様

群ADMISSION_HANDOFF_CURRENT19_REASON_REAUTH_V1/event2592、WBS-F03、原.5/1.5/4pp cap10。source7f035ccfe89c46e8f4fae52099b1c0e4e890e66b/Main21d不変、正式1964-53/17-190/工数null/原残予測を保持。

四Main全417行：SchemaHistoryAdmission六/ServiceDatabaseAdmission六/InspectorLockHandoff五/MaintenanceMutationGuard二。PG11590の固定19IDに限定し、他の空理由・未参照指摘を暗黙に分類しない。旧PG6048非空12・PG6354非空七だけを全source SHA/座標/priority/message SHA/元rowへ一致させる。必要JdbcAdmissionFailures・origin/main SS332/341§7.3/343SSC095119を照合する。1253/1362/1499/1928の後続成果を確認し、既機能を作り直さない。

期待契約：Admissionのowned rows→statement direct close・SQL/unknown順位・新固定SQL secondary、borrowed Connection非所有。Handoffは同期callback未知identityとknown再取得失敗secondaryを分け、必須再取得失敗で成功値を返さない。scalar/timeoutの資源は取得宣言直後TWR、timeoutは同親残期限とtransaction-local返値を前後guard。これらの構造は実advisory/親子/Unit所有や終端の証拠ではない。四source/helperは旧8c/aedと同byte、当scopeはPG変更不要。新たな製品期待値を同じproduction methodで生成せず、既承認契約と現sourceを比較する。

`python3 -B tools/quality/pg11123_checked_python_entry.py tools/quality/pg11590_admission_handoff_source_reauth.py`、PG11592 metadata負例、PG11594 index、PG11595独立原履歴再計算。全て既公開JSON/Java text/承認文書読取と新metadata保存だけ。型実行/target load/Sessionやcallback構築/DB/VM/Root/鍵/credential実体/私有raw・保留工具・Graph9/deferred8へアクセスせず、新PT/harnessを起動しない。

理由空欄・誤source/旧runtime/coverage100補完/件数脱落をmetadata負例で拒否し、製品PTとして計数しない。全19raw/currentWhole pendingを維持、新コード/製品PT/coverage/正式受入0。全F03/451の不足と全安全HOLD/原本等を保持する。環境/command/終了はinvocation、path/hash/実測集計は2232。
