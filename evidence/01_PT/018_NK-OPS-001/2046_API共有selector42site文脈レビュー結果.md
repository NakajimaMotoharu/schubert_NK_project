# API共有selector42候補・静的文脈レビュー

2026-10-26、群2341/G03.01/開始.5/2/6 cap10、current f127。PG10252のAPI42候補/30sourceを現SHA不変で読み、共通呼出し名だけで欠陥を判定しない。製品Test/DB/HMAC/鍵/native/Root/外部操作0。独立LP/JCE/golden・入力identity・不変性・前後条件を区別する。

|source|site数|根拠/判定|
|---|---:|---|
|UserMutationRequestTest|2|keys.calculate二結果の比較はheader/token除外property、別checkは手書きLP/JCEと各fields・入力header identityへ比較。cleanupは別SecretBufferTest固定3byte/他owner/null/emptyのoracleがある。|
|UserQueryRequestTest|2|同じくheader除外/同一input・独立LP/JCE check/cleanup補助。|
|LogRequestTest|2|check/emptyFiltersはTest独立LP/JCEで計算したdigest、cleanup補助は共通固定length oracleと区別。|
|MediaApplicationServiceTest|1|固定二InstantとDBの明示timestamptz三値が先に独立比較され、二DB値の非同値は補助property。今回DB不実行。|
|MediaRequestTest|1|field.value後closeゼロはcleanup補助、別manualLP/JCEと共通固定3byte oracleを確認。|
|QuestionMutationApplicationServiceTest|2|固定SUCCESS/0200集合、Test wire helper固定offsetのpayload slice。Production生成をexpectedへ使わない。|
|QuestionMutationReplayServiceTest|2|keys.calculateの比較はrole/token除外property、直前に独立Mac/LP byte列との比較あり。|
|QuestionQueryApplicationServiceTest|2|一siteのexpected helperがProduction decode→ReplayTest.wireのsemantic判定を使うためBUG1811/YKT1562。もう一siteは初回/再送payload同値の補助property、独立初回oracleへ依存する。|
|QuestionQueryRepositoryTest|1|USER/ADMIN捕捉SQLの非同値と各owner predicate literalを別検査。SQL処理は今回実行しない。|
|QuestionQueryRequestTest|1|role除外propertyに先立ち独立LP/JCE oracleあり。|
|QuestionSubmitRequestTest|2|hash同値はowner以外header/role除外property、checkがJDK DataOutputStream固定LP/domain/field/bodyと独立Macを比較。|
|ScenarioApplicationServiceTest|1|Test ScenarioReplayFixtureの固定offset、独立JCA hash/既fixtureの公開publisher countに基づくwireをslice。実file/親再試験をしない。|
|PostgresDeploymentTest|1|同じsettings関数はTest parser。expectedはSS342独立32行literal、actualだけ配備template読取で、Production parserを共有しない。|
|InboxModelTest|1|固定Optional tokenの入力保存属性で同値helper名はJDK Optional.of。|
|OperationFingerprintTest|1|NFD/NFC同値property。別methodの独立OpenSSL固定canonical/HMAC vectorが外部根拠。|
|SecretBufferTest|2|Inspectable.storageはTestによる所有buffer capacity観測、全capacityゼロのproperty。別methodに固定3byte afterclose/null/empty/例外/他owner byte保持oracleが既存で、新しい同じ確認を作らず参照。|
|AuthenticationInboxCleanupTest|1|固定END/Optional.emptyと業務DB後条件の組合せ。JDK helper名一致でSUT共有ではない。|
|InboxCleanupNonAuthenticationTest|1|同上、固定END/0件/参照不変、今回DB不実行。|
|InspectionParentBoundaryTest|1|Test固定List5/2/3/trueの二owner読取結果、lock後条件は別literal。今回再演0。|
|ApiDurationMetricExporterTest|1|固定Prometheus literal行のSetとactual行のSet比較、同呼出しはJDK集合化だけ。|
|ApiObservationContextTest|1|owner.metrics二回の同一性はcached registryのidentity契約、次の未ready render拒否・port呼出し空と組合せる。無意味な一回取得値の自己比較ではない。|
|AsyncJobCountRepositoryTest|1|Test指定rs/ps exception identityのsuppressed順をJDK Listで比較。|
|AsyncJobMetricCollectorTest|1|同上、Test注入close identityとUNKNOWN処理後の状態、実graph処理を今回起動しない。|
|OutboxObservationRepositoryTest|1|同上、Test指定rs/ps identity/order。|
|AuthContextCodecTest|1|Test固定identityのsession UUIDを別DTOへ渡す保存属性、別JCE envelope/AAD固定oracleを確認。実sessionを読まない。|
|AuthSessionServiceTest|1|固定JSON literalとDB detailsを同JDK-adjacent JSON parserで構造比較、Production生成をexpectedへ使わない。|
|LoginInboxServiceTest|1|cleanup補助は別独立LP/JCE/元caller copy比較と共通固定3byte oracleを参照。|
|LoginUsernameTest|2|Test literalUnicode/repeatだけのexpected、NFC/LocaleROOTの明示sigma/İ vector。|
|PasswordPolicyTest|3|同上、NFC/emoji/ASCIIの固定literalとJDK char[]変換。|
|ApiApplicationPreparationTest|2|複数layoutが同一processor instanceを共有するassembly identity契約、別class型/キー集合/保持領域後条件あり。今回assembly/実環境不実行。|

41siteは当文脈で欠陥を認定せず、一site/expected共通helperにoracle独立性不足を起票。ほかの62共有候補（Batch41/Bootstrap7/Web14）・残direct/identifier/constructor等と全要求/TestID/branch/evidence joinは未完。次は対象限定PGで独立oracleへ是正し、元Production PTのHOLDを解除せず、期待値資格のメタ試験と実PTを分ける。正式1964-53/17-190/工数null/HOLD不変。
