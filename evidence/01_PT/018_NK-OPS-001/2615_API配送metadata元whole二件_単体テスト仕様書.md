# 2615 API配送metadata 元whole二件・単体テスト仕様書

同群の別PG読取scope（実行前固定）：SyncRequestListener全97行/PMD00255、TransactedEventListener全97行/PMD00256、InboundTransactions全94行/PMD00196・00198と二typed failure carrierを確認。SS312/321 SSC319/332のnull/session preflight・borrowed context/attempted→rollback→confirmed・typed terminal/原例外再throwを現Sourceへ束縛、direct Error/fatal通知は登録consumer側の別責務として未実証を保持する。三Mainは旧raw/実PMD観測と現Source byte同一、four context reader-v2/post-v3のcfg/normalを固定6b53/14216へ設定するだけで旧module/解析条件を変更しない。旧raw4を保持しwhole pending/quality false、元broker PTのPASSへ代替しない。14246 review/14248独立postに全原XML/token/owner/source/import hash・guard反例を保存、実際のJMS/rollback/isolating/notify/Root実行0。これらを配送record二件のcoverage対象へ含めない。

着手前2026-10-30 JST/event3002内、Source6b53efeec87f3ec36a840dd8e7759656cb4aee5c/normal14216/PG-D872。群見積0.5/3/5pp cap10の内数。元SyncRequestListenerTestは先頭390/777行を確認した段階で実EmbeddedActiveMQ/ActiveMQConnectionFactory(vm://0)/TempDir/実DLQ/再送・broker.stopを確認、whole実行はHOLD。残387行未読/全bodyレビュー済みにせず、mock部分だけの抽出・新fixture置換をしない。

今回の通常PTは別の既存原whole DeliveryMetadataTest（二method/全file読了）とMain DeliveryMetadata（全file/initializer/lambda/accessor読了）だけ。Sync listenerの代替でもgraph9の再試行でもない。java.time.Instant/java.util.List/数値/文字列/Objects以外のProduct依存なし、DB・JMS・file・network・VM・credential・環境変数・thread・native・permit等の取得/操作なし。元既存Testは変更せず独立JUnit class選択、Reporterは既13728の12自己検証・hash固定版でXML/summaryを生成するだけ。元確認済み全回帰/共有44/旧400を確認目的で再演せず、現Sourceの当完全Source unitを初回独立host資格確認する。

Program/trace=NK-MSG-001/DeliveryMetadata constructor・deliveryCount/transportMessageId/receivedAt・redacted toString、RD MQ-003/006/008～010・UI212/213/231・SS312 SSC153/BUG423/YKT334。Main canonical/cost=P005-03、Testの現canonicalはUNKNOWN/nullのまま、当群change/関連担当をcanonicalへ転記しない。

|Test ID/元method|fixture/入力/操作|独立期待/根拠|
|---|---|---|
|PT-JMS-EVENT-DELIVERY / countsAndPrintable128ByteBoundaryAreNotCapped|固定NOW=2026-10-01T00:00Z、count 1/3/4/5/MAX×ID !・ID:actual-delivery・~128byte。原constructorから各getter/toStringを実測。|入力literalと同じcount/ID/時刻、固定redacted文字列。特に4超をcapしないSS153、expectedをProduction methodから生成しない。|
|同 / nullMissingInvalidAndControlMetadataReject|null ID/時刻、count0/-1/MIN、ID空/空白/129byte/ASCII31/127/非ASCII|nullはNPE契約、他はIAE。文字範囲0x20～0x7eと非blank/最大128、count>=1の独立境界。拒否を正常業務成功としてcatchしない。|

正常/境界/異常/nullを元wholeで実行、外部provider例外/再送/並行はこの不変record・独立scalarには非該当で実JMS機能全体の非該当認定へ広げない。旧独立source責任1917/1526を索引参照し原Source/Test hashをnormal14216へ照合する。

command=python3 -B tools/quality/pg11123_checked_python_entry.py tools/quality/pg14242_delivery_metadata_whole_two_pt.py。新-onlyslot/原normal6b53六Jar/元Test二件/hash3396be3b・既Reporter/hashc9d94f87、通常JDK25.0.4 javac→JUnit/JaCoCo一exec。新Test/graph/fixture0。独立post14244で実XML/終了F/E/S/未実行0、全Source六Jar/原Test/SDK、単一session/CRC、DeliveryMetadata完全Source一physicalのline/method/class/branchを測定。自然0やmissがあれば未達保持し、coverage目的の追加人工呼出/手動除外をしない。元record生成filterは既JaCoCo標準不変更。compile/実行失敗時は元結果を保存、必要障害を修正前起票。

結果2616へ日時/OS/JDK/tool/branch/source/実command/exit/XML・exec/coverage hash/actual/assertion根拠/関連BUGとHOLDを記録。正式1964/53・個別17/190・工数null/QA051final/F03・451/元DB・broker・graph等HOLD/原本保全・二held工具metadata前除外を維持、Product2成功だけで全PGPT/IT/ST完了とはしない。
