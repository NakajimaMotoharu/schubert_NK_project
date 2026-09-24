# NK-OPS-001 API非秘密設定単体テスト仕様書

Program NK-OPS-001。Class/method `ApiNonSecretConfig.parse/value/canonicalSha256`。RD SYS-002/004・MQ-001・DAT-001、UI212/231/253、SS311/321/342/343 §4–5、PG272。`src/deployment/config/common.yml.template`と`api.yml.template`を実配布候補とする。対象はjar default＋common＋APIの非秘密YAMLで、env location、credential tree/file属性、URL/role実接続、root admission、外部process起動は別工程依存として未認定。

| Test ID | 目的・fixture/事前条件 | 入力・操作 | 独立期待値・根拠 |
|---|---|---|---|
| PT-OPS-API-CFG-001 | SS343 §5の固定初期値 | 空の2層をparseし22固定keyとcanonical hashを照合 | 文書から独立に転記したUTF-8 `key=value LF`昇順golden vectorのSHA-256。Production map/formatterを期待生成に用いない |
| PT-OPS-API-CFG-002 | 同fixture | commonのDEBUG、APIの合法DB/MQ loopback port・root・整数型を上書き | source優先順とport1/65535、整数8、hash変化。固定keyは維持 |
| PT-OPS-API-CFG-003 | 同fixture | 重複、未知/secret、別source key、list/map/null/非文字key、alias、CRLF/BOM、raw/デコード後placeholder、空quote、16KiB超、改行値 | すべて固定redacted `IllegalArgumentException`。YAML構文診断や入力値を外へ出さない。SS343 §4、BUG-251再発防止 |
| PT-OPS-API-CFG-004 | 同fixture | 全固定key drift、6 Address drift、DB/MQ URLのhost/scheme/port/parameter、相対/同一/入れ子root | 起動前非成功。SS321 topology・SS343固定値/loopback/非重複root |
| PT-OPS-API-CFG-005 | 同fixture | null入力/未知key、32並行parse | null契約NPE、未知key固定拒否、全hash同値。外部secretなし |
| PT-OPS-API-CFG-006 | 配布template2file | 実fileを読むPT fixtureでparseしgoldenと照合 | templateの全値とcanonical hashがSS343固定初期値の独立vectorと一致 |

正常・境界・異常・null・例外・並行を網羅。再送は設定parseに適用しない。YAML `LoadSettings`は重複禁止、alias0、非scalar key禁止、codepoint上限を指定。Flat dotted-keyのみ本部品では許可。実file identity/ACLの安全確認は未実装なのでtemplate parse成功だけで本番設定読込完了としない。実行command/日時・commit・coverage・BUG/SSC・manifest/hashは061へ記録。除外設定なし。
