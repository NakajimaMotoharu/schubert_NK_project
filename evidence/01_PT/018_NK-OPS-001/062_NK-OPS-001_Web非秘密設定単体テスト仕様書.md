# NK-OPS-001 Web非秘密設定単体テスト仕様書

Program NK-OPS-001。Class/method `WebNonSecretConfig.parse/value/canonicalSha256`。RD SYS-002/004・AUT-002・MED-001、UI212/223/226/237/253、SS311/342/343 §4–5、PG273。`src/deployment/config/common.yml.template`と`web.yml.template`を配布候補とする。対象はjar default＋common＋Webの非秘密YAML。env location、credential tree/file属性、DB/JMS実接続、root admission、外部process起動は対象外で未認定。

| Test ID | 目的・fixture/事前条件 | 入力・操作 | 独立期待値・根拠 |
|---|---|---|---|
| PT-OPS-WEB-CFG-001 | SS343 §5の15初期値 | 空の2層をparseし全固定keyとcanonical hashを照合 | 文書から独立転記したUTF-8 `key=value LF`昇順golden vectorのSHA-256。Production map/formatterは期待生成に用いない |
| PT-OPS-WEB-CFG-002 | 同fixture | common DEBUGとWebの合法port・timeout境界・wait/stream1・別rootを上書き | source優先順、port1/65535、100ms/1s/1500ms、hash変化。session上限2を維持 |
| PT-OPS-WEB-CFG-003 | 同fixture | 重複、未知/secret、別source key、list/map/null/非文字key、alias、複数document、CRLF/BOM、raw/decoded placeholder、空quote、16KiB超、改行値 | 全件固定redacted `IllegalArgumentException`。parser診断や入力値を公開しない。SS343 §4 |
| PT-OPS-WEB-CFG-004 | 同fixture | 固定key drift、両portの0/65536/衝突、timeout99/2001ms/3s、wait0/21/逆転、stream0/21、相対/同一/入れ子root | 起動前非成功。SS343 §5の固定値・範囲・root区別を独立確認 |
| PT-OPS-WEB-CFG-005 | 同fixture | null入力/未知key、32並行parse | null契約NPE、未知key固定拒否、全hash同値。秘密入力なし |
| PT-OPS-WEB-CFG-006 | 配布template2file | 実fileをPT fixtureで読みparseしgoldenと照合 | template全値とcanonical hashがSS343の独立vectorに一致 |

正常・境界・異常・null・例外・並行を網羅。再送は設定parseに適用しない。除外設定なし。YAMLはflat dotted-keyのみ受け、重複・alias・非scalar・16KiB超を拒否する。実file identity/ACLとsecret搬送は後続必須gate。実行command/日時・commit・coverage・BUG/SSC・manifest/hashは063へ記録。
