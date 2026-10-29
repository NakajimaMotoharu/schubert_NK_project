# 2717 Scenario詳細・Music階層 元whole20 単体テスト仕様

Production source6b53efeec87f3ec36a840dd8e7759656cb4aee5c、branch dev-foundation、Git15a9174741f2fc7afac35ac3d8450ed007b0ca83。NK-WEB-001/FUN005/006、UI234/235、SS313/323/333、PG-D923。対象三Mainと元ScenarioDetailViewModelTest全430行12件・MusicHierarchyViewModelTest全355行8件を全body、必要Protocol DTO/実enum/validator/semantic helperも全body確認済み。Main/Test/fixture変更0。

|Test ID|独立した期待値・観点|
|---|---|
|WEB194～205|INLINE/FILEの実DeliveryMode二値、前後id/title組、200/201、FILE metadata件数1/10000/0/10001と実records不一致、連続entry/audio順・重複・同entry属性不一致、null、immutable/closedBean/redaction、固定percent href/text/合成DOM、自己64task/8thread/10秒|
|WEB246～253|元API順category/sectionと手書き129合計、20/21・100/101境界、件数不一致・重複・empty/dot segment拒否、null/immutable/closedBean、固定Unicodeとpercent予約文字、合成DOM・自己64task/10秒|

期待は手書きliteral、明示件数・入力表・独立DOM値。Production methodでexpectedを生成しない。FILEは型付きmetadata fixtureのみで実file open/hash/read、large-result受入ではない。StringTemplateResolverはメモリ内文字列のみで実template/Browser/HTTP/API/DB/JMS/VM/Root/graph/cohort/鍵操作なし。語だけでなく全bodyの副作用を確認した通常元whole初回試験であり、拒否操作の抽出・代替経路ではない。

対象ScenarioDetail四physical、MusicCategory/Section各二physical、三Source全八code closureをnormal14216同一source Jar/byteで固定する。Main canonical owner P01607/11/12、元二Test UNKNOWNを保持。依存helperは当target coverageで別Source合格へ加算しない。環境は元own JVM prefix、JDK25.0.4/Platform1.13.4/JaCoCo0.8.15、外側180秒。PG14596 checked entryで一回実行→PG14598独立XML/FESnotrun/終了・一session/CRC/八metadata反例・全input/静的14224・各Source四counterを照合。未達/自然branch0はそのまま残す。

着手前event3107予定 .5/3/6pp cap10、primary P01607・component11/12追加費0、専有消費不明/N-Tnull。結果2718へcommand/実行時刻/環境/source/hash/coverage/期待対実際/関連障害を保存。正式1964/53、歴史17/190、工数null、QA051final、全F03/451/HOLDを変更しない。未実行は合格にしない。
