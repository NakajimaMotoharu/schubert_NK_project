# WEBCAT015 名前取得済みのlabel検証

NK-OPS-001、WBS-F03／P018-09、MON005～013／UI252／SS351／354、BUG-3251。旧WEBCAT001～014は[既仕様](2705_両Catalog単一exec全面測定56_単体テスト仕様書.md)を保持。対象はpackage-private `WebMetricCatalog.labels(String,List<Tag>)`。固定値・独立期待の7familyの各name/key/valueを既仕様から列挙し、戻りのlabel個数と全key/valueを比較する。meterや他のproduction methodをexpected生成に使用しない。

入力はメモリSDK値のみ。プールのmutable labelを返却後に変更し元配列を空にしても固定戻りが変化しない。stateだけならmissing固定、未知nameはunknown固定、null listはNPEで判定する。元14と追加1の計15を固定した当sourceで実行。製品Main、承認済みresource、SDK byteを照合し、静的、全7物理のCRC、当Catalogの生四を独立post。実Scrapeや他型の不足は未受入。旧exec合算なし。
