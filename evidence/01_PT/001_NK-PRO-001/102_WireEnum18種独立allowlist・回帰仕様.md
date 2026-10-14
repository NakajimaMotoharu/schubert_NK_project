# WireEnum18種独立allowlist・Protocol回帰（YKT1010）

NK-PRO-001/ProtocolSemanticTypeTest.approvedEnumNamesWireValuesAndConversionMatchIndependentDesignTables/PT-PRO-001-T04、485主担当WBS-P002-01、共通headerのP001-01は別主担当・参照費重複0。UI234（Game/Entry/Voice/Delivery）、UI235（Disposition/Pair/Animation/Video）、UI236（Role/LogType/LogLevel/User/Question/Notification）、SS333§8（MIME六値）、SS351§5（通知error五値）を独立literal name=wire tableへ転記した。

各enumの宣言件数/name/wire、required/optional decode、FieldValue encodeはliteral expectedを使用。未知UNAPPROVED_CANARYはrequired/optional共にLayoutValidationExceptionを要求。Java nameは承認wire意味に対応する内部型名を固定し、wire許容集合はUI/SSを正本にする。元generic enumValue往復は補助converter契約のみで承認集合oracleへ加点0、既source/Main変更無し。18type合計のliteral数はtest inputから集計し実結果へ記録する。

PG2634の実Protocol通常回帰：expected82PT/17suite/174Main/static0・FES-flaky-skipped-notrun0・line/method/class/branch全100、全Main/resource Jar memberは既actual2620と同byteを要求。command固定PYTHONPATH pg2634_protocol_oracle_regression_test.py→clean固定→pg2634_protocol_oracle_regression.py。Main/a79/VM/Root/Backup/ADMIN不変更、旧81件へ新一件を算術加算して合格化0。合成反例proofは別2630/2632でPT/coverage加点0、semantic18typeのmutation/consumer横展開と全六正式統合は未完。group0690費0.5/1.5/4pp/原v3不変更、個別実費N-Tnull。

v1/session33025 actual1/TestSource3b7e244c5/payloadcd6ebd36：親pomの全module graphをProtocol-only archiveへ解決できずMaven project collectionで拒否、JUnit未実行。元slot/logを保持、v2は親graph全source・上位原文とnk.pt.repositoryを固定入力に含めるが-pl選択はProtocolのまま。試験期待82/17/174・static/counter/byte条件は不変更。
