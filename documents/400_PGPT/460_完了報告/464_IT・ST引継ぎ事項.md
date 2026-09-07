# IT・ST引継ぎ事項

## 1. 位置づけ

後続Linux serverでのみ確定できるcomponent間、実service、性能・容量・可用性・運用の実測値を引き継ぐ。本工程はIT/ST完了を宣言しない。

## 2. 初期引継ぎ

| ID | 項目 | PG/PTで保証する範囲 | Linux serverでの確認 | 状態 |
|---|---|---|---|---|
| ITS-H-001 | Caddy/Web/API/Artemis/PostgreSQL接続 | 設定schema、単体契約、sanitized fixture | TLS、systemd順序、実socket/credential/権限 | 引継ぎ予定 |
| ITS-H-002 | Artemis容量・再配送 | Embedded/schema、1/5/25秒、DLQ/Expiry契約 | Journal/paging、disk 90%、restart、実時間 | 引継ぎ予定 |
| ITS-H-003 | PostgreSQL backup/restore | DDL/Flyway、role/grant、command contract | `pg_dump -Fc`/restore、RPO/RTO、専用role | 引継ぎ予定 |
| ITS-H-004 | 性能・大容量file/media | Range/hash/atomic file単体境界 | Master 59,627 file/19,240,707,190 byteで容量・性能 | 引継ぎ予定 |
| ITS-H-005 | Characterization | NK adapterと関連case単体契約 | Deployed NKで24 case、DIF-001～016のみ | 引継ぎ予定 |
| ITS-H-006 | Password照合p95 | pbkdf2-v1/310000/16byte salt/256bitの独立JCA検証、256byte全長差 | 本番CPU/Java25でwarm-up後Login照合p95を測定。SS314の0.5～1.0秒から外れる場合security review。同一IDのparameterを変えない | 引継ぎ予定 |

| ITS-H-007 | Username key拡張migration・切戻し | SSC-014/V007の比較key96byte、表示/audit64byte、旧64byte拒否→DDL拡張、UK/NULL/境界、実Loginの独立PT | 既存schemaからV007へFlyway適用と復旧を実serverで確認。旧codeへ切戻す前にkey64byte超の有無を集計し、存在する場合は切戻し不可として運用判断。値の切捨て/再計算/削除で回避しない。JDK更新でUnicode増幅guardを再実行 | 引継ぎ予定 |

## 3. 更新履歴

| 日付 | 内容 |
|---|---|
| 2026-09-01 | 初期引継ぎ対象を登録。 |
