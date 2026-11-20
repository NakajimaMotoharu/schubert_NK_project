# JDBC／JMS実装型を対象とする依存監査単体テスト

NK-OPS-001、SYS-005／007、SS311 §2/3/5.2、WBS-F02-a、BUG-3388／3389、YKT-2723。JDK25でコンパイルする独立の型名fixtureにより監査工具の静的ルールを検査する。

| Test ID | 合成経路 | 独立期待 |
|---|---|---|
| PT-F02-VENDOR-001〜004 | Storage・ProtocolからPostgreSQLまたはArtemis実装型へ直接参照 | 既存FRAMEWORK_FENCESで一件ずつ報告 |
| PT-F02-VENDOR-005・006 | Web Controllerから同実装型へ直接参照 | 既存CONTROLLER_BOUNDARYで一件ずつ報告 |
| PT-F02-VENDOR-007〜010 | Bootstrap移行JDBC、Batch管理Artemis、API JMS adapter、Web session JDBC | 上記の禁止境界の指摘0 |

合成stubはcompile時のみ使用し監査入力JARに入れない。実transport・JDBC driver、製品JAR、サービス・実DB・brokerは起動しない。修正前は独立した10検査、修正後は同10と既Repository・Controller等45の全出現集合、旧78物理のSHAを照合する。監査終了1は明示禁止fixtureの期待結果。試験の合格を製品のF02・coverage・451へ加算しない。

実行は `python3 -B evidence/01_PT/018_NK-OPS-001/input/5383_f02_vendor_jdbc_jms_boundaries.py before|after`。原run PG40572、修正後 PG40574、独立照合 PG40576。環境、command、真正終了値、入力とTest ID別結果、class数はmanifestに記録する。
