# 1570 Web HTTP Metricラベル契約 単体テスト仕様書

2026-10-23、PG-D526/NK-OPS-001/P018-09/C07共有費0。着手0.5/1.5/3pp・上限10pp、共有10/残90/reset1793306748、元開始0。RD171 MON005～013/UI252§4～5/SS351§6・8・10/SS313。RD171のMicrometer採用を維持し、独自counter/histogram backendを製造しない。今回HttpMetricContractはその前提の閉ラベル/設定metadataのみ、実metric収集/監視server/公開/owner/ready/有効serviceの証明ではない。

対象 `src/schubert-nk-web/.../web/monitoring/HttpMetricContract` とnested Metric/Route/Method/Status/Labels、package NullMarked。Production依存/POM/既HTTP応答/既WebRequestTrace・Producer/Root/native/DBを変更しない。Webだけのservice=WEB、二metricはSS351のnk_http_requests_total(counter/4labels)とnk_http_request_duration_seconds(histogram/service,route)。9bucketは50/100/250/500/1000/1500/2000/2500/5000ms。Micrometer自身の実timer・percentile・Prometheus名変換は未実装/未検証の別依存であり、metadata成功でその合格を捏造しない。

Routeは既承認SS313のregistered template・static assetと既WebRequestTrace閉34値を独立goldenへ明記し、unknown `/**`を含め35値。raw path/query/IDをラベルとして保持せず、完全一致しなければ固定unknownへ。MethodはGET/HEAD/POST/PUT/PATCH/DELETE/OPTIONS/TRACE/CONNECTとOTHERの10値、未知はOTHER。Statusは100～599だけを1xx～5xxへ分類、範囲外は固定拒否。Labelsは閉enumだけを保持し、request mapはservice/route/method/status_class、duration mapはservice/routeだけのimmutable固定key。自由tag key/actor/ID/address/body/path入力fieldを追加しない。nullは境界拒否、modeはSTANDARD=false/DEBUG=trueのstrict二値でlog levelと結合しない。

|Test ID/method|独立期待値|
|---|---|
|PT-OPS-HTTPMETRIC001 / httpMetric001|二name/type/label集合・strict mode・9DurationのSS literal |
|002 / httpMetric002|独立35行route golden×10method literal×5status代表値=1750 request label組、duration35組。全key/type/service・未知以外のcanonical値 |
|003 / httpMetric003|10,000異なる合成route/methodもrequest1組/duration1組、query/ID/制御/username/absolute pathのcanaryは返却mapへ出ない |
|004 / httpMetric004|nullとunknown metric/mode/status99/600、status100/599境界、Labels三null不変契約・固定診断に元入力を含めない |
|005 / httpMetric005|label maps/allowed label集合/route metadata/9bucketを変更不可、両metricだけが許可される |
|006 / httpMetric006|64並行classificationで同固定map・所有executor終端、実service/DB/sleepなし |

新6通常PTを一固定sourceから実行し、当6実行class＋metadata1のCRC/単一session/四counter100、親Enforcer/lint/Werror/NullAway/SpotBugs/Checkstyle/PMD個別適用性を検証。全Webや既Batch73のcoverageへ合算せず、Production実Jarの当class同byteを独立確認する。全体451/同source全scope/正式1964-53/実NK CHR/native/QA051final/HOLDは維持。境界期待は上記literal/独立goldenから作り、新Production parseでexpectedを生成0。実環境/command/source/結果/hashは1571以降へ。

## 2026-11-22 現候補の合成routeと有限並行

httpMetric002／006。固定35行×10method×5状態級を当resourceで実測。4workerの64fixtureと終了制限を保持し例外契約だけを限定。選択2成功、該当広域例外0、同試験JVM実命令一致。Main・実HTTP・全451はこの選択に含めない。BUG-3563/3564、YKT-2803。evidence/01_PT/018_NK-OPS-001/evidence/PG42194-f03-web-http-metric-bounded-current-v1/manifest.json SHA256 570e3dea4ca18b8e7eb783ef679c352c0ea4a3355046b61a19bf9549292b6091。

## 2026-11-22 Web監視値の別fixture

WebMonitoringValueContractTestの固定mode合成試験はPG42198。同fixtureの独立route35行と順序はPG42202／BUG-3565／YKT-2804で1成功、fixtureのchecked例外のみ限定。実HTTPや他の試験の合算は行わず、同候補別結果を保管。evidence/01_PT/018_NK-OPS-001/evidence/PG42202-f03-web-monitoring-route-fixture-v1/manifest.json SHA256 3df55341bb17799d8e388aac57fbc1eae87b29e6cdfb64556ebae431fe16c287。
