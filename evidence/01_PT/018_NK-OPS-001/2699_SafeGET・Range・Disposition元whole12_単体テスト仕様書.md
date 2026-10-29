# 2699 Safe GET・Range・Disposition 元whole12 単体テスト仕様

source6b53/dev-foundation/Git4d6ea191ae12b2d0c65832e72010483604e6e9ec、PG-D914、PG14534/36、event3089・.5/3/6pp cap10。Program NK-MED-001/NK-WEB-001、RD FUN-005..007/PER-004..006/AUT-001..004、UI221/223/226/235/237、SS314 §7/352 §3/333 §9-10/323 MEDIA1024。PT_DEFAULT。

元SavedRequestTargetTest4・HttpByteRangeParserTest4・ContentDispositionFactoryTest1・ContentDispositionBoundaryTest3の全body/初期化/依存を確認。target MainはSavedRequestTarget・HttpByteRangeParser・ContentDispositionFactory。Parserの全5physical（Full/Partial/Unsatisfiable/Selection含む）、他各1、計7physical6Code1noCode interfaceを分母に明記し、手動除外しない。MediaDescriptor/Validator/MediaType/ContentDispositionは全body確認済み純値依存、これらの別元20等counter成功を当試験へ合成しない。

|Test ID|独立literal/操作/期待|
|---|---|
|WEB005|safe GETのpath/query/日本語/encoded query等をそのまま保持、固定redaction|
|WEB006|null、非GET、相対/外部/fragment/backslash/CRLF/controls/dot segment/不正encodingを拒否、固定例外/cause無|
|WEB007|UTF8 2047/2048受入・2049拒否、681日本語/不正surrogate/補助文字|
|WEB008|10thread100task、個別固定target/20秒get、cross-state無し|
|PT-MED001|手書きinterval table、最初のrangeだけ、1MiB cap、suffix/leadingzero/空header|
|PT-MED002|grammar/非正size/逆順/ゼロsuffix/decimal overflow/Long加算overflowはUnsatisfiable|
|PT-MED003|nullとFull/Partial constructor境界、Long.MAX単byte/1MiB正確性|
|PT-MED004|8thread100taskの偶奇interval oracle、局所invokeAll/get無期限とownJVM180秒上限を区別|
|PT-MED005|RFC5987の独立percent literal、日本語/空白/予約文字/256byte境界、null不正metadata拒否|
|HEADERBOUND001..003|ASCII/予約文字/補助UTF8/%をdecodeしない/63補助文字+拡張子受入・64拒否、両mode|

URI/ヘッダ文字列・数値だけを扱い、実HTTP/redirect/認証/任意file/Media配信/DB/JMS/VM/Root/鍵/cohort/graph9は0。公開dummy file pathはデータ文字列でFile APIへ渡さない。Productionからexpectedを生成しない。元Test/Main/Fixture変更0、新TestID0、Mainowner P00904/P01502・四TestUNKNOWN維持。

commandはchecked Python entryで14534、独立14536を各一回。normal14216・static14224・六Jar/全input固定、fresh元whole選択12/4・XML/FES/終了/一execCRC/原OS-JDK・全closure/coverageを実manifestで照合。不足を100へ補完しない、旧source/別exec/旧PT転用0、formal/wholeF03/451/工数更新0。結果2700へ。
