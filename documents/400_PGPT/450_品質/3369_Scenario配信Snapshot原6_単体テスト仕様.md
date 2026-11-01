# ScenarioDelivery/Snapshot 原whole6 単体テスト仕様

2026-11-01 / PG-D1082 / PG17290-SCENARIO-DELIVERY-SNAPSHOT-ORIGINAL6、source6b53・開始HEAD71ea2e6b94378597801d319b8b04bcb873fe5d8a/dev-foundation。事前2/5/9共有pp cap10・主F03/元canonical維持、freshused73/rem27。開始前に両名のfollowup index（各0）と現2655 registryを確認、対象Main二つ/原suite二つは未登録。index0だけを許可・未実装と推定しない。

## PT_DEFAULT・全sourceと依存

ScenarioDetailDelivery全class・ScenarioDetailSnapshot全record・原DeliveryTest3全本文/byte helper・SnapshotBoundaryTest3全本文/records/entry helper、ScenarioFilePublisher interface全文を読了。Deliveryは200以下memory INLINE、超過時は注入publisher一回→descriptor投影だけ。実Publisher実装を作らない。SnapshotはList.copyOf/INLINE shape/最大10000/元codecとsequence検査で、DB接続やfile I/Oなし。下位PayloadCodec/PayloadTypeCatalog/semantic DTOは同6bの既Source資格を補助根拠として使い、旧成功を新原6へ転用しない。

原TestはInstant/UUIDの固定値、手書1728byte metadata/4800byte record golden、元publisher lambda/AtomicInteger、memory Listだけ。hash=a×64はdescriptor投影fixtureであり実content hash oracleではない。crypto・乱数・Thread・Files/DB/JMS/Root/VM/native/権限/鍵・原本Backup/permit/intent操作0。旧Test CP/新fixture/元whole切出し0、freshcompile全二suite6method/一exec。二package application.scenario/persistenceはmodule api配下の実pathで拘束し、prefixやTest pathを暗黙に同一化しない。

|Program/class・Test ID|原method|正常/境界/異常と独立期待|
|---|---|---|
|NK-SCN-001/ScenarioDetailDelivery・PT-SCN-008-R01|r01ZeroThrough200RecordsStayInlineAndNeverPublish|0/1/199/200 recordsはINLINE/publisher0。手書SCNRSP01 DATA1728/record4800の全byte、header込み1984+count×4800<1000000、immutable records|
|同・PT-SCN-008-R02|r02Above200PublishesOnceAndProjectsEveryFileDescriptorField|201/10000はpublisher1/同records/time、FILE DATAのUUID/path/byteLength/hash/recordLength/countを手書offsetへ投影、wire records0、元snapshot INLINE/件数保持|
|同・PT-SCN-008-R03|r03NullPortFailureAndMismatchedDescriptorNeverFallbackOrRegenerate|null publisher/snapshot/time/descriptor拒否、publisher IOは同一instance・一回、count不一致は固定ISE/再生成やfallback0|
|NK-SCN-001/ScenarioDetailSnapshot・SNAPSHOTMAX001|snapshotMax001MaximumRowsRemainImmutableAndKeepLastRecord|10000行とfirst/last ID/sequence/line/body literal、caller mutation/clear後もsnapshot保持、同metadata参照/immutable/toString固定|
|同・SNAPSHOTMAX002|snapshotMax002InteriorAndTailSequenceGapsRejectWithoutChangingCaller|index201/5000/9999のsequence一差分→LayoutValidationException、caller size/同bad object/入力不変|
|同・SNAPSHOTMAX003|snapshotMax003TailTextPastWireBoundRejectsBeforeSnapshotEscapes|最後行4097文字→FieldEncodingException、先頭/入力末尾/size不変、Snapshotを成功返却しない|

golden DATA offset：0:id12/12:game12/24:title256/280:path512/792:prevId12/804:prevTitle256/1060:nextId12/1072:nextTitle256/1328:mode1/1329:UUID36/1365:relativePath256/1621:bytes12/1633:hash64/1697:recordLength6/1703:recordCount9。record offset：0:id12/12:sequence6/18:line8/26:type/164:body/4260:voice count3、paddingはASCII space、numberはLocale.ROOTの独立固定桁。expectedにProduction encoderを使わず、Production encoderはactual wireの取得側だけ。file実体/保管/Range/owner/再送/DBcommit/実並行/CHR受入は別programに残す。

RD FUN004/005・FIL001～009は関連、UI234§10/237、SS332/333と実publisher責務を分ける。byte offset/上限は正本と後続固有traceで照合する。新Program製造/Main/Test/SS変更0。17289 plan→17290 raw→post/独立を同source/session/execへ拘束し、全二Sourceの全physical/四counter/静的14224元証拠/held・native probe/原TestCRCを確認、未達はmissのまま記録する。Snapshotの未試験shape/件数超過等を到達不能へ分類しない。原6成功だけで全条件/全Program/451完了を宣言しない。

OS/JDK/branch/commit/argv/時刻/終了/XML/FES・aborted・container0/入力期待actual/coverage/path/hash/BUGを各manifestへ。Shared枠の整数差0を専有費0としない、原予測/v3～v5/正式1964PT53scope/17of190/工数null/QA051final/全HOLD不変。通常小群/commit/PMO待ち停止0、fresh残10以下/取得不能で保全。
