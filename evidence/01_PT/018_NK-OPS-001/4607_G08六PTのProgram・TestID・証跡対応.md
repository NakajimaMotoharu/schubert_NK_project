# G08 六PTのProgram・Test ID・証跡対応

六つの固定source/runについて、仕様、Test ID、JUnit XML、成果物のSHA256を照合した。既69実行と固有51 Test IDに対応する。Cleanupの旧事前試験と新再試験を別sourceとして両方保持した。170宣言hash一致、うちgzip解凍18。製品再実行とexec結合は0。

| Program | Run ID | 選択内の成功 | 固定試験source | 原仕様 | 証跡 |
|---|---|---:|---|---|---|
| NK-MIG-001 | PG38668-BUG3234-SCHEMA-OWNER-CLOSE | 11 | 380a0369e42a | [004_NK-MIG-001_SQL重大例外・原九新一通常十仕様.md](../019_NK-MIG-001/004_NK-MIG-001_SQL重大例外・原九新一通常十仕様.md) | [PG38669-bug3235-schema-owner-post-v3](evidence/PG38669-bug3235-schema-owner-post-v3/manifest.json) |
| NK-DAT-001 | PG38684-SSC461-RUN-REFERENCE-JDBC | 8 | bdea127fb2ef | [447_WBS66参照DAO純JDBC単体仕様.md](../004_NK-DAT-001/447_WBS66参照DAO純JDBC単体仕様.md) | [PG38686-ssc461-run-reference-post-v1](evidence/PG38686-ssc461-run-reference-post-v1/manifest.json) |
| NK-BAT-001 | PG38706-SSC461-CLEANUP-DOUBLET | 18 | 617af24e6410 | [703_Cleanupステップ_単体テスト仕様書.md](../017_NK-BAT-001/703_Cleanupステップ_単体テスト仕様書.md) | [PG38708-ssc461-cleanup-jdbc-post-v1](evidence/PG38708-ssc461-cleanup-jdbc-post-v1/manifest.json) |
| NK-BAT-001 | PG38729-BUG3237-CLEANUP-CLOSE | 18 | 56ae8c9dc3b8 | [703_Cleanupステップ_単体テスト仕様書.md](../017_NK-BAT-001/703_Cleanupステップ_単体テスト仕様書.md) | [PG38732-bug3237-cleanup-owner-post-v2](evidence/PG38732-bug3237-cleanup-owner-post-v2/manifest.json) |
| NK-BAT-001 | PG38753-SSC461-BACKUP-PAIR-JDBC | 10 | 9304ce334ad4 | [699_Backup監査ペア_単体テスト仕様書.md](../017_NK-BAT-001/699_Backup監査ペア_単体テスト仕様書.md) | [PG38755-ssc461-backup-pair-post-v2](evidence/PG38755-ssc461-backup-pair-post-v2/manifest.json) |
| NK-MSG-002 | PG38784-SSC462-ENCRYPTED-RESPONSE | 4 | 568b4e28e1f2 | [001_NK-MSG-002_単体テスト仕様書.md](../006_NK-MSG-002/001_NK-MSG-002_単体テスト仕様書.md) | [PG38786-ssc462-encrypted-response-post-v1](evidence/PG38786-ssc462-encrypted-response-post-v1/manifest.json) |

全Test ID・独立仕様hash・元保存名と実保全パスは[対応JSON](evidence/PG38798-g08-six-current-pt-evidence-v1/run-program-test-map.json)に記録した。初回照合では既OUTCOMEの仕様に列挙ではなく範囲が使われていた。定義済み範囲で照合し、試験を再実行していない。全G08・451・PGPTの正式受入は継続。独立manifest SHA256 7a98d4a8b517cb35d3c957fb18d88318af39c9fe6d5d813bd4e140670dcb18b4。
