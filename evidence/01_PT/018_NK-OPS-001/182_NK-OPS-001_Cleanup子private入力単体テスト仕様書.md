# 182 NK-OPS-001 Cleanup子private入力単体テスト仕様書

Program ID: NK-OPS-001/NK-BAT-001。対象は `RootBatchCredentialReader.readCleanupRequest`/`readBytes`/`inspect`、既存`read`および `CleanupWorkerRequest.consume`。RD OPS-009/BAK-001、UI251、SS343 §6/SSC104-PG329・SS341/342。Test IDは PT-OPS-RBCR009～012、既存RBCR001～008とCREQ001～007を回帰対象とする。

前提: `BackupPublicationFixture`の実保持file/`OwnedTransferDirectory`を使い、root:root0500/0400・ACL0・tmpfs/read-onlyは明示合成metadataとして注入する。真正systemd private mount/Root子Unit/固定`CREDENTIALS_DIRECTORY`照合は本試験の範囲外。`cleanup-request`はSSの独立ASCII literal `NKCLEAN1`/run/activation/cutoff/manifest SHAを用い、Production `encode`を期待値作成に使用しない。試験専用`db-batch`は公開fixtureで実credentialを含まない。

| Test ID | 入力・操作 | 独立期待値 |
|---|---|---|
| RBCR009 | 1～256byteの固定private copy、別固定`db-batch`、欠落file | canonical相関4値がliteral一致し、DB password ownerは別に読取可。欠落ではfallbackせず固定IOException |
| RBCR010 | 空、257byte、version違い、末尾追加、digest大文字、別名`db-api` | 全て固定IOException、源file/別名探索なし。長さ/形式はSS343・`NKCLEAN1` golden byte契約から算出 |
| RBCR011 | short/zero/position IO、非root UID、ACL混入 | 相関を返さず固定IOException、全保持owner close。read/前後metadata契約はSS343 |
| RBCR012 | 不正copy→同名修復（test fixtureだけ）→同一読取器で2回正常再読 | 不正を成功へ繰上げず、次の正常copyを毎回fresh読取。親本番sourceの上書き許可は含まない |

正常・境界・異常・例外・null・再送・並行はRBCR001～012/CREQ001～007で組み合わせる。`readCleanupRequest`を子自身のroot Unit snapshot/固定source locationへ実結線する後続PTが必要。実行command、Linux/JDK25.0.4/Maven3.9.12、対象commit、四指標、F/E/S/静的結果、関連BUG/SSC、sanitized証跡path/hashは183へ記録。Coverage除外なし、定義branch0は条件網羅と混同しない。
