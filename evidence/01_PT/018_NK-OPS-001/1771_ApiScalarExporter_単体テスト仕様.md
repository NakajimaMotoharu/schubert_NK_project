# API precision registry scalar出力 PG/PT仕様

NK-OPS-001/RD171/UI252/SS311351/411、PG-D601、主WBS-P018-09/C07参照0加算、group1998。開始29/71・2/5/9pp/cap10はPG8416/event1998へ固定。旧1745/1747のSDK fixtureはPrometheus registry派生、production ExactDurationMeterRegistryはSimple派生のため、成功の転用/確認再演をしない。

## 製造契約

ApiScalarMetricExporterをAPI監視packageに追加し、同roleのCounter/Gauge二種を一adapterで標準textへ変換する。API→Web参照/共用Bootstrap拡張/同一classのmodule複製/既ApiDuration変更をせず、共有は既公式SDK model/writerのみ。caller-approved名前/label keysをdeep copy、name/labels/valueを一回capture、sourceを保持/closeしない。counterは有限非負（小数可）、gaugeは標準double/明示NaN未知を保持。型不一致/null/不正namespace/labelは拒否、provider RTE/Errorを握り潰さずchecked writer IOを固定message+同causeへ。

当群は低位generic codec、固定API label値catalog/実endpoint/mode接続は後続未完。SS/六POM/Bootstrap/Web/既API MainとUnitを変更しない。

## ApiScalarMetricExporterTest SCALAR001～024（新24）

|ID|目的/独立入力→期待|
|---|---|
|001|literal counter2.5、SS351名/type/label順/重複suffixなし|
|002|gauge NaN/0/負/±Infの標準text、unknownを0へしない|
|003|counter0/MIN/MAX有限値を保持|
|004|counter負/NaN/±Infを拒否|
|005|空registry/namespaceとunknown meterは空text|
|006|同名別型Gauge/Counter/Timer/Summaryを両経路で拒否|
|007|source/map/writer nullを両境界で拒否|
|008|namespace name/set/要素nullを拒否|
|009|不正prefix/uppercase/Counter suffixを拒否|
|010|invalid label/le/欠落/過剰を拒否|
|011|実duplicate tagsを独立assert後に拒否|
|012|quote/backslash/newline escaping、返却textの独立literal|
|013|borrowed source nonclose/閉鎖済み拒否|
|014|providerで入力map/setを変更しても事前deepcopy保持|
|015|Counter provider RTE identity保持|
|016|Gauge provider RTE identity保持|
|017|Counter provider Errorを成功化しない|
|018|Gauge provider Errorを成功化しない|
|019|Counter checked writer IO同cause/固定message/owner保持|
|020|Gauge checked writer IO同cause/固定message/owner保持|
|021|Counter name/valueの一回read、後続名へ変化しても初回承認名のみ|
|022|Gauge name/valueの一回read、同様に初回名のみ|
|023|二family/同family二seriesを正しいtype/metadata/値で出力|
|024|有限64並行scrape/別sourceに状態を漏らさずliteral値、join10sec/sleep0|

## ApiScalarPrecisionContractTest APISCALAR001～008（新8）

actual ExactDurationMeterRegistry(SimpleConfig.DEFAULT,MockClock)＋供給済み技術Recorderだけを使用し、DB/JMS/controlを開かない。Gauge10family/51series（outbox6/jobs5/pool4/MQ圧36）、Counter4family/801series（Inbox768/operation8/redelivery18/MQstage7）、合計14family/852sampleを独立SS literalで検証。

|ID|目的/独立期待|
|---|---|
|001|初期852sample/14family・51NaN/801zero、timer/internal helper混入なし|
|002|供給pool/outbox/jobsとMQ一destinationの固定Gauge値、未取得はNaN保持|
|003|四Counterの固定eventを各一回/一部二回、期待1/2・full name不変|
|004|STANDARD初期sourceの両scalar出力は空、未取得NaNと未登録を区別|
|005|有限64worker event後の固定Counter64、source閉鎖なし|
|006|Gauge known→missing→known zero、正しいNaN/0とfraction秒|
|007|namespace subset選択/unknown・histogram等非選択、caller map不変更|
|008|二sourceの供給値/unknown/Counterを独立保持、同exporterの再利用|

全期待はliteral/固定vectorと独立計算、production methodでexpected生成なし。**新32/2**、normal六/NullAway/Spotless→original32→新Main1実四100/PMD-CS-SB-missing0/CRC0/session1→全physical/source-owner/役割→1772へ。元command/OS-JDK/source/branch/日時/exit/input/期待/実際/XML/log/coverage/static/hash/BUG-YKTを新onlyPG84xx slotと公開manifestへ保存。実装済み違反は修正前915/916、未実行/failed/skippedをPASSへ算入しない。

現在PT/coverage UNRUN。formal1964-53/原190新受入0/工数null・QA051final/whole451/CHR/F03Root11・actual VM/Root/DB/JMS/鍵/native/endpoint/配備/拒否未特定HOLD。元/v4/v5/当初見積り不変更、共有枠を専有費へ換算せず、通常区切りで停止しない。
