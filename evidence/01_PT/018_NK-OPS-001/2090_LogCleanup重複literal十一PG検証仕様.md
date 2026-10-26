# 2090 Log/Cleanup重複literal十一PG検証仕様

2026-10-26、BUG1850/YKT1601、基点source095720ee2766cd9f0bd441ee4bc019833fde8184/PG10598正常。主責P01004/P01707、変更管理F03参照は追加費0、群開始1/3/7週次枠pp/cap10、専有費/実token null。

LogQueryApplicationServiceTest（NK-API、ADM067..073、原source trace/SS352/各class既annotation）：0000成功13、0200冪等成功12、0103権限拒否4、Inbox count SQL6、none故障未設定4、vm://0メモリbroker URL4、database故障point5＝七定数48参照。CleanupStepRepositoryTest（NK-BAT-001、BAT162..169、OPS009/DAT009/UI251/SS331§3.14/332/341）：step_target_count/step_success_count列、question id2 count SQL、row.close故障point各四＝四定数16参照。

PG1850-LITERAL001～011は上記順、製品PTの追加Test IDではない。元fixture literalが独立expectedの根拠、結果code三は承認UI232§7の固定値も照合する。Production enum/getter/DB結果からexpectedを作らない。十一の新Test-local定数を追加しString token64だけ置換、他全token/元assertion/SQL/wire/fault sequence保持、Main0変更。未知/誤値/参照欠損/他assert変更をmetadata反例で検出する。

前提=基点正常source全入力SHA・明示二fileの一致、既job終端、元全成功の再演0。操作はsource/metadata/静的のみから開始、pyflakes0、独立逆展開token照合、PMD/Checkstyle四元fileで十一指摘消滅・他39全属性保持を確認後、新固定source六正常compile/PT0と独立class/source/traceを照合する。JDK25.0.4/Maven3.9.12/既PMD7.28/CS14.3、source/run/command/exit/hashは同番号manifestへ保存し結果2091へ集約する。

元DB/JMS/故障/key/graph動的PTはNOT_EXECUTED_HOLD、fixtureを別harnessへ抜出して実行0。coverage null/正式1964-53/個別17-190/工数null/QA051final/全安全HOLD不変。全F03の受入や実PT PASSへ換算しない。expectedliteral同値化のPG合否と残39指摘の適用性、全451を分離する。保留二fileは内容accessしない・旧未読保証不明保持。
