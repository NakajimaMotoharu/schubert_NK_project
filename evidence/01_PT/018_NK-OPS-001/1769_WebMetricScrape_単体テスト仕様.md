# pure Web DEBUG/STANDARD scrape policy PG/PT仕様

NK-OPS-001/RD171/UI252/SS311351 §6/8/10・411、PG-D600、主WBS-P018-09/C07参照0加算、group1996。開始28/72・1/3/6pp/cap10はPG8404/event1996へ固定。先行1768/cd43c1adbのcodec品質は同byteを照合し、旧96の確認再演なし。

## Production契約

WebMetricScrapeはborrowed MeterRegistry/modeを操作引数に取り、sourceをfield保持/close/新規登録せず純粋なtext取得だけを行う。modeは既HttpMetricContractのexact DEBUG/STANDARD、unknown/nullは拒否。STANDARDはsourceのtype/closed/meters/valueを読まず空text、DEBUGは既precision capabilityを検査して三approved exporterの七family textを一つの戻り値へまとめる。後段failure時に部分文字列を成功返却せず、provider failureを隠さない。各pointのsnapshotだけを保証し、scrape全体のtransaction/同時点性を捏造しない。

三formatter instanceだけを保持し外部資源を取得しない。API/Bootstrap/POM/旧Main/Unit/SS/実HTTP/管理server/Unitや実mode切替は変更しない。このpolicy完成は実STANDARD service停止/公開制限や実endpoint受入ではない。

## 新SCRAPE001～014（WebMetricScrapeTest、独立14/1）

|ID|入力/期待・独立根拠|
|---|---|
|001|STANDARD/不正値を持つsource：空text、getMeters/isClosed/value読取0、既sourceは保持|
|002|DEBUG実precision registry初期：SS七family/2219sample、13NaN/HTTP0/media0|
|003|DEBUG供給済み：literal HTTP1/media7/HTTPsum1e-9/pool3等、source nonclose|
|004|DEBUG→STANDARD→DEBUG純粋policy呼出：中間空・元の供給値/登録を破壊/closeせず再出力（実運用mode切替とは別）|
|005|DEBUG空precision registry：空text、source保持|
|006|DEBUG非compatible source：CONFIG_INVALID、provider/closed読取0|
|007|null source/null mode/未知・空・lowercase mode拒否、source読取0|
|008|DEBUG閉鎖済み拒否、STANDARD閉鎖済みでも詳細sourceを読まず空（再openなし）|
|009|tag provider RTE/Error identity保持、source保持|
|010|Gauge出力後Counter故障：Gauge実読取を確認し、全体result未設定/例外、部分成功返却なし|
|011|unknown metricのvalue provider未読、DEBUG空text|
|012|有限64並行scrape、七family/固定3値/2219sample、future join10sec・sleep0|
|013|選択された不正labelはreject、汎用APIへfallbackしない|
|014|故障sourceの後に同policyで正常source：古い部分text/source/failureを保持せず固定正常値|

期待集合/値はSS literal/独立固定入力から作成し、production methodでexpectedを生成しない。compatible fake registryは公開markerとNoop meterの通常PT stubのみ、実sourceとの合否/実native資格へ混同しない。real precision registryケースを別に含める。秘密/実利用者値/反射なし。

source固定→PG840x正常six/PT0/NullAway/Spotless→original14/1→新Main1実四100/PMD-CS-SB-missing0/CRC0/session1→全physical/source-owner/役割→1770へ。旧codec四100は別source/runのcounterを加算せずbyte依存として照合。manifest/元slotに日時/OS-JDK/branch/source/command/exit/input/期待/実際/XML/coverage/static/hashを保存、未実行/failed/skippedをPASSにしない。実装済み違反は修正前915/916へ。

formal1964-53/原190新受入0/工数null・QA051final/whole451/CHR/F03Root11・actual endpoint/VM/Root/DB/native/鍵/配備/拒否未特定HOLDを維持。元/v4/v5/当初見積りは固定、共有枠と専有費を混同しない。通常区切りで停止しない。
