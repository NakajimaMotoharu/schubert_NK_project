# 1295 API管理stop：修正前の真正反例

1294/SSC313/PG-D462/BUG1547/YKT1307。red Test snapshot **506a901c6703e87727219a6ad46758701887573a**、Production Mainはacbから全不変更。当compiled ApiManagementServer.class SHAは資格済みacb全体の同classと一致した。既期待値/原Current/解析/build不変更、新Testのみ。

元69294/pg6128-api-management-stop-red-v1、2026-10-20 17:37:18.453261Z→17:38:26.390686Z、phase[0,1]/Maven1/真正exit1。実14件/6suite、failure1/error0/skipped0、13成功は限定実行結果であり合格gateではない。expected20/9のうち後続reactor6件/3suiteはnot-runで合格へ加算0、APIが失敗したためAPI/Web/batchの後段static/reportも未完。manifestの欠測target counter {0,0}を実測0%/100%と解釈しない。

失敗Test=ApiManagementStopTest.apiStop001FailedStopNeverMakesLaterCloseAFalseSuccess。最初のstopは同一marker Runtimeをthrow、readyはDOWN、次closeは本来stop再試行2回目の期待に対し実1回。JUnit assertion `failed stop must be retried by retained owner ==> expected: <2> but was: <1>`。stop前closed確定により次closeがno-opとなる実反例を検出した。fixtureはfinallyで実delegate stop0/own executor actual joinを完了、既サービス/VM/DB/Root/failed-cohort操作0。

WorkPG379/pg6128-api-management-stop-red-v1/begin.safe.json SHA **1f53aa8fc025b165f1764042ce451b428a594f2931229bf1c09952d9096c5ac3**、source.tar **e606f9b2c62d3e28f026b7f72bf48c72dcd531e9e536a38ef9eeec3161b4f4c3**、manifest.safe.json **b8a6c36322a48cc79571999000809bb745e77176f27d1fedcae9f80007afc2a5**、当一原XML SHA **3d3be76baf3b036d66a8c1425ec8d7ffc090012e5c925317020a1454fa85ea4e**。実commandは462PTPRE037/pg6128 tool、既JDK25.0.4/Maven3.9.12/通常six-format先行・self-owned loopback fixtureだけ。raw XML/logはGitへ出さず私有保持、必要な値/hashだけ本記録。

このredは障害再現でPT PASS/coverage/代替確認には加算0、元失敗は保全して再演しない。次はMain一件だけのstopping/stop確認/actual join/closed完了・deadline/割込/phase再試行をPGし、既7Test＋新四境界Test＋guard12の当宣言23/9をgreenで検証する。関連S2/S3のAPI親/既JMS/factory保持は未完、YKT1307を一件だけで完了扱いにしない。
