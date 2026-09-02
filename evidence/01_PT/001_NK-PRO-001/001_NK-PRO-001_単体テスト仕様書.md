# NK-PRO-001 単体テスト仕様書

## 1. Program

| 項目 | 内容 |
|---|---|
| Program ID | `NK-PRO-001` |
| Class/method | `CommonHeader`、`MessageKind`、`InteractionKind`、`ResultCode`、`LayoutId`、`LayoutDefinition`、`LayoutRegistry`、`FieldDefinition`、`LayoutFields`、`LayoutFieldCatalog`、`PayloadData`、`PayloadRecord`、SS 323の69 named record、`PayloadTypeCatalog.decode/encode/dataType/recordType`、`TypedFieldValues`、`ProtocolId`と9 ID型、18 wire enum、`HttpStatusCode`、`ElapsedMilliseconds`、`Sha256Hex`、`RelativePath`、`DisplayPath`、`TypedPayloadValues` |
| 関連RD | MQ-014～MQ-038、MSG-001～MSG-011、MSG-F02/F03、FIL-006 |
| 関連UI | 232～236 |
| 関連SS | 311、322～323 |
| 関連台帳 | BUG-002/003/004、YKT-002/003/004、SSC-004、QA/RDF/UICなし |

## 2. 事前条件・fixture

- Java 25、Maven Wrapper、JUnit Jupiterを使用する。時刻、UUID、layout metadataはtest内の固定値とする。
- 64 layoutの期待tupleはUI 233をtest resourceへ独立転記し、production registryから期待値を生成しない。
- SS 323の64 layout→data/record class名を独立TSVへ転記し、production catalogや生成scriptから期待値を生成しない。
- Headerの期待byteはUI 232の1開始offset/lengthからtest側builderで構築する。

## 3. Test case

| Test ID | 目的・入力/操作 | 独立期待値・根拠 | 観点 | Evidence |
|---|---|---|---|---|
| PT-PRO-001-H01 | Q/S/E、S/A/I、result code全定義を生成・未知値をparse | UI 232 §3/§7の許容集合だけを受理 | 正常/未知/null | JUnit XML |
| PT-PRO-001-H02 | CommonHeaderへ固定値、lowercase UUID、JST、context、各長さを設定 | UI 232のQ/S/E相関と0～1,000,000 byte制約を満たす | 正常/境界 | JUnit XML |
| PT-PRO-001-H03 | protocol/version/layout/direction/interaction/UUID/context/result/長さの不正値を個別投入 | NPEではなく項目を示す契約例外 | 異常/null | JUnit XML |
| PT-PRO-001-L01 | 64 layoutのID、direction、interaction、data/record/max/totalを列挙 | UI 233の64行と完全一致、重複0 | 正常/trace | catalog comparison |
| PT-PRO-001-L02 | 不正ID/version/負長/record組合せ/最大body超過/重複を構築 | SS 322 §2/§12により起動時拒否 | 境界/異常 | JUnit XML |
| PT-PRO-001-L03 | registryの戻り集合とdefinitionを変更しようとする | immutable、未知layout/versionは専用例外 | Security/例外 | JUnit XML |
| PT-PRO-001-F01 | FieldDefinitionのoffset/length/type/presence/paddingを構築 | 1開始、end=`start+length-1`、gap/overlap監査可能 | 正常/境界 | JUnit XML |
| PT-PRO-001-F02 | UI 234～236の60有項目layout・389 fieldを全列挙しproduction catalogと比較 | UI 3文書のSHA-256を付した独立TSVとlayout/area/name/start/length/type/presence/ruleが完全一致 | 正常/trace | catalog comparison/JUnit XML |
| PT-PRO-001-F03 | 8列不足、未知layout/area/type/presence、数値不正、重複、gap/overlap、領域長不一致を構築 | 起動時に`LayoutValidationException`または型別の未対応例外で拒否 | 異常/null | JUnit XML |
| PT-PRO-001-T01 | 64 layoutのdata/record class名をproduction catalogと独立fixtureで比較し、全named typeを列挙 | SS 323転記64行と完全一致、data/recordの実classは69型、反復record layoutは14件 | 正常/trace | `named-types-ss323.tsv`、JUnit XML |
| PT-PRO-001-T02 | 64 layoutをnamed typeへ変換しfield値へ戻す。optional値あり/なし、未知layout、data/record型不一致、record有無、nullを投入 | 明示mapperで完全往復し、reflectionによるcomponent順推測なし。不一致・nullは境界で拒否 | 正常/異常/null/security | JUnit XML |
| PT-PRO-001-T03 | `String`/`long`/`boolean`、N17/X17日時、UUID、認証context、SHA-256、relative/display pathを型変換し、null/unset/未知形式/NFD/byte境界/Unix・drive・UNC/`.`/`..`/空segment/backslash/controlを投入 | SS 323 §2のJava型、UI 243とSS 333 §5のpath拒否matrixから独立固定した値だけを受理する。全semantic型・69 named recordの`toString`は値を出さない | 正常/境界/異常/null/security | JUnit XML、BUG-004再試験 |
| PT-PRO-001-T04 | N12 ID 9種、N2～N8=`int`、N9/N12=`long`、18 wire enum、X3 HTTP status、X9 elapsedを69 named recordへ変換し、0/1/各桁上限/上限+1/未知値/nullを投入 | SS 311 §4.1、SS 322 §3、SS 323 §2、UI 223/234～236、SS 333/351、SSC-004から独立した型・allowlist・rangeだけを受理。Record constructorでwire桁不変条件を確立 | 正常/境界/異常/null/security | `ProtocolSemanticTypeTest.xml`、64 layout matrix |

## 4. Null・並行・再送観点

- Public constructor/factory/lookupへnull、blank、unknownを投入し、NPEを外部契約にしない。
- Registryはimmutableなため並行readで同一内容を返す。状態更新、再送固有処理は本Programにない。

## 5. 実行command・合格条件

```sh
JAVA_HOME=/home/mini/codex/project1/work/toolchain/jdk-25.0.4 \
MAVEN_USER_HOME=/home/mini/codex/project1/work/toolchain/m2 \
./mvnw -Dmaven.repo.local=/home/mini/codex/project1/work/toolchain/m2/repository \
  --no-transfer-progress -pl src/schubert-nk-protocol -am clean verify
```

Line/method/class/branchを各100%、failure/error/skipped/flaky/disabled/not-runを0、64/64 layout一致を合格条件とする。対象commit、coverage、実行日時、終了code、evidence hashは実行結果とmanifestへ固定する。

## 6. 実行結果・障害

状態: **PG・PT完了**。Run `PT-PRO-20260902-06`、commit `f519ba318c258b08982dc09e04dbc088e439bc83`でProgram 25件、module全56件PASS、coverage 4指標100%、SpotBugs 0件。UI 234～236の389 field catalog、SS 323の69 named record/64明示mapper、全共通Java型、N12 ID、primitive桁range、X numeric wrapper、wire enum allowlistを実装・試験済み。BUG-002/003/004・YKT-002/003/004は同runで再試験PASS。詳細は`002_NK-PRO-001_実行結果.md`と`evidence/manifest.json`を参照する。
