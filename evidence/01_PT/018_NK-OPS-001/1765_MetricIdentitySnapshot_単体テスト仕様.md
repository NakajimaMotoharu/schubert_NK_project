# metric名の承認時snapshot PG/PT仕様

NK-OPS-001/RD171/UI252/SS311351/411、WBS-P018-09/C07参照0加算、group1992。開始27/73・1/3/6pp/cap10はPG8378/event1992へ固定。前群1764/4234e0ffdまでの成果を保持し、Mainを変更せず現sourcee5f0/8368原0081b454の既compileで独立4を先に実行する。

## 目的と独立期待値

generic codecの契約「approved namespaceだけを出力」に対し、Meter.Id.getNameが初回と後続で変化する入力を用意する。初回名はSS351、後続名は非catalogの固定fixture。各codecは初回承認名を一回copyしてmodelに使用し、後続名を再読取って別familyへ出してはならない。ラベル・Snapshotは正常固定値、provider mutationや実外部入力なし。Idは公開SDK APIのstubでありprivate反射なし。

|ID|MetricIdentitySnapshotContractTest method/対象|期待値|
|---|---|---|
|MIDNAME001|midname001/Web Counter|`nk_http_requests_total` type counterのみ、非承認名不在・name一回|
|MIDNAME002|midname002/Web Gauge|`nk_db_pool_connections` type gaugeのみ、非承認名不在・name一回|
|MIDNAME003|midname003/Web Timer|`nk_http_request_duration_seconds` type histogramのみ、非承認名不在・name一回|
|MIDNAME004|midname004/API Summary|`nk_db_query_duration_seconds` type histogramのみ、非承認名不在・name一回|

全期待名/type/keyを独立literalで記述し、production methodでexpectedを作らない。snapshot/valueは正常単純vector、scalar混合読取り/書込をfixtureで拒否する。先行4のactual失敗が既実装違反を示した場合だけ、修正前915/916へ起票し全四対象を是正する。Mainを先に直して再現結果を失わない。

## 是正が必要な場合の固定必要matrix

新4＋必要既API unit24/接続6＝30、Web unit16×3/接続6×3＝66、合計 **100件/9suite**。変更見込はAPI Summary/Web三exporterのname読取一回化だけ、normal六/NullAway/Spotless後に新source真正100、当四exporter＋byte不変WebMetricTextの実5四100/静的0・全physical-owner/責務を要求する。既catalog Main/14は当変更のcallerでないため確認再演しない。旧metadata/coverageを新sourceへ加算しない。

source/branch/command/OS-JDK/入力/期待/実際/XML/exec/exit/coverage/static/hash/BUG-YKTを新onlyPG83xx slotと公開manifestへ保存し1766へ結合。原4222/旧SDK成功確認の再演0、Failed/skipped/not-runを合格へ加算0。当初estimate/発見/手戻り/再認証を分離。actual VM/Root/DB/鍵/native/endpoint/配備/拒否未特定HOLD、formal1964-53/原190新受入0/工数null・QA051final維持。name閉鎖後に検証済みLabelsのmodel直接接続/mode policyへ継続。
