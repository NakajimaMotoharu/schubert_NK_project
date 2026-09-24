# NK-OPS-001 API設定読取結線単体テスト仕様書

Program NK-OPS-001。Class/method `ApiConfigurationLoader.production/load`、`NonSecretConfigSource.read`。RD SYS-002/004・MQ-001、UI212/231/253、SS311/321/342/343 §4–5、PG-D-276。隔離sourceは公開非秘密固定YAMLだけを返す。実`/etc`/credential、OS account/ACL、外部Java main・DB/JMS接続は本仕様の対象外。

| Test ID | 目的・事前条件/fixture | 入力・操作 | 独立期待値・根拠 |
|---|---|---|---|
| PT-OPS-API-LOAD-001 | 手組common/API2層 | `load`1回 | SourceはAPI指定で1回のみ。common DEBUG、API loopback61617、default version001。SS343の層順をliteralから照合 |
| PT-OPS-API-LOAD-002 | 合成StorageIoExceptionと別process key | Source失敗/不正YAMLを別々に注入 | checked source失敗は同一例外identity、不正keyは固定redacted parser拒否。原因を混同しない |
| PT-OPS-API-LOAD-003 | null source/contents、本番factory | constructor/load/factory | nullはNPE、factoryは非null。実fileは開かない |
| PT-OPS-API-LOAD-004 | 同じ公開2層、32 fresh read | 8 threadで32回load | 全結果が手組literalのSTANDARD/max8、Source API指定32回。単一cached値で代替しない |
| PT-OPS-API-LOAD-005 | SSC-080固定非秘密env Map | 固定値、欠落、別path、大小文字alias、未知secret-like key、無関係PATH、null Map | 正規`SCHUBERT_NK_CONFIG_DIR=/etc/schubert-nk`だけ（無関係OS keyは無視）読取前受理。異常は固定診断でSource呼出0、nullはNPE。SS343 §4の固定root・秘密分離から独立転記 |

正常・境界・異常・null・例外・並行を検証。再送は設定読取に非該当。Production期待生成・coverage除外なし。実行command/日時/commit、coverage、結果、BUG、証跡path/hashは067と同Program evidence/manifest.jsonへ記録。
