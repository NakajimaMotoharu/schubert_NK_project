# JST・ResourceScope・単調時計の個別受入

2026-10-15、WBS-P003-03/08、Production a9/PG2802。Main/Test/設定変更なし、同source全3702/542/1643/静的六0・同28stream/全Main-resource-debug同byteを001/112/公開wholeから参照する。全体未網羅603L115M0C470B/正式1964-53/工数null/QA051final保留/ITST未完は維持。

PG3316（工具f945824c7）は既終了PG3302原manifest/hash/sourceをRO認証し、Protocol17suite85case/Web二suite14caseに加えStorage23suite163caseの全原XML/source hashを要約、actual0。sourceは固定25e571bd1、現在選択Testが同byteであることを検査した。Test名の引数値は公開せずclass/元ordinal/名前SHAで一意追跡し、metadata properties/stdoutを輸出0。これらは3702の内数で新試験加点0、Maven/VM/業務再実行0。公開`evidence/provisional/PG3316-whole-storage-suite-witness/manifest.json`。

## P003-03：JstWireTimestamp一path

UI232 §3、SS322 §4.2、MSG011（主担当P002-01）を適用。Program仕様N01/T03/T04とJstWireTimestampTestの実四methodへ対応する。

| actual method | 独立期待値/境界/異常 |
|---|---|
| formatsAndParsesStrictJstMilliseconds | 固定Instant03:34:56.789Z→JST12:34:56.789の17桁literal、うるう日2024-02-29、null、sub-ms、16/18桁、非数字、2/29不正、月13。Production formatでparse expectedを作らない |
| bug037ExpandedYearsAndUnrepresentableInstantsAreRejected | 17ASCII桁に収まらないexpanded year、provider範囲外Instant、millisecond精度を送信側で型付き拒否。旧BUG037/YKT033の正常/異常vectorを維持 |
| bug037HeaderSenderRejectsBadTimeAndPreservesAdjacentContext | header固定offset/隣接context不変と不正時刻送信拒否を独立literalで確認 |
| bug037RequiredAndOptionalDataSendersRejectBadTime | 必須N17と任意X17の送信境界・通常JST値と不正値を確認し、切捨て/非正規時刻を返さない |

全class/methodの四counterは同sourceでmiss0。JSTのserialize/parseは純変換・immutable formatterでIO/transaction/再送状態/owned資源なし。nullはJava内部即時参照precondition、format精度/範囲・parse形式/日付異常はIllegalArgumentExceptionに分類する。時計の実時間観測や現在日付をgoldenへ用いない。scope=485一path/hash、専有RD/shared参照空、終了依存P002-02は同a9受入済み。

## P003-08：ResourceScope、LinuxMonotonicClock二path

ResourceScopeはSS333先頭SSC063/PG170171・BUG195/YKT154の明示優先順位を正本とする。単調時計は承認SSC119/289、SS341 §7.3/SS343のCLOCK_MONOTONIC=1・Linux64bit timespec・固定非成功/代替時計禁止を適用する。SS333だけで時計の正本根拠を省略しない。

| Test ID／actual method | 独立oracle・後条件 |
|---|---|
| RSCOPE001/successfulOwnership | literal順body→close、結果42、成功closeまで戻らない |
| RSCOPE002/knownIoFailures | 明示入力の各既知Storage reasonはbodyのみなら保持、IO close/既存suppressed等の複合はUNAVAILABLE。raw cause/補助例外を外部へ渡さず、close回数1を独立counterで確認 |
| RSCOPE003/unknownBodyFailures | Runtime/NPE/Errorの元primary identityを保持、close1回、補助0 |
| RSCOPE004/knownBodyUnknownCleanup | 既知IO body又は成功body＋unknown cleanupは元unknownを優先し正常復帰0 |
| RSCOPE005/unknownCompoundFailures | unknown三種×close IO/unknown三種/同一throwableの全15組、元primary同一、固定redacted secondary一件、self-suppressionなし、close1回 |
| RSCOPE006/nullAndNullableContracts | release/action nullは受領前拒否・close0、明示nullable callback結果はnull透過＋close1、body NPEはcleanup後に同一物を非正常伝播。NPE catch正常化ではない |
| RSCOPE007/nestedScopes | literal body→inner-close→outer-close、全close、未知複合のprimary/sanitized secondary二件・既知reason保持 |
| RSCOPE008/concurrentScopes | 64virtual threadの各入力iに対する独立算術i+42とclose総数64、共通mutable resource状態を持たない |
| COWNER時計/literalTimespecAndExactSignedLongBoundary | Test ReadCallがCLOCK_MONOTONIC ID1、16byte/offset0seconds・8nanosを要求。0、2s+999999999ns、Long.MAX_VALUE=9223372036s+854775807nsの独立literal |
| COWNER時計/negativeAndOverflowNeverWrapOrUseAnotherClock | 負seconds/nanos、nanos1000000000、和の上限+1、積overflow、read -1を固定IOException/原因なしで拒否、fallbackなし、null read拒否 |
| COWNER時計/fixedAbiPlatformAndSymbolFailures | null OS/arch/symbol、非Linux/不明arch/欠落symbolを拒否。許可文字列amd64/x86_64/aarch64の同host64bit ABI呼出しと、当hostの実clock>0/同bootで後退0を検査。実ARM機試験をしたとは主張しない |

上記8＋3の実methodはPG3316のStorage原XMLへ一意対応する。CLOCK_MONOTONICはWallClock/System.nanoTimeのJVM別始点へfallbackしないsource control flowも確認した。Arenaはmethod内で所有/全経路close、readのscopeは借用、OS clock観測以外のUnit/DB/Root変異0。ResourceScopeは受領したclose一回だけを持ち、callerの借用root/他資源/再試行を勝手に操作しない。

scope=485二path/hash（内部Action/ReadCall含む各outer family集約）、専有RD/shared参照空、同sourceStorage LINE1172/METHOD257/CLASS37/BRANCH527全miss0・physicalMain74を別単位で維持。全種類のIO理由をTest入力へ列挙することと、Production methodでexpected結果を生成することを混同しない。expectedは入力reason/例外identity・SSの優先順位表・独立順序counter/算術である。

## 三criteria・認定範囲

contract＝上記全入力/結果/例外/所有/終了後条件・Test ID・実XMLと承認SSを対応。scope＝P003-03一path/P003-08二path、全含有method/interface・関連根拠を485/hashと一致。quality＝同source実全3702/静的六0/FES-flaky-notrun0/当各family四miss0/同1643Main-79resource-debug/CRC/異28stream、正常/境界/異常/null/並行/closeと非該当根拠を確認。両方の終了依存P002-02は同a9 ACCEPTED。既strict auditを前/候補/後照合してから当二leafだけ認定する。

元ResourceScope BUG195の全consumer横展開を今回新しく閉鎖したとは扱わず、既承認契約と現在の共通scope単体/同source全体結果をこのleafで受入する。各consumerの固有操作/DB/Unit/復旧は対応ownerの個別受入に残す。単調時計を所有/boot/epoch/Invocation認証の代用にしない。新実装/新native/再実行0、原/v3費用不変更、群0860は当二leafの固有監査.15/.5/1.2pp内、実費/N/Tnull。
