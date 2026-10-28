# 2428 Systemd Test 重複literal21件・製造静的確認結果

2026-10-28、2427/PG-D780/BUG2035/YKT1783。Production source41359340de234b8bea7578d957bcbf4df6ab951f（当Test一fileのprivate String21だけ、Main不変更・未配備）。既20 Test methodは変更なし、新Test ID/新physical0。動的PT NOT_EXECUTED_HOLD、coverage NOT_MEASURED、実行免除・代替PASSではない。

|工程・元owned session|公開manifest（`evidence/provisional/`配下）|SHA256・真正終了|
|---|---|---|
|原本修正前保存|PG13190-systemd-test-literal-originals-v1|9159076b27e5b090f8aa550402456d51d90daeb5790d84836fe74f113309457b /0|
|全文逆/24反例・PMD/CS、95878|PG13192-systemd-test-literal-preflight-v1|1a7db1f6a6db5b41a8c61119b98825cd1cce173fa6eab50c050f91557e6066f1 /0|
|固定source六normal、73443|PG13194-systemd-test-literal-six-compile-v1|6c6809515a4ae056dad337e44b5ffd8e26b617e0292e88df7082b3ddcddea1b9 /0・PT0|
|六SpotBugs、86228|PG13196-systemd-test-literal-static-v1|34746d45558149ae8cf2eb13d460628c7d518b6c8b13e0c9770afcf58028a253 /0・PT0|
|独立全物理/ABI、18208|PG13198-systemd-test-literal-post-v1|3f52f5b1beea8cac7407c7ed5a2fa58af0a9dba7d6225162ce8ab95499e9e35d /0|
|当SHA一registry、83241の第一entry|PG13200-systemd-test-literal-trace-v1|14eeb898ff39831293d062df06e2a081220a001ac5fc929705fdcb88fbbd3ea5 /0|
|WBS独立/八反例、同第二entry|PG13201-systemd-test-literal-trace-post-v1|0bc35249198d2bbc6775b16d97f84ae4b6a40e7e700c500754c9c984973b5f47 /0|

## 確認した成果と未確認事項

- 元40raw中AvoidDuplicateLiterals21だけ消滅、他19は原rule/class/method/message・columnを除く位置非依存signatureで一致。PMD自身は残19のため終了4、raw gate1を保持。Checkstyle0、六SpotBugs0。規約の抑制/除外追加なし。
- 元全文に対するprivate21宣言除去/全参照展開のtoken完全一致、定数21値・assert・境界・終端の24非同値反例を拒否。独立期待値は元fixture literalのままでProduction定数へ共通化していない。
- 全1843Main同byte、Test1974 keyset不変、当SourceFile三classだけ変化・他1971同byte・新physical0。三class全method形状不変、外側private String21のConstantValueだけ追加・他全private/public metadata一致。匿名一classはrawCode同/debug差だけ、外側/CallsはrawCode表現差がある（CP indexを含むため意味差の証明ではない）。source全文逆と正確な定数metadataを別根拠として併用。
- registry995の当Test SHA一だけ更新、他994row・全canonical owner/cost/旧runtime/unknown二/論理941歴史943/原見積を不変更。原raw8438=Main1502+Test6936、累計原是正987、用途参照3271/current-source再照合pending976（当変更で既Thread参照一を追加保留）/参照なし5167。全体違反件数null、全WBS audit1/HOLD、F03/451未受入。

LinuxSystemdSessionTestの既native/FFM/library/資源処理を実行していない。BUG2035/YKT1783は当PG・静的確認済だが動的再試験HOLDのため全面完了ではない。元source80baの9PT/codec四100を当sourceの実測へ転用しない。正式1964PT/53scope・歴史17/190・新受入0・工数率null・QA051final保留を維持。

## 費用・再開

群2794開始、原1/3/6pp・cap10、共有5→6（同reset1793774153、他chat込み・専有費null）、実tokenN/Tnull。新工具bind後失敗0、source追加再試行0、当PG原是正21を新leaf受入と混同しない。事前authoringで無意味な余剰guard一を実原診断との集合一致へ置換（bind前・製品再試験なし）。used10次点検・残10以下/不明停止。保存/pushは最新456を参照し、通常区切りで停止せず次の独立PG/PTへ進む。
