# Web Gaugeの精度registry→標準text PG/PT仕様

NK-OPS-001/RD171/UI252/SS311351/411、PG-D596、WBS-P018-09/C07参照・追加予算0、group1988。開始1/3/6pp/cap10、fresh26/74/reset1793382075はPG8348/event1988に固定。1760 source6c91のMainを保全、既4222・SDK/Gauge既成功・Counter44を確認だけで再演しない。

## 着手/終了依存と製造

既Web precision registryはSimpleMeterRegistry派生であり、1742の別PrometheusMeterRegistryでの成功を当registryへ転用できない。WebGaugeMetricExporterを新規に実装し、WebMetricTextの既namespace/label/writerをbyte不変で再利用する。公式GaugeSnapshot builder/textwriterへvalue()一回だけを渡す。Gauge標準double（有限負値/NaN/±Infを含む）の符号・意味をformatterで勝手に変えず、各業務gaugeの非負invariantは既Recorderが所有する。既pool/outbox/streamが明示するNaN=未取得と既知0を保持する。null/provider failureとNaNを混同せず、sourceは借用・closeしない。Bootstrap/API/POM/上位/外部仕様を変更しない。

## 固定Test ID/独立oracle（新22/2、未実行）

|ID|class/目的・入力→期待根拠|
|---|---|
|GAUGEENC001|WebGaugeMetricExporterTest.gaugeenc001：literal2.5、SS351 pool family/type gauge、exact sorted labels/text|
|GAUGEENC002|002：0/±MAX/±MINのwireを独立Double literalで保持、負値のclamp禁止|
|GAUGEENC003|003：明示NaN/+Inf/-Infの標準text、unknownを0へ捏造しない|
|GAUGEENC004|004：二系列/quote・backslash・newline escaping、literalwire|
|GAUGEENC005|005：同名Counter/Timer/SummaryはIAE|
|GAUGEENC006|006：source/namespace/name/keys/要素nullを境界拒否、NPE正常化なし|
|GAUGEENC007|007：不正nk名/label/le/欠落/過剰keysをIAE|
|GAUGEENC008|008：重複tagを持つMeter.Id identity/実key列の独立assert後に製品拒否|
|GAUGEENC009|009：空registry/namespaceとunknown meterは空text|
|GAUGEENC010|010：source借用維持、閉鎖済みはISE|
|GAUGEENC011|011：provider value()一回だけ、入力変更なし|
|GAUGEENC012|012：provider RTE identity/owner保持|
|GAUGEENC013|013：provider Errorを成功へ変換しない|
|GAUGEENC014|014：providerで入力map/setを破壊しても事前deepcopy保持|
|GAUGEENC015|015：writer checkedIOの同cause/固定message/source保持|
|GAUGEENC016|016：nullwriter/不正namespaceをprovider読取前に拒否|
|WEBGAUGE001|WebGaugeExporterContractTest.webgauge001：actual OverflowSafeHttpMeterRegistryと三Recorder、4family/13gauge、初期すべてNaN。HTTP counter/timer/helper/media counter非選択|
|WEBGAUGE002|002：pool 3/5/2/8→missing NaN→既知0/0/0/1、元immutable tuple不変|
|WEBGAUGE003|003：outbox literal2/3/0、ages1.5/2/0秒、missing NaN/既知空0、単一publicationは各gaugeの観測であって全scrapeのtransaction保証でない|
|WEBGAUGE004|004：AUDIO2/VIDEO0/MUSIC未取得NaN→AUDIO missingだけNaN、固定三label|
|WEBGAUGE005|005：別owner全NaN/被測定owner供給値/STANDARD空、借用nonclose|
|WEBGAUGE006|006：有限64並行scrapeで固定既知13値とfamilyが一致、future join10sec・sleep0|

期待値は固定SS名/label・独立literal2/3/1.5/13・手作りwireから生成しproduction methodで作らない。新22のみ、変更は新Gauge1Main/Unit1/明示tools接続Test/helper。必要qualityは新Gauge＋再利用WebMetricTextの同exec実四100/静的0/normal六/全physical-source-owner/責務。既helper/recordersの過去counterは合算しない。metadata反例は製品PTへ加算0。

## 実行・証跡（UNRUN）

source固定→PG835xの正常six/NullAway/Spotless（PT0）→新22/2一JVM→独立post/CRC0/一exec/全四100/PMD-CS-SB-missing0→all-six physical/全source責務とinput hash→1762。fixture/actual/expected/XML/coverage/command/OS/JDK/exit/branch/関連BUG・hashは各公開manifest/元own slotに保持。未実行/failed/skippedをPASSへ算入しない。現在BUGなし、見つかった実装済み違反は修正前915/916へ。

actual endpoint/VM/Root/cohort/native/DB/Backup/鍵/配備/拒否未特定操作はHOLD、起動・本番接続なし。formal1964/53・原190新受入0・工数null・QA051final・whole451未受入を維持。試験終了だけでPGPT完了/IT-ST完了にしない。
