# 696 Morning正常WARNING10 単体テスト仕様・結果（host限定）

2026-10-13計測追記訂正：systemd templateの485 owner/costOwnerはWBS-C02。Unit製造と共通Unit PT（PT-OPS-MUNIT001～004/SSC278-UNIT1790）はC02:contract/scope/qualityの限定証拠・主担当共通費一回へ帰属する。0523群開始0.5/1.5/4pp・原event/v3/予算は不変、実費N/T/allocatedPpは未分離null、P018-03.02への再計上0。下記旧P018表記は着手時の分類として保持するが現分類に使わない。Root/FD側の独立PT（PT-OPS-PG1800-PARENT001/002、Root世代host1743等）は各既群の責務を維持し、Unitへの参照費は0。候補0fdのhost4成功を実VM2741のUnit受入へ加算せず、同候補sourceの署名/実Unit/終了依存joinは未完。

Program NK-OPS-001、MorningServiceUnitTest.munit001～004とsystemd親template、SS341/343/SSC278・BUG1162/YKT930、WBS-P018-03.02。Source候補0fd734195（実VM current2741/PG1638は不変更）。Unitの追加行は唯一SuccessExitStatus=10、Java MaintenanceCompletionの承認済みSUCCESS0/WARNING10に対応、他30/50/70/143/signal/timeoutを許可しない。親30min/60s/SendSIGKILL=no・credential/hardening・target子並列禁止は維持。

Test ID=PT-OPS-MUNIT001～004/SSC278-UNIT1790。fixtureは実template byteをreadし、独立literal exact key/value/唯一行数を検証、値をProduction methodから生成しない。正常WARNING契約はTestを先に修正（2bfe600bc）し、旧templateで1 failure/他3成功を確認してから実装。これは既BUG1162の再現兼TDDでありredを合格へ算入しない。

red PG1790（2bfe600bc）：actual1/tests4/failure1/errors0/skipped0、XML SHA6ff9d7fc871906dbba8251cbc5d491c52a19054c29fc228e51a77126c98cc70f。green PG1790（0fd734195）：actual0/tests4/failure0/errors0/skipped0、XML SHA844311847cb4570e9f8bb7ec0642fbe71970ab14ca0c0111c94bfc639cce7139。実JUnit class/method unique4・全started4/aborted0・javac Werror/Xlint0、source/全library/入力byte前後不変。PG1790 driverの正常CLIはred期待再現を記録する終了0だが、actual test exit1は上記通り保持。

実行=固定PYTHONPATHでpython3 -B tools/quality/pg1790_morning_unit_selected.py red / green、hostJDK25.0.4/M2固定JUnit5.13.4/Platform1.13.4、Ubuntu26.04.1/x86-64、branchdev-foundation。新classes/XML/log private slotを個別作成、既target/fixture/VM/DB変更0。全command/日時/libraries/input hash/operator source/終了codeはwork/pgpt-runs/PG379/pg1790-morning-unit-{red,green}-v1/manifest.safe.jsonに保存。

Production Java byteのcoverage計測は本Unit fixtureに適用しない。既full1755/1756の3618成功は旧Test/設定sourceであり、この候補の全回帰へ流用しない。same-source署名/BOM/正規停止配備・実Unit/新PID1 job done/正常10原本/実Root/owned停止/native/451は未実行。親Unitバグのhostコード/PT部分だけ完了、BUG1162/YKT930の実環境/全横展開は対応中。全formal1964PT/53scope/四100は未更新。
