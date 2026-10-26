# 1187 Semantic独立期待値七・診断保護・定数九PGPT仕様

Program NK-PRO-001、WBS-P001-03主担当/G03.01・F03参照、event2467、開始1/3/7pp cap10。base host source21d275a74/Main21d7c304、BUG1865/YKT1616・1866/1617・1867/1618先行。関連NK-PRO-001/UI232§3・243/SS323§2/10・354、固定wire/UTF8/NFC型契約を変えないTest-only PG。前1185/1186の四成功を変更後sourceへ輸入しない。

同一SemanticFieldValueTest内の一経路へ集約する。

| 変更 | 独立した期待値・保持条件 |
|---|---|
| 九literal/既54参照を定数化 | safe、relative/display、unset、value、invalid、absolute、NFC relative/displayを意味名のTest-private定数へ。各元値/全String token参照を逆展開で保持。e+combining入力をNFC期待値へ同一化しない。 |
| decoder七のexpected factory依存を除く | Auth optionalはHEXA、SHA required/optionalはHEXA、Relative required/optionalは明示relative literal、Display required/optionalは明示display literalへ。OptionalはJDK包装だけ、Production getter/mapはactual側にだけ置く。Main factoryはencoderへの入力構築として保持しexpectedを生成しない。 |
| uppercase診断保護一 | 元lowercase UUID非含有を残し、実不正inputの固定UUID_UPPERCASE_TEXTもsafe exception messageに非含有を検査。共通語invalid等を一律禁止する誤assertは作らない。 |

Auth/SHAのHEXAは公開された型shape用synthetic64 lowercase hexで、実credentialではない。relative/displayの期待値はSSの明示NFC/相対文字列、decomposed入力はJDK/Productionからexpectedを作らずprecomposed literalへ照合する。equals/hashの既補助propertyは独立数値/内容oracleとは区別し、各wireValue literal assertionを保持する。

四Test methodすべてに影響するため、前の二method選択から次の四method固定catalogへ広げる。PT_DEFAULTの具体境界は1185と同じ純粋Protocol jar/Test/JUnit/jspecifyだけ、memory値検査/日時/UUID/UTF8/NFC、DB/JMS/HTTP/実file/credential/Root/VMなし。元HOLD Testの抽出や再演ではなく、当変更sourceの既存Test四を普通に実行する。

| Test ID family（各JP/TR） | method | 主観点/独立期待値 |
|---|---|---|
| PT-PRO-SEM-D | semanticHelpersDecodeAndEncodeEverySupportedShape | 明示string/number/boolean、JST17digitと固定Instant、UUID、HEXA/path/display、unset。七decoder primitive expectedとencode固定FieldValue constructorを別方向で照合、期待値をProduction戻値から作らない。 |
| PT-PRO-SEM-N | semanticHelpersRejectInvalidWireValuesWithoutReturningPartialObjects | Feb30/invalid/uppercase UUID/absolute・空pathを拒否。固定safe semantic診断・IAE cause、lower/uppercase UUID非出力。 |
| PT-PRO-SEM-V | semanticValueObjectsNormalizeValidateCompareAndRedact | 固定wireValue/NFC literal、null/空/絶対/traversal/byte境界、redacted toString、補助equals/hash relation。後者を独立内容/numeric oracleとはしない。 |
| PT-PRO-SEM-Z | semanticEncodingHelpersRejectNullReferences | null入力/Optional referenceをNPE契約で拒否、catchして製品の正常値にしない。 |

PG前にsource変換/仕様を固定→九値/旧54参照/七assert/追加一guardを原sourceに結合・不正な値/他assert/normalization改変のmetadata反例→整形→source commit固定→必要六正常/対象静的→preflight→ja-JP/tr-TR専用JVM各四Test/一suite（計八実行/四固有method）→元XML/exec/CRC/session/loaded-classを独立postする。並行/再送/transactionは無状態codec値型の当Testに非該当、Localeをglobalに変更せず別processへ分離。変更後の失敗は915へ修正前起票し、F/E/S/flaky/aborted/not-runは合格へ入れない。

coverageは完全Protocol物理176（解析169と無実行member package注釈七を含む）の各exec別全counter/未網羅を報告。前1186/他source/両Localeのexecを合成せず、100%未達は未達で残す。標準counter0の生成class等G01の残を隠さない。source/Main/他Test/元owner-cost/trace/旧runtimeを保持し、全Program/G03/F03/451・正式1964/53/17/190・工数null・QA051final・元安全HOLDを別判定とする。

command/OS/JDK/tool/version/時刻/branch/対象commit/actual exit/fixture・expected/actual/全counter/BUG/hashは各manifestと1188結果へ保存する。明示した新launcher/metadata readerだけを公開し、保留二fileをread/hash/scan/変更しない。通常小受入/報告/commitで止まらず、所定停止条件まで継続する。
