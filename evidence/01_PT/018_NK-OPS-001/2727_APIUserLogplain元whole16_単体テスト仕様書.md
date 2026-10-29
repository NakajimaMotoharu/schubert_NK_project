# 2727 API User/Log plain 元whole16 単体テスト仕様

source6b53efeec87f3ec36a840dd8e7759656cb4aee5c/dev-foundation/Git8862a514ccacf8c97b383a23007dfbf341155a3b。NK-ADM-001/NK-MSG-002/FUN008/009/MQ006～010、UI235/236、SS323§9.4-5/324/332、PG-D928。原Core4/157行・Response4/172行・LogPlain8/238行、二MainRequest全body、CanonicalField/Request/Actor/Role/必要Protocol DTO/enum/helperを全body確認。元2008/2012/2016のPT_DEFAULT独立性・golden期待根拠も照合した。新fixture/held Testからの抽出や拒否操作の改名ではない。

UserQueryRequestTest463は@BeforeAllの実ApiLogDatabaseFixture/実DB、鍵HMAC/close後assertを含むため全class動的HOLD、部分抽出0。今回別の元三classは非null repository/connectionを構築せず、queryは全nullだけで最初のnull拒否に停止。canonicalはplain fieldと通常caller-scope cleanupのみ、鍵/暗号/HMAC/進行中close/消去後参照/並行close0。Root/Graph9/VM/DB/JMS/HTTP/私有raw/実ログ/原本/鍵操作0。

|Test ID|独立golden/入力/期待|
|---|---|
|ADM-CORE001～004|96/12byte hand wire、Équipe/ADMIN/ACTIVE又はoptional space、owner7/8・固定五field/一field順とX1/N1・ASCII1/50/3、unknownZZZREQ01固定拒否、redaction、canonical(null)/query全null拒否|
|ADM-VAL001～004|USR固定offset77/page-size1/50、emptypage受理、page0/size49/行数不整合の型別拒否、UDT target3/4・layout/data型不一致、nullは別契約|
|LOG-PLAIN001～008|656byte、offset0/256/272/336/592/600/617/634、七optional全128maskと独立names/types/UTC値、655/657/unknownEnum/不正月/page0/reserved拒否、response clamp/原page999999保持・layout/type/page-size/件数拒否|

expectedはSS/UI offset/長さと手書きUTF8・固定日時差・bit表から生成し、Production encode/canonicalでexpected生成0。128maskをTestID128件へ水増ししない。今回初回当source16method/3suite、Main/Test/fixture変更0。二Main canonicalP01001/P01809、元三TestUNKNOWN、全pathを明示table/module/package/normalhashへ事前固定、両WBS実leaf確認済み。

群event3118予定 .5/3/6pp cap10、primaryP01001/componentP01809追加0。開始event実0を確認してから14630 checkedentryでwhole16を一回、14632が独立XML/FES/真正終了/原ownENV/全input/六Jar/static14224/一CRC/八metadata反例/二Source全closure/counterを照合。query正常/その他未呼出条件はcoverage不足のまま記録し、人工到達/除外/他exec合成0。JDK25.0.4/Platform1.13.4/JaCoCo0.8.15・outer180秒。結果2728へcommand/time/source/環境/hash/実際/不足/BUGを保存、全正式/工数null/全F03-451/QA051final/HOLDは不変。
