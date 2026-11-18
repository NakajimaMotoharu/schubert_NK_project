# SSC-461 SchemaHistory JDBC境界の実行結果

Core d15952579fea3067180a9fc65523045002e50482、Unit c10f41fb75273a5cc704ad34f5051e4c355e3ef4。変更1箇所、元whole10は同一byte。PG38634は真正0、10成功・F/E/skip/選定内未実行0。PG38636で7物理CRC、実行5、元XMLを確認。PG38640独立生測定ではSchemaHistoryAdmission.inspectの4B/2IとRowのtoString/hashCode/successの3M/9Iが未到達。初回独立判定の不成立は記録し、生測定とJUnitは再起動なし。BUG3234を修正前起票。

PG38626/28のstrict、NullAway、CS/format/SpotBugsを確認。PMD生29は元2265全位置に同命令・source位置差1・同独立根拠で対応。元SQL identity／closeは現オラクルでPT、移管6/104。全ArchUnit、実DB、F02・全451は未完。証跡 evidence/01_PT/018_NK-OPS-001/evidence/PG38640-f02-schema-history-jdbc-owner-independent-v1/manifest.json SHA256 ec173e2018f0dadf7883fa6ea988a34b6206935a0d4cd4e75dac9394fb70b3a7。
