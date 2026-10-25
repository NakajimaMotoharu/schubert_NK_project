# 共通Typed helper残分岐の当source単体テスト仕様

2026-10-25、sourcefd3d04df5710ca28f0e34f919cbc103e569a607b、主WBS-P001-03/関連P001-02・P002-02参照追加費0、群PROTOCOL_TYPED_MISSED_BOUNDARIES24_V1、開始.5/2/5cap10、fresh used10/残90/reset1793513544、実N/T/配賦/工数null。元20/4で74/75 class四100・TypedFieldValuesだけ残11line/7branchだったため、対応する既存4methodを限定追加し、同75classを単一runの24case/6suiteで測定する。新Test/source/Main/oracle変更0、既成功確認だけの全回帰/compile/static再演0・旧exec union0。

独立TestID根拠はProgram001原T03/T04（UI234～236/SS311§4.1/SS322§3/SS323§2/SS333/351/SSC004）及びProgram002/P05。既ID familyと完全class#methodを一意キーにする。歴史PT-PRO-20260902-06のProgram完了は原sourceの記録として保持し、新sourceの正式認定へ転用しない。

| 追加する既存class#method | 既ID | 独立期待値・狙い |
|---|---|---|
| semantic.ProtocolSemanticTypeTest#typedHelpersConvertIntAndIdentifiersWithoutLosingWireKinds | PT-PRO-001-T04 | int123/ID42を受理、Long.MAX_VALUE→int overflow・ID0・ABC/0/13桁ID・null factoryを所定例外で拒否。固定数値でrequiredInt/parseOptionalId/semanticIdの例外を確認 |
| semantic.ProtocolSemanticTypeTest#xNumericWrappersAndGeneratedNumericRangesRejectNonCanonicalValues | PT-PRO-001-T04 | 固定HTTP200/elapsed999999999、unsigned0/999999999999を受理、負/1000を3桁/桁数0・19を拒否。expectedをProductionの上限関数から作らない |
| semantic.ProtocolSemanticTypeTest#approvedEnumNamesWireValuesAndConversionMatchIndependentDesignTables | PT-PRO-001-T04 | 手書き18型のNAME=wire表からencode/required/optionalを双方向に照合、UNAPPROVED_CANARYは各型拒否。Production wireValueからexpectedを作る自己整合のmethodは追加選択せず、この独立表を使う |
| SemanticFieldValueTest#semanticHelpersRejectInvalidWireValuesWithoutReturningPartialObjects | PT-PRO-001-T03 | 固定不正日付、uppercase UUID/invalid UUID、invalid context/SHA、絶対relative path/空display pathをLayoutValidationException、cause IllegalArgumentException、固定message接頭辞/UUID本文非露出で拒否。値型検証だけで実path/秘密へアクセスしない |

対象method/共通fields・values・assertSemanticFailure・assertApprovedEnum helperの到達sourceを全文点検。PT_DEFAULT：不変field値、標準時刻/UUID、enum/ID/rangeの値型factory、例外assertのみ。相対/絶対path文字列はmemory値、実file探索/実auth/credential/DB/JMS/HTTP/Root/VM/native/鍵/配備/intent/permit/権限変更/RuntimeHookなし。fixture三TSVは013と同byteでnew-only classesへコピーし、自己所有有限JUnit/XML/exec/metadata読取以外の副作用なし。ProtocolSemanticTypeTestの他二methodやSemanticFieldValueTestの他三methodは発見/実行しない。

元20method＋追加4methodの明示selectだけ。source/dependency/input/fixture/hash、24found/started/success・F/E/S/aborted/container failure0、6suite/XML/元exitをPG9714へ。PG9716は元XML/session/CRCと、原485完全class名＋SS32369型＋SourceFile別membershipの全73unit/75physical classを独立確認する。missing class/未実行/missed counterを隠さず、四100は実証まで未達。将来target追加は別群/見積で扱う。

必要BUG/YKTは修正前登録。既BUG1757/YKT1508はfix7a3936d74/origin一致・Program002/014の全対象/六反例/非該当/原失敗保持を照合して工具scopeだけ閉じ、旧成功/受入を再加算しない。正式1964-53/17-190/工数null/QA051final/全actualHOLD/G074493/現WBS監査HOLDは不変、通常達成/commitでは止めず残PGPTへ継続する。
