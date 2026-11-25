# Payload全64layout・semantic条件の個別受入matrix

2026-10-15、WBS-P002-02、Production a9/PG2802、UI232～236/SS322323。所有はPayloadCodec/PayloadSemanticValidatorの2path/2実行family、専有RD/sharedClassReferencesは空。全体/同byte資格を実証してから個別受入へ使用する。

## 独立契約と実Test

| Test ID／actual method群 | 独立期待値・入力・後条件 |
|---|---|
| P01/P07、PayloadCodecTest.allSixtyFourLayoutsRoundTripMinimumSuccessValues/fixedAndIndependentGoldenFieldsEncodeAtExactOffsets、PayloadGoldenVectorTest.allSixtyFourLayoutsMatchIndependentMinimumMaximumAndErrorHashes | UI233の全64tuple、UI234～236の389field/offset/type/presence/ruleを原正本→独立fixtureへ照合済み。LGNREQのUsername0/Password64/Client320と固定REQUEST byteは別byte builder。全64のmin/max DATA/RECORD＋31errorの287SHAはPG3292が原UIから別計算し一致。往復結果だけをexpectedにしない |
| M01/P08、everyRepeatingLayoutAcceptsItsMaximumRecordBoundary | 全14反復layoutのmax件数と256+data+record×countのUI233独立式、0件/1件/最大/最大超過を検査。recordの種類/長さ不一致はencode/decode前に型付き拒否 |
| P02/E01/E02、everyResponseLayoutUsesExactErrorFillersAndNoRecords/resultCodeProfilePreservesOnlyTheApprovedCancellationConflictState、AuthenticationErrorProfileTest全三 | 通常0000/0200とerrorを分離。Fは固定、Xspace/Nzero/Bspace、record0。Login retry/remaining/message及び取消0107 latest stateだけは個別UI条件を優先し、他fieldをechoしない。未知code/不正filler/長さ/型/欠落を拒否。003と同じ共有証拠、製造費を二重計上0 |
| P03/P05、encodeRejectsUnknownMissingWrongTypeAndRecordViolations/decodeRejectsLengthsNullsFixedValuesAndBadErrorFillers/valuesAreImmutableNullSafeAndRedacted/numericDigitLimitIsCheckedWithoutOverflow | 未知/fixed field指定・必須欠落・wrong kind・record過多・payload長差・fixed/error byte破壊・null container/key/value/要素を各独立に投入。送信MessageEncodingException/受信PermanentProtocolException/内部Java preconditionを区別。不変map/list・比較/hash/redactionと整数桁境界を確認 |
| P06、PayloadSemanticValidatorTest.pageConstantsCountsAndArithmeticAreEnforced | 独立UIのPage1/size100又は50、Total/Effective/Total pages/First/Last/record件数の算術を一条件ずつ変更し拒否。一般data shapeの自己往復では判定しない |
| P06、listRecordConditionsAndOrderingAreEnforced | Speaker出現数/検索Line番号/audio有無とID/path、Game表示順、Route prefix昇順、File IDの指定順を固定値で変更し、それぞれのUI規則で受理/拒否 |
| P06、scenarioInlineAndLargeFileConditionsAreEnforced | inline/large-result I/F、前後ID/title相関、UUID/relative path/SHA/byte長/record長4800/件数、Entry sequence/連続番号と条件付きaudio。wire単独で判定不能なDB内容やhidden表示順を勝手に要求0 |
| P06、mediaAnimationAndMusicConditionsAreEnforced | MEDIA descriptor、ANM/ANL/VID、MAIN/SUBTRACK/OVA/OPENING、親main/曲pair key/role、byte長/表示順等の個別条件をUI固定値と変更一条件から判定 |
| P06、loginUserPasswordDateAndSessionRulesAreEnforced | Login成功時context/role/date、UserのID/状態/locked until/session数、操作token/version/Password policyのwire側条件、範囲dateを各独立固定値で確認。実認証/DB role変更成功は他owner受入へ残す |
| P06、notificationCancellationAndQuestionStateConditionsAreEnforced/deletedNotificationNeverContainsAnswer | RECEIVED/PROCESSING/COMPLETED/ERROR/CANCELLEDと対応日時/本文/Question ID、deleted summary/answer非漏洩、取消/回答状態条件を個別固定expectationで判定。BUG-437等の旧独立reproを保全 |
| P06、receiptWebAndDefensiveContractsAreEnforced | receipt/HTTP status/Elapsed/Path/action/message・log fieldのbounds/type/必須/防御的契約、null/未知を検査。raw body/session/token/keyをlogへ出す仕様にしない |
| P09、sharedCodecProducesIdenticalBytesUnderConcurrentUse | BUG1285是正後だけを使用。UI234の独立384byte（全space＋offset0/64/320 A）を8worker全futureへ比較。Production encodeでexpectedを生成0。安定した共通誤byteを返す実shadowはAssertionFailedErrorで拒否、正常は維持 |

P04の69型・295component両方向意味はP001-03/109～113の主担当へ参照し、本payloadの全64wire/semantic検証と同一の仕事として二重計上しない。入力を組むTest helperがProduction metadataを参照していてもexpectedの正常性をそこだけに依存せず、原文fixture/独立287hash/固定scalar/明示条件の各oracleへjoinする。

## 三criteria・限界

contract＝全64layout/14record/31error・上表の全八semantic method・個別例外/入力と独立期待値を原XML Test名へ対応。scope＝2path/hash/全class-method・共有費なしを485と一致。quality＝関連85/17/174/四100/static0・実二反例拒否→必要一全3702/542/1643/static六0/FES-flaky-notrun0→同a9全Main/resource/debug byte/CRC/28stream、当二family四miss0を実照合。whole source/run/hashとactual Test名は001/112・PG3312 witness/新whole公開manifestへ固定する。未実行・別source・旧Test集合を合格へ足さない。

codec/validatorはimmutable/local copyだけでDB/transaction/所有資源を持たず、業務再送の重複更新・JMS consumer所有は非該当。Java内部null参照はfactory/constructorで即時拒否、受信null wireは恒久protocol拒否、明示任意だけUnset/Optionalを許可。NPE catch正常化0。停止/解放が必要な実資源をここで仮合格にはしない。

終了依存=P001-01/P001-02の同a9受入。全体/同native資格が真正終端するまでBUG1285/1288/YKT1051/1054/P001-03/P002-02は未完。全criteria・依存・hash・sourceを既strict auditの前/候補/後で照合してから認定する。正式1964/53・工数null・QA051final保留・全体残counter及びIT/ST未完は不変更。

## P03/P05の元入力独立性（BUG-3854、YKT-1557）

`PayloadCodecTest#decodeRejectsLengthsNullsFixedValuesAndBadErrorFillers` の正常対照を、UI232 §5.1、UI234 §3.1／3.2、UI235 §4.2で結合する。対象はLGNREQ01の384バイトと予約offset365、LGNRSP01の432バイト中のX offset0とN offset167、ANMRSP01の16バイト中のB offset6。ここでoffsetは0起点。Xと予約のspace、NのASCII 0、Bのspaceを独立に設定する。

元の有効入力を先にdecodeし、対象の値またはlayoutを検証する。その後、元の1バイトだけを置換して各 `PermanentProtocolException` を確認する。期待元は公開設計と規定文字、製品encodeは比較元へ使わない。QA-054のWLGEVTは汎用とnamedの別契約があるため、既試験の「汎用decoderが値を保持する」を維持する。個別終了・正規Protocolの照合・scope coverageはPG45370に対応する。
