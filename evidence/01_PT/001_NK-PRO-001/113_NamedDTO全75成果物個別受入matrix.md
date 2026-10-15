# Named DTO全75成果物の個別受入matrix

2026-10-15、WBS-P001-03、Production a9/PG2802。関連SS323、UI233～236、109～111。本票は全体/同byte資格の実終端後だけ受入へ使用し、監査中の記述だけで認定しない。

## 全scope

485の専有75path＝SS323の69 named data/record型＋FixedPayload/PayloadData/PayloadRecord/PayloadValues/TypedFieldValues/TypedPayloadValues。73実行familyと2抽象interface、専有RD/sharedClassReferencesは空。Java型はSS311323/SSC004、fieldの意味/名前/順序は正本UI234～236の独立fixtureへ接続し、要求行ownerが別でも当型の具体的契約を省略しない。

| 対象 | Test ID・actual・独立oracle |
|---|---|
| auth/scenario/media/admin/question/log/commonの全69 named type（完全名/総数は原fixtureで厳密検査） | T01/T02/T04及びDIR3298-001。型名/全64layout対応はSS323独立fixture。public accessor135bindingとUI非固定field295項目の識別値/型/Optional genericを独立指定。from→各public componentと、独立入力→明示public constructor→fieldsを別方向で照合。全参照null・from null・79任意の個別Unset/Optional.empty・空4型のempty/余剰/全toString redaction。Production field順/reflection private/expectedのProduction生成0。カテゴリ等の型やwire値はUIの明示literalとSS型規則であり、actual型からexpectedを推測しない |
| FixedPayload | MessageCodecTest.fixedPayloadIsDefensiveAndWireMessageChecksLengths、M01/M02：独立input `[1,2]`/`[3,4,5]`をconstructor後に変更、返却copyも変更し、原同literal不変/record list変更不可/長さ件数/負長/record長不一致/null collection・要素を検証 |
| PayloadData、PayloadRecord | fields()抽象契約のみ、当69実装を上記独立expected mapへ照合。実行不能を除外設定へ変えない |
| PayloadValues、TypedPayloadValues | PayloadCodecTest.valuesAreImmutableNullSafeAndRedacted、PayloadTypeCatalogTest.typedModelsAndHelpersRejectNullMissingAndWrongKinds/catalogRejectsUnknownLayoutsAndMismatchedDataOrRecordTypes：layout/data/records・collection要素のnull、immutable戻り値/型不一致/不許可recordを拒否。一般値→typed→一般値往復は補助propertyに限定し、意味対応の単独oracleにしない |
| TypedFieldValues | SemanticFieldValueTest全四、ProtocolSemanticTypeTestの独立enum/ID/int/Xnumeric table、T03/T04：必須/Optional/Unset・wrong kind/null/未正規/未知値/semantic wrapperの各変換をliteral/標準JDK値へ照合。DIR3298-001も295componentの全入力と公開signatureを独立検査。ここで参照する各wrapper自体の主担当はP002-01、製造費/受入の二重付与0 |

69型の正確な完全名とfield一覧はSS323独立64行fixture、named-accessors-independent.tsv、全fixtureを実列挙するDIR3298-001及びactual XMLへ一意joinする。上表の機能別括りは分類の説明に限り、手計算の分類数をscopeの代用にしない。

## 実反例と品質

BUG1288：旧往復試験が実Login Username/Password相互swapを見逃したbeforeを保持。48e4dd275先行→d45aec8f1是正後、実同shadowがDIR3298-001のscalar assertionで失敗、正常全69は実成功。公開PG3294 manifest/110のsource/UTC/payload/log hashへ接続し、診断四selectorをProduction PT/coverageへ加点0。

正常/境界/異常/null/例外は上表。純immutable DTOでDB/transaction/IO/owned processを持たず、その再送副作用/競合更新/資源終了は非該当。並行readの前提は参照/collection/byte copyの不変性と共有codecの独立8worker試験へ対応。全任意fieldを同時に埋めた入力を業務semantic適合requestとは主張せず、その相関はP002-02の別八methodで検証する。

contract＝全75artifact・295component・69型・TestID・両方向の独立期待値を対応。scope＝485専有75/hash/73実行＋2抽象/共有空を一致。quality＝actual Protocol85/四100/静的0・二反例拒否→必要一全3702/542/1643/静的六0/FES-flaky-notrun0→同a9全1643Main/79resource/debug byte/CRC/異28stream資格及び当73family四miss0を確認。各実source/run/hashは112/新公開whole manifest/PG3312原XML witnessで固定する。

終了依存は空。新全体/同native資格の未完中は本leafを閉じない。成立後も正式1964PT/53scope・全体残counter・工数null/QA051final保留・他WBS受入/ITST状態は変更しない。
