# NK-PRO-001/002 独立64上限・匿名Log仕様

主仕様0183882・UI233234235236/SS322323・MQ014～045/MSG001～011、QA054。Program001: LayoutRegistry/FieldCatalog/WebLogEventData.from/fields/constructors。Program002: PayloadCodec.encode/decode/FieldCodec。source固定8a027340、Main7aed不変。

| Test ID | class/method | 独立期待 |
|---|---|---|
| 既存Golden1（上限追補） | PayloadGoldenVectorTest.allSixtyFourLayoutsMatchIndependentMinimumMaximumAndErrorHashes | 元payloadgolden hash64を保持、既存UI233転記tableのID/kind/interaction/data/record/count/totalを直接比較 |
| 既存Golden2（上限追補） | everyRepeatingLayoutAcceptsItsMaximumRecordBoundary | 14repeatの件数/最大長をUI233 fixture literalで期待、256byteヘッダの独立算式 |
| 既存Golden3 | sharedCodecProducesIdenticalBytesUnderConcurrentUse | 384byte独立offset/space期待、元ready/start/get10と8並行維持、finallystartreleaseと有限owner |
| PT-PRO-QA054-001..012 | WebLogActionContractTest元12全method | 元UI235 literalbyte/正常/未知/交差/UTF8境界/null14/予約/並行・全期待不変更 |
| PT-PRO-QA054-013（新1） | anonymousRequestKeepsOptionalAuditMetadataAbsentOnTheWire | UI235 Username975/64・Role1039/5・Details1044/1024を全space、2080byte独立vectorとOptional.empty三・復号/fields |

新規Fixture生成0、既layouts-ui233.tsvはorigin/main UI233とSS323全64に一致、14repeat/31response。最大数字入力は独立nines整数にし、SUT helperで境界生成しない。匿名byte期待hash4bf23803ae5ebeb90f032f87657c17b5dd4b5f94fc3629f64a0b18e2616aebcf、元golden hash corpusは変更禁止。

実行: PYTHONPATH=tools/quality python3 -B evidence/01_PT/002_NK-PRO-002/input/009_protocol_independent_limits_qualifier.py prepare|static|run（run source8a027指定）、010preflight/011post。Java25.0.4/JUnit1.13.4/JaCoCo0.8.15/既protocol正常jar/JSpecify1.0.1、実DB/JMS/HTTP/RootVM/native/HMAC/鍵0。元15＋新1全16を一回、F/E/S/aborted0、newunique1のみ。全Program coverage/full451は別、当限定WebLogEventDataのLMC/自然B0と他codec未測定を分ける。BUG2541～44/YKT2177/2266～68の原因・是正・失敗証拠を参照。
