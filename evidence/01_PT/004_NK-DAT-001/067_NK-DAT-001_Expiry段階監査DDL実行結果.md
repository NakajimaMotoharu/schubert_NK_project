# NK-DAT-001 Expiry段階監査DDL 実行結果

PG246/SSC-078/BUG-238/YKT-189、PT-DB-018。2026-09-24現在、V022/独立PTの選択試験は成功、対象source commit、正式run、全reactor/coverage/49scope/hashは未確定のため**合格へ算入しない**。正式run40/source`c1512bf6`はV021最終監査のみの限定認定であり、本段階監査を含まない。

再現・期待値は対の066仕様書。選択`/tmp/PG246-selected.log`は2026-09-24 14:22:40 JST、API34/34（DatabaseMigration18、StepCleanup8、InspectionParent8）、exit0、failure/error/skipped0。選択`/tmp/PG246-batch-selected.log`は14:23:13 JST、Batch24/24、exit0、failure/error/skipped0。019負canary99/99。隔離PG18のV021旧23514、V022 partial commit/re-read、旧SUCCESS不変、FAILED after NULL、同日attempt2最終成功を独立literalで確認。いずれも未commit探索なので正式認定へ算入しない。正式の日時/OS/JDK/PostgreSQL/Flyway/pgJDBC、branch/commit、command/exit、PT-DB-018の入力・期待・実際、負条件、coverage/static、manifest path/hash、関連BUG/SSCを後続で記録する。親のpurge前DB確定・失敗/同run再実行/不確定commitは別の必須受入であり、V022成功だけでExpiry清掃全体を完了にしない。
