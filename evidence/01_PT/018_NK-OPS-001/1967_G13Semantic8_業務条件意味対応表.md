# Payload semantic八methodの条件対応

1966/2197/current64446。全Test465行/全validator487行、TestのvalidPayload→PayloadTypeCatalogTestの固定fixture helper、decode→named mapping→semantic呼出部分を読取。既P06の業務条件oracleを追跡するが、全named mapperの再reviewではない。assertInvalidはPayloadTypeCatalog.decode全体のLayoutValidationExceptionを期待するため、型constructor側で先に拒否するcaseをvalidator分岐実行済みと断定しない。

| class | method | 既存Test ID family | 独立期待値・条件 | 未証明・範囲 |
|---|---|---|---|---|
| PayloadSemanticValidatorTest | pageConstantsCountsAndArithmeticAreEnforced | PT-PRO-002-P06 | Page size100/50、Page>=1、Total count=records、空はtotalPages1/first0/last0/records0、page1/count1の各算術値を一つずつ破壊 | 2ページ目正常・Effective page999999の専用固定vectorは当Test群になく、source検索では2は不整合入力のみ。全ページ境界を八methodから認定しない |
| PayloadSemanticValidatorTest | listRecordConditionsAndOrderingAreEnforced | PT-PRO-002-P06 | Speaker出現>=1、Game順序非減少、検索Line>=1とaudio flag↔ID/path、Route File件数>=1/Prefix厳密増加。SCFはID2→1でも受理 | SCFのDB指定順などwire単独で判定不能なhidden順を推測追加0。すべてのlist/UIsort条件を単一validatorへ強制しない |
| PayloadSemanticValidatorTest | scenarioInlineAndLargeFileConditionsAreEnforced | PT-PRO-002-P06 | Iは0～200＋descriptorなし、Fはinline0・descriptor完全・4800×1～10000。Entry連続/ID再出現拒否/同entry本文一致/audio0又は1開始連続、片側audio指定拒否 | fileの実size/SHA/原本/FD確認は別。generic/named入力からsemanticまでのpipelineであり実large-result fileを読まない |
| PayloadSemanticValidatorTest | mediaAnimationAndMusicConditionsAreEnforced | PT-PRO-002-P06 | File byte長>0、animation1+2+opening1=4、SUBTRACKだけparent、music role N以外だけpair key | MIME/SHA/pathのscalar allowlistはnamed typeへ依存。実media/Range/DB表示順の成功ではない |
| PayloadSemanticValidatorTest | loginUserPasswordDateAndSessionRulesAreEnforced | PT-PRO-002-P06 | username trim/allowlist、password12～128codepoint/256byte/末尾space/username同値拒否、login成功必須context/Role/日時・retry/attempt0、expiry>issue、session3拒否、date逆転/32日拒否 | 31日/366日の全等号境界・全Unicode・同時session実制御は本method単独未証明。internal scalar型とcross-fieldを分離 |
| PayloadSemanticValidatorTest | notificationCancellationAndQuestionStateConditionsAreEnforced | PT-PRO-002-P06 | RECEIVED/PROCESSING/COMPLETED/ERROR/CANCELLEDの日時presence、error二field、削除flag↔本文/ID、未完answer禁止、取消CANCELLED+日時、ANSWERED↔回答日時 | approval済UI236の状態を使用、未知状態は別直接fixture。DB owner/再送/取消transactionの代用にしない |
| PayloadSemanticValidatorTest | receiptWebAndDefensiveContractsAreEnforced | PT-PRO-002-P06 | 受付26文字allowlist、質問空/末尾space、HTTP大文字3～8/Path先頭slash/query禁止、null validator、wrong numeric/text/flag/timestampとUNKNOWN通知を直接Typed fixtureで拒否 | direct fixtureで型別helper拒否を確認する設計だが今回動的未実行。実HTTP/log/token/外部拒否操作の試行でない |
| PayloadSemanticValidatorTest | deletedNotificationNeverContainsAnswer | PT-PRO-002-P06 | 未削除COMPLETEDは回答あり可、削除＋質問/ID unsetは受理、回答を戻すと拒否。既BUG562の独立textを使用 | 削除済み通知そのものの削除/DB伝播は対象外。古いBUG成功/実PTをcurrentへ合算しない |

fixtureは型別のliteral/default/明示replacementを入力にし、expectedは上表のUI/SS条件からassertValid/assertInvalidを固定する。Production validatorの返り値からexpectedを計算0。ただし入力の領域形状はProduction catalog参照、scalar constructor拒否とsemantic拒否の個別到達証明には実行情報が必要であり静的表だけで補完しない。

次の独立通常PT候補はpage2/count101/size100→totalPages2/first101/last101/record1、最大effective999999/total99999900/first99999801/last99999900/record100及び一条件±1拒否。これは既P06内の明示境界vector追加候補で、既成功確認の再演や拒否境界の探索ではない。実着手前に専用仕様/固定source/安全判定を別群へ凍結する。現群は八method/一family/八関係の静的対応のみ、製品差分/実PT/coverage/正式増分0。
