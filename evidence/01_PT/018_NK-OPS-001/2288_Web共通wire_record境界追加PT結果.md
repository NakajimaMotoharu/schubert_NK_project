# Web共通wire record・境界追加PT結果

source54e84fe04836dd88c3adfda5ac3f010eb591a7ee、PG-D723/2287/主WBS-P005-02。既規約是正BUG1940等の修正成果・旧source8を保持し、本群は新規wire009..012の四契約を追加したsourceで元8＋追加4を一run実行したもの。Main不変更、実装違反未観測のため新BUG起票対象なし（TDD/未測定分岐の追加PT）。

|工程|actual・manifest SHA256|
|---|---|
|12010 元execの非実行行map|0・90dfcdab551d7ca76ecb55df23a36607e1a4bbbf0c023580d5a573dc1b2844db|
|12012 独立UI byte/golden三/元8不変|0・c550a50234d1798bc97b34a3cee5e3cc5f57b73eead048943d87985170181aba|
|12014 独立追加1350token/12改変負例|0・d08647673459a18664b757eab45a393a3588bb225d3d7935589aa9173f9a8a17|
|12016 normal六/PT0|0・214dca80b3e55dcddd14932b1d2e77a4f5ba48bc9e2a0521890890081292b94a|
|12018 元8＋新4/一suite|0・83e830344ae46b8097d1ca8027c34e7d2dc7fb3596206e9da2ffe3c0308a4048|
|12020 実PMD/CS|1保持・3bfc240dc4772cdaec9c574f9e0527fdab3d6ba89d28872161c2de5aaaf3ae3b|
|12022 独立XML/CRC/byte/全counter|0・c5d6237eca375bc4735b29fab91cc52ca8e57b3667d36836b0591eb73e709e17|
|12023/25 現Thread二/八負例|0・4f6727e8ba7420a072ea01a4e7dd3a30b0782ac9b690810a2c3c2c87babcca13 / 226c47f3145461e122cf49fc96a8295e9119212d56fd20719af9007f652f8d4c|
|12024/26 原ownertrace/監査|0・b20e91c8e05ae52ab6df7f34ed93053b7d05f324659e75e6987d7fc3c7fbc167 / 11c8375862bf5b37eb85e325f6d3b4612e7be40ee408da897eede282ade73c8e|

## 新四caseの独立期待と真正結果

- wire009：UI234 PAGED48とUI236§11.3の一基点表から別Pythonで1/2/50record（976/1648/33904byte）を構成し、各SHA ad126708/902a9637/73036d0aをJava fixtureへ固定。実行時全byte digest一致、page六項目、ID降順、受付ID/Username/UTF8概要/三状態/日時Optionalの全値・件数/順序が明示値一致。borrowed providerは不変更、交換後providerを上書きしてもtyped結果不変、listは変更拒否、一send/pending0/request消去。
- wire010：非空input recordはfields callbackを呼ぶ前に固定INVALID_INPUT、send0/pending0。CallbackのAssertionErrorで早期拒否契約を反証できる。
- wire011：QSS最小未満303・最大超33905・QSSに対する別QSB layout・header総長と実byte不一致を、同型INVALID_RESPONSE/一send/pending0/redactionで拒否。
- wire012：recordのID0/未知state/ANSWERED日時欠落/予約byte非spaceを同様に拒否し、再送なし。recordコピー後のfinally消去経路は実測hit、内部temporary byteの直接読取/反射はしない。公開所有後条件とsource/分岐証拠を区別する。

新四は12018 manifestのclass#methodとTEST XMLへ一意対応。全12/一suite F/E/S/abort0、ja-JP一exec PG12018-BUSRECORD-JP、旧exec合成0。直接九Mainは113L24M9C26B全miss0、前2L1M5Bを当runで解消、branch0/0 classはN/A・enum等既定filter/手動除外追加0。完全Web358/350解析+8packageのcounter未達は12022 measurementに保持し、全Web/全PGPTの100%とはしない。

全Main1843同byte/他Test1960同byte・一SourceFile二物理Test差。12028でraw Code表現/debug表の別hashを結合、意味保持は元8raw token不変・独立新golden/typed scalar・新source全12実行で判断する。static2→2（元Thread二）/CSprocessing0/gate1、Threadの原180task/10秒/JavaSE単所有を現source再認証、新適用性参照0。source/cost P005-02を983行一SHA/他982不変で保持、予算/受入/監査同HOLD1。

日時/OS/JDK25.0.4/Maven3.9.12/JUnit5.13.4-Platform1.13.4/JaCoCo0.8.15/PMD7.28/CS14.3/source/branch/command/終了code/input/期待/actual/hashは各manifest。すべて合成fixture・秘密なし、保留二工具/Graph9/鍵close・実Broker/DB/VM/Root/native/私有raw操作0。正式1964-53/個別17-190/工数null/QA051final/全F03・451未受入は不変更。新PT四/直接九測定と旧24是正を別成果として記録する。
