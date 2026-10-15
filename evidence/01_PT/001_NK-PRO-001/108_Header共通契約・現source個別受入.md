# Header共通契約・現source個別受入

2026-10-15、WBS-P001-01、Production a9cb0ac9a3a0f9bc37d0952943a98016c7a25f25。
104～106の実before/after反例・通常84・全3701/native28と、107の独立正本照合及び原XML witnessへ接続する。単なる旧合格転記ではなく、以下全条件を個別に照合した。

## 全6artifactとTest ID

| 所有対象 | 実Test／独立期待値 |
|---|---|
| AuthenticationContext | H01/H03、HeaderModelTest.authenticationContextValidatesAndRedacts：lowercase64hexだけ、63桁/大文字/null拒否、固定異値の比較/hash、toString完全REDACTED。synthetic値で実秘密ではない |
| MessageKind、InteractionKind | H01、enumsMapOnlyApprovedWireValues：UI232 §3のQ/S/E及びS/A/Iの全六name/wireをliteralで両側確認。未知/空/複数字/null拒否。実反例で片側wire改変二件をAssertionFailedError拒否 |
| ResultCode | H01、同Test：UI232 §7の0000/0100～0107/0200/9000/9001の12固定name/wire、0000/0200だけsuccess profile。未知0199/9900/9999/null拒否。101～103の旧実反例も履歴として保全 |
| CommonHeader | H02/H03及びHDR3266-001/002、実Header七Test：Q/S/EとLogin/通常認証context、相関、結果profile、layout/direction/interaction/version/長さ・件数の各不一致を型付き拒否。百万byte両境界/次byte/checked overflow、九参照の名前付き即時null precondition、redactionを確認。構造不正をNPEで代用する実反例を拒否 |
| header/package-info | @NullMarked宣言のみ。Java25 lint/NullAway/JSpecifyは実全compileへ含み、annotationだけで静的成功とはしない。実行対象methodなし |

実source Testは010f631ba/PG3274であり、PG3286にて現Test/resource全byte一致と実Header七methodを元XMLから検証。旧五Testの結果を新二Testへ流用しない。全五実行familyの現四counter missed0、Mainは全artifact a9同byte、公開六XML/1643Main/79resource/debug CRC資格は018/881及び106のまま。

## 485原文の専有要求全5行

| RD | 独立oracle／実Testとのjoin／当leafの判断 |
|---|---|
| MQ-014：固定共通header＋data＋0以上record、総長は件数可変 | UI232 §2/§3の256byte固定headerと独立length式。MessageCodecTest.headerEncodingMatchesIndependentUi232GoldenVectorは別offset builderの固定byte、fullMessageRoundTripsAtByteBoundariesAndRejectsInvalidSizesは固定537byte構造/不正長、Header H02/H03は組合せ不変条件。codec主担当の製造・費用・受入を本leafへ二重計上しない |
| MQ-015：要求/応答で同layout/同型header | 同CommonHeader/HeaderCodecをQ/S/Eに使用。MessageCodecTest.responseAndEventHeadersRoundTripWithoutLeakingContextとHeaderModelTest.validHeadersCoverRequestResponseErrorAndEventProfiles。固定header黄金値が同型往復だけの自己oracleを補完 |
| MQ-016：画面要求・応答ごとのBean/DTO | SS323独立64行→PayloadTypeCatalogTest.explicitCatalogMatchesIndependentSs323NamedTypeFixtureで各実class名を照合。PG3284が原SS→fixture全64/69を直接照合。要求の型分離は充足、DTO個々のcomponent意味変換はP001-03の固有受入へ残す |
| MQ-017：開始byte/byte長/順序/型/必須/padding/許容値 | P001-02の107個別受入、UI233全64・UI234～236全389field原文一致、FieldDefinitionの固定literal padding/end不変条件、未知値/重複/gap/overlap拒否、Headerの固定offset golden。当owner要求を空と扱わない |
| MQ-018：文字はUTF8、encode後byte数 | FieldCodecTest.textEncodeNormalizesUtf8AndPadsWithAsciiSpace/textDecodeIsStrictCanonicalAndOptionalAware：固定UTF8 byte literal、日本語/NFD→NFC/超過/不正UTF8/不正surrogate/control/trailing space/任意spaceと必須を区別。Production encoderでexpectedを生成しない。codec主担当P002-01へ費用/受入を二重付与しない |

UI232 §3/§7とSS322は現origin/main正本を閲覧照合した。Header/codec/main/oracleの当群変更0、実3701/28を単なる監査のため再実行しない。

## 三criteriaと終了条件

contract＝上表の全5要求/6artifact・Test ID/原XML method・独立byte/literal/型分離を照合。scope＝485 P001-01専有6path/shared参照空/5要求を一致、他owner受入を変更しない。quality＝actual3701/542/1643/FES-flaky-notrun0/static六0・Protocol84/四100・全Main物理byte/CRC/28stream資格、当五family四miss0、Java内部即時null拒否と外部不正wireの型付き拒否を区別する。BUG1279の三実反例は診断数でPT/coverage加点0。

immutable header/value/enumsは資源/transaction/再送状態を持たず、再送は同値保持という構造契約まで。業務重複排除・DB/JMS並行・実プロセス所有は他ownerの固有受入へ残す。各recordはconstructorで不変条件確立、共有mutable state/IOなし。終了依存は空であり、P001-03の未完を当leafの完了と読み替えない。

認定操作は`wbs_individual_review_apply.py`へ現source/全scope/5要求/全三criteria/明示hash付き証拠を渡し、変更前・候補・後の既strict auditで同source/hash/criteria/終了依存を検査する。条件の緩和・新source作成・VM再実行なし。正式1964PT/53scope・全体603L115M470B未網羅・工数率null・QA051final保留は不変。
