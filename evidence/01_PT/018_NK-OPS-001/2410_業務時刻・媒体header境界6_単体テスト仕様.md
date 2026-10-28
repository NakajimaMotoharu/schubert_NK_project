# 業務時刻・媒体header境界6・単体テスト仕様

群BUSINESS_TIME_HEADER_BOUNDARIES6_V1/event2775、原2/5/9pp cap10・共有85残15、主担当WBS-P011-03/関連P009-04追加配賦0。Main担当は元logical行を実lookup済み。新whole Test二つ/各3件だけ、既DBを同居するQuestionCommandServiceTestのnull/Instant.MIN/MAX/redactionケースの抽出・複製はしない。元ContentDispositionFactoryTest一件の再演もしない。

| Test ID / method suffix | 入力・操作 | 独立期待 |
| --- | --- | --- |
| PT-CMD-TIMEBOUND-001 / lowerBoundPreservesFloorWithoutRounding | UTC0001下限と+999ns、下限-1ns | 下限へmicro秒切捨て、下限前は拒否 |
| PT-CMD-TIMEBOUND-002 / upperBoundAcceptsSubmicrosecondTailOnly | UTC9999末尾.999999と+999ns、次の1μs | 前二つは同最大micro秒、年10000は拒否 |
| PT-CMD-TIMEBOUND-003 / preEpochTruncationUsesUtcFloor | epoch前後各1ns | 1969末尾.999999と1970開始.000000、Message/Correlation値不変 |
| PT-MED-HEADERBOUND-001 / asciiAndReservedCharactersHaveLiteralEscapes | 安全文字列と~!#$&+^`|*% | 固定ASCII fallback・表記固定の独立%HH literal、+をspaceへ混同しない |
| PT-MED-HEADERBOUND-002 / supplementaryUtf8AndLiteralPercentAreNotDecoded | 二𝄞.ogg と %2F.ogg | E4 BA 8C/F0 9D 84 9E固定byte、%は%25で再escape・slashへdecodeしない |
| PT-MED-HEADERBOUND-003 / supplementaryNameLimitIsByteBasedForBothModes | U+1D11E×63＋.ogg=256byteと×64=260byte、I/A | 63の全UTF8四byte系列を保持・modeだけ差、260byteはdescriptorで拒否 |

関連SS332/351のUTC micro秒・0001～9999、SS333§9のfilename* UTF8/固定fallback・256byte・SS323 MEDIA1024/UI235237。時刻expectedはUTC literal、header expectedは表のUnicode codepointを独立UTF8展開したliteral。productionをexpected生成に使わない。入力はpublic固定UUID/合成名/path/hashでありraw session/key/token等ではない。

新Test/Main直接closureはQuestionCommandMetadata、ContentDispositionFactory、MediaDescriptor、MediaDescriptorValidator、MediaType、ContentDisposition（六Main、全source本文確認済み）。JDK value/time/文字列/URL encoderだけ、fixture/support追加なし・実FS/HTTP/DB/JMS/Root/native/Graph9/crypto/環境・process操作0。Source固定後の正常六module compile一回→当源全6/2/JVM240s→局所PMD/CS・六SB→同一exec独立counter/CRC/全Main旧Test不変・新二physical→Program011/009別索引/trace。未測定を100%にせず、既held元Testの成功を合算0。新nullケースは当新scopeへ移植せず既HOLDを保持する。Result/coverage/manifest hash/未実行分は2411へ残す。
