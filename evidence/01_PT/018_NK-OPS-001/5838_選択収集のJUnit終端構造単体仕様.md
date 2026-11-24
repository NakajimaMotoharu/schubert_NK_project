# 選択収集のJUnit終端構造単体仕様

品質工具NK-OPS-001、RD TST-101、SS354、451、WBS-F03/2-2-b。BUG-3807／YKT-2965。対象は030～033の選択収集と、元reactorの `pgpt_reactor_junit.validate_passing_surefire_suite`。既存の選択Test ID、method、class、件数は維持する。

PT-QA-JUNIT-SCOPE001は各parserへ一件の合成テストを渡し、正規testsuiteと明示0、正規properties、文字列標準出力、既定class・methodで受理することを確認する。失敗・エラー・skipの各属性欠落、整数表記00、異root、未知の直下要素、標準出力内の子要素、properties二要素は、各独立入力で拒否する。期待値は固定Surefireの構造と451成功条件から設定する。

元のreactor収集は既存のsource/run/hash・重複試験確認を維持する。実テスト、JMS、DB、外部ログまたは安全保留の操作を必要としない。
