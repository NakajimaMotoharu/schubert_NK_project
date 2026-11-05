# Command metadata 非null・非表示単体仕様

Program NK-QST-001 / QuestionCommandMetadata全record / SS332/351・PT-QRY028/NTF012・411/451・796。原部分80リストの最後のtoString未通過とnullablecaller契約を補う小部品の通常PTで、代表Vには数えない。

|Test ID|class/method・入力・独立期待|
|---|---|
|PT-CMD-META001|QuestionCommandMetadataContractTest.everyMissingTraceFieldRejectsAtConstructionWithoutNullNormalization。messageId/correlationId/at各nullはconstructor NPE拒否、固定field診断だけ。Objects nonnull caller契約で、productionがNPEをcatchして正常化する実装なし。|
|PT-CMD-META002|同renderingIsConstantForDistinctTraceValuesAndCannotExposeIdentityOrTime。異なる固定UUIDとUTC1970/9999 metadataでtoStringはliteral「QuestionCommandMetadata[REDACTED]」のみ、getterは入力値を保持。expectedをSUTの表示/日時計算から生成しない。|
|PT-CMD-TIMEBOUND001|既QuestionCommandTimeBoundaryTest.lowerBoundPreservesFloorWithoutRounding。0001-01-01T00:00:00Zと+999nsは下限µs、-1nsは拒否。|
|PT-CMD-TIMEBOUND002|既upperBoundAcceptsSubmicrosecondTailOnly。9999-12-31T23:59:59.999999Z/+999ns許可、+1000ns拒否。|
|PT-CMD-TIMEBOUND003|既preEpochTruncationUsesUtcFloor。1969末999999999nsは999999µs、1970+1nsはEPOCH、message/correlation保持。期待は独立literal時刻でSUT.truncateの再利用なし。|

新Test2＋元境界Test3全class/全5methodを同sourceで実行する。元Test/Main/仕様は不変更、元exec合算・成功確認だけの反復なし。FixtureはUUID/Instantだけ、実DB/JMS/crypto/key/credential/session発行/Root/file/native/VM/network0、HELD四class非到達。Mainbuild/NullAway/六SBはPG18642/18648同b093全input/JARhash一致で再利用。PG19000compile0/PG19002static後source固定、PG19008正常APIjar/全5/2class/単exec-session/正常Mainphysical1/CRC/四counter100/HELD4zeroを独立post。終了枠はfreshUTC時刻>=postをassert。結果/実時刻/OS-JDK/argv/source/exit/hash/BUGは012へ。個別WBS/業務更新/通知/owner/token/HMAC/正式451/V/IT-STは未受入。
