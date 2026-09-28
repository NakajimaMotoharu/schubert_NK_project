# 231 NK-OPS-001 Backup起動intent PT仕様（PG355）

状態: SSC-106の同boot fail-closed fileと親M admissionを対象とする限定仕様。真正Morning Unit、固定Backup Unitの実start、hard timeout・親死亡後の運用復旧、backup完了をこの結果で認定しない。

| 項目 | 内容 |
|---|---|
| Program / class/method | NK-OPS-001 / `BackupStartIntentFiles.create/requireClear/begin/retire/close`、`MorningControlScope.withClearIntent/executeNativeOwned`、`BackupUnitStartClient.start` |
| 関連正本 | OPS-009、BAK-001、UI251、SS341§5-6、SS343§6.15、SSC-105/106、BUG-315/YKT-248 |
| fixture | `BackupPublicationFixture`の保持directory FD・実new-only file IO・合成root0/tmpfs metadataと限定gate、`MorningControlScopeTest.HeldM`、既存start child。fixture owner/FS合成を実root受入と混同しない |
| 独立期待値 | `backup-start.intent`は固定の空root0600 fileで、同bootの次回M admissionが存在/IO不明を拒否。公開が不明なら`systemctl`は0件。期待名・順序・permissionはSS341/343のliteralから定め、Production `begin`/`start`をoracleに使わない |

| Test ID | 目的・入力/操作 | 独立期待結果 |
|---|---|---|
| PT-OPS-BFENCE001 | 空namespaceからbegin→close/reopen観測→同token retire | 空固定markerが1件、残留中の次回admission/二重begin拒否。同一owner・同inode tokenでのみ削除・dir sync後に不存在 |
| PT-OPS-BFENCE002 | file作成後dir force故障 | 起動を許さずmarkerを保持。次回admission拒否、暗黙repair/unlinkなし |
| PT-OPS-BFENCE003 | 既存空/非空marker | 内容を信用せず存在だけで拒否。既存byte不変更 |
| PT-OPS-BFENCE004 | UID/ACL/readonly/非tmpfs/metadata/gate/interrupt負例 | file新規作成0、固定IOException/StorageIoException。null契約はconstructor/begin/retireに別負例 |
| PT-OPS-BFENCE005 | 別owner並行begin | CREATE_NEWのwinner1件、loserは失敗、marker1件/次回拒否 |
| PT-OPS-BFENCE006 | null root/security/source/gate/intent/context | `NullPointerException`または固定拒否、file mutation0 |
| PT-OPS-MCTRL014 | M保持下で残留拒否/markerなしの順序を注入 | intent確認はDB/原本作成、fixed stop、A取得、INVALIDより前。拒否で後続callback0件 |
| PT-OPS-BSTART009 | 起動clientの前にintent portを注入 | root/policy→intent→client。公開不明ならclient0件、start送達不明時はUNKNOWN・自動retire0 |

実行環境、commit、command、F/E/S、line/method/class/branch coverage、静的結果、関連BUG/SSC、sanitized証跡とhashは[232](232_NK-OPS-001_Backup起動intent_実行結果.md)に記録する。PTの直接`retire`は親の全終端証明を模したfile adapter操作であり、Production親へ許可を与えない。Native固定root、親M/A・今回fresh receipt/stop、VM Unit起動と再boot後admissionは別途必要。
