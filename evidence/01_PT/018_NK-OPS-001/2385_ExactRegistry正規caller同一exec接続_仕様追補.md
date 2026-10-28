# ExactRegistry正規caller同一exec接続 仕様追補

2026-10-28 / BUG2003-YKT1751 / 2383親群2/5/8cap10内・追加予算0。source0124b5938a50f4ceea542486c336ba12146cb1b4を維持、12819normal/六SB12820/原10成功を保持する。12822真正1はcoverage未達（outer22L6M1C13B/miss1L1B、inner23L7M1C10B miss0）、PT失敗でも100でもない。旧exec/全readerstdoutから12823でpartial独立測定を保存し、同Product試験の確認再演はしない。

必要追加は既whole DbQueryDurationMetricRecorderTest全488行/九Testだけ、従来原10と合わせた新19/二suiteを一execへ含める。26Mainは同hash既読、SDK own registry/時計stub/固定scalar duration/recordersでSQL/実DB/JMS/ネットワーク/FS/VM/Root/native/鍵/権限を操作しない。Query parserのSQL風Stringは未知enum値negativeで実行先無し。Fixtureは独立文字列四series/五bucket/0・1ns・MAX/Golden2.000000001/固定count・sum・max/例外同一性とownercloseを検証、Productionをexpected生成に使わない。

dbTime001～009：四固定series/正規互換constructor、独立秒CDF/MAX二回、closed parser/enum防御copy、null/負/未知mode/STD未記録、部分factory失敗、record前後failure非補償、八worker/64有限taskの入力から独立算出したcount/sum/maxと別registry不干渉、foreign counter非上書き・非close、大小極端値二順。007のinvokeAllとTWRには局所絶対deadlineがなく、Future.get5秒/外JVM240秒と区別する。原helper/9method/assert/TWR/finally不変更、新Test ID0。

PG12837同source plan→12838 new-only whole19→12840追加Testを含むPMD-CS（Main二＋Test既存Thread/map適用性raw保持）、同source六SB12820をbyte証明で参照→12842独立全XML/CRC/全1843Main/1962Test/単一exec全六artifact/registryouter-inner→Main二と全Thread/mapの現source文脈/独立反例/元983owner/集合を閉じる。normal snapshot・依存・全source不変でなければ再利用しない。旧10＋別9のexec union禁止、全artifact/451/正式受入は別・安全HOLD保持。結果2384へ。
