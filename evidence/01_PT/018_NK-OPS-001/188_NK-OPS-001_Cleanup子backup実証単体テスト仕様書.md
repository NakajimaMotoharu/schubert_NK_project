# 188 NK-OPS-001 Cleanup子backup実証単体テスト仕様書

Program ID NK-OPS-001/NK-BAT-001。対象`CleanupBackupAdmission.verify`、既存`BackupManifestReader.findCleanupClaims`/`BackupArtifactVerifier.verify`/`BackupStepRepository.inspect`。RD OPS-009/BAK-001、UI251、SS341/343、SSC104-PG332。Test ID PT-OPS-CBA001以降。Production code実装前の仕様。

fixtureは公開byteだけの`BackupArtifactFixture`と、独立PostgreSQL18/Flyway schemaへ手書きSQLで投入する同run/step/UTCµs/件数/byte数。期待digestは186の固定golden SHA `bd608252091beeda64978c96a85107bd329c56f4222cb0a21c39b868af45c370`、DB後条件はSS341のSQL列値から独立算出し、Production verify/inspectをexpected生成に使わない。credential、実dump/keyは保存しない。

| Test ID | 入力・操作 | 独立期待値 |
|---|---|---|
| CBA001 | 正規同run request・4file・両step SUCCESS、独立SQL観測 | 同一manifest観測を返す。ConnectionはautoCommit=true、rollbackで書込0、borrowed Connection/root開存、全file不変 |
| CBA002 | 4fileの1件を同size別byte、MANIFEST/request digest不一致 | DB SELECT前に固定拒否、書込・DELETE 0、元file削除0 |
| CBA003 | DB両RUNNING、片SUCCESS、別run/handle/count/status/ended異常 | 全て固定拒否。SUCCESSに補完せずDB行不変 |
| CBA004 | rollback・autoCommit復元・query故障/割込、null引数 | cleanup不明は固定非成功、rollback失敗後に復元を試みない。nullは境界契約違反、NPEを正常化しない |
| CBA005 | 同read-only observation再送、並行別session/advisory競合 | 再送はDB更新0で同一結果。advisoryなし/競合は外側`CleanupDatabaseSession`で拒否、単独proofを削除権限へ昇格しない |

各実行の事前条件、追加negative、実行command・環境/commit、coverage4指標、F/E/S/static、BUG/SSC、sanitized evidence path/hashは189へ記録する。Production全体100%未達・実Unit/親M/A/DELETE未達は合格へ算入しない。Coverage除外なし。
