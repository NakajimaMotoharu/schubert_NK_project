# NK-OPS-001 API／Web非秘密YAMLのUnicode境界

PT-OPS-APICFG009、PT-OPS-WEBCFG009。API／Webの非秘密設定 `parse(String, String)`、SS343 §4–5、既存のUTF-8の設定入力契約と非公開診断。ファイル設定読取の不正UTF-8は別のPT-OPS-CFGFILE-003を参照する。

| Test ID | 入力 | 独立期待値 |
|---|---|---|
| PT-OPS-APICFG009 | 共通YAMLの合法な設定行と、コメントに①U+1F642、②孤立した上位サロゲート、③孤立した下位サロゲート | ①設定値 `DEBUG`。②③ `IllegalArgumentException`、固定API診断、原因なし、抑制例外0。 |
| PT-OPS-WEBCFG009 | 同じ公開合成入力をWebへ渡す | ①設定値 `DEBUG`。②③ 同型の例外、固定Web診断、原因なし、抑制例外0。 |

現候補の正確な入力とJDK25／固定SDKの組合せをsource・manifestに保存する。秘密、保留鍵、実ファイル読取、DB、サービス起動はfixtureに含めない。既存のサイズ境界APICFG008／WEBCFG008は元証跡を保持する。

## 局所試験結果

PG42390、a3b08ecd60bbfe6c02def78a4146bf7f027f2ae6／Main 1e4e9e64830b552727043f3cb8b9435b28cba472。2件成功・失敗/エラー/skip各0、4異常と2正常対照。現Checkstyle／PMD／SpotBugsは0、欠落型0。旧サイズ境界の製品三物理と完全一致。evidence/01_PT/018_NK-OPS-001/evidence/PG42390-f03-bootstrap-yaml-malformed-unicode-v1/manifest.json SHA256 992c8a55f17f8cd77096c19de92b8e4cf54ebcf9d5b0ff4b8176e74c2bc084f4。当試験の全体coverageと実設定ファイルは未測定。
