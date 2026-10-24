# Web catalogの検証済みLabels→model直接接続 PG/PT仕様

NK-OPS-001/RD171/UI252/SS311351/411、PG-D599、WBS-P018-09/C07参照0加算、group1994。開始28/72・2/4/8pp/cap10はPG8392/event1994に固定。1766/bf7ceeed0の新100/5四100を保持し確認だけで再演しない。

## 製造契約

Web Counter/Gauge/Timerにfixed catalog専用scrape APIを追加する。既generic API/checked-writer seamは変更せず、内部encodeへOptionalのimmutable catalogを渡す。名前はBUG1701の単一captured String、tag list/key/valueも一回read/copyし、**検証済みSDK Labelsをそのpoint modelへ直接渡す**。別preflightと後続mutable再読取の組合せにはしない。Generic経路は従来のcaller-approved key契約のまま、approved経路だけSS351固定七family/label値を強制する。

WebMetricCatalogはname-domain解決とtag-copyを分離し、public labels(Id)では未知名をtag providerより前に拒否する順を維持する。package内部ではcaptured name/tag listからLabelsへ変換、id.getNameを再読取らない。API Main/Bootstrap/POM/上位/実endpoint・ownerは変更しない。

## 新APPROVED001～012（WebApprovedMetricExporterContractTest）

|ID|入力/期待・独立根拠|
|---|---|
|001|実precision Web registry/五Recorder→固定七family/2219wire samples、13NaN/HTTP1750/media36/hist420、SS literalから独立算出|
|002|approved Gauge全四familyの不正値を拒否、generic caller-approved経路では同fixtureが出力可能な差を明示|
|003|approved Counter二familyのraw route/未知method/media mode等を拒否|
|004|approved Timerのraw route/別serviceを拒否|
|005|Gauge providerがvalue()で元Tagを変えてもコピー済み許可値を出力、元変異は実assert|
|006|Counter providerがcount()で元routeを変え、Id名も後続変化しても初回name/labelsだけを出力|
|007|Timer providerがtakeSnapshot()で元routeを変えても初回name/labelsだけを出力|
|008|unknown meterのvalue providerは呼ばず全approved経路が空text|
|009|空registry/借用保持/閉鎖済みregistryの拒否を三APIで確認|
|010|tag provider RTE/Error identity保持、raw format/正常化なし|
|011|実precision registry・有限64並行scrapeの七family/固定値/系列数、join10sec/sleep0|
|012|source nullと全七familyのmissing/extra/duplicate/null tag/valueを境界拒否、catalog/name snapshotを回避しない|

期待名/keys/値/2219は固定SS literal、production expected生成なし。可変Id/Tagは公開SDK stubで、private反射/実外部値なし。実sourceはWeb内のみ、API source/旧API30の確認再演なし。

## 固定必要matrix・品質

新12＋必要Web unit48/catalog14/Web接続18＝80＋共通identity4（同classのAPI一件を含む）＝**96件/9suite**。API一件の確認は共通境界fixture内数で、旧API30の再資格ではない。新source normal六/NullAway/Spotless→真正96→Web三exporter/catalog/textの実5四100/PMD-CS-SB-missing0/CRC0/一exec→全physical/source-owner/役割→1768へ。一般API/TIMERENC/SUMENCの元goldenは変更しない。source/branch/command/OS-JDK/日時/exit/input/期待/実際/XML/coverage/static/hash/BUG-YKTは新onlyPG84xx元slot/公開manifestへ。

現在PT/coverage UNRUN、実装済み違反は修正前915/916へ。DEBUG/STANDARD統合policyとactual endpoint/VM/Root/DB/native/鍵/配備/拒否未特定操作は当群の外/HOLD、後続未完とする。formal1964-53/原190新受入0/工数null・QA051final/全451未受入/元-v4-v5を維持。通常区切りで停止しない。
