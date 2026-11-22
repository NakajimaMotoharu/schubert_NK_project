# NK-OPS-001 API／Web非秘密YAMLのUnicode境界

PT-OPS-APICFG009、PT-OPS-WEBCFG009。API／Webの非秘密設定 `parse(String, String)`、SS343 §4–5、既存のUTF-8の設定入力契約と非公開診断。ファイル設定読取の不正UTF-8は別のPT-OPS-CFGFILE-003を参照する。

| Test ID | 入力 | 独立期待値 |
|---|---|---|
| PT-OPS-APICFG009 | 共通YAMLの合法な設定行と、コメントに①U+1F642、②孤立した上位サロゲート、③孤立した下位サロゲート | ①設定値 `DEBUG`。②③ `IllegalArgumentException`、固定API診断、原因なし、抑制例外0。 |
| PT-OPS-WEBCFG009 | 同じ公開合成入力をWebへ渡す | ①設定値 `DEBUG`。②③ 同型の例外、固定Web診断、原因なし、抑制例外0。 |

現候補の正確な入力とJDK25／固定SDKの組合せをsource・manifestに保存する。秘密、保留鍵、実ファイル読取、DB、サービス起動はfixtureに含めない。既存のサイズ境界APICFG008／WEBCFG008は元証跡を保持する。
