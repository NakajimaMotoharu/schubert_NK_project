# API必須列と質問frameの静的検査・通常試験

NK-DAT-001／NK-MSG-002、WBS-F03/2-2-b／P004-05、SS331/332/324/354、SSC-157、451 §5、YKT-2863。対象APIの限定4 Mainとpackage metadata 3をRoot同一NullAwayでcompile。実DB、実認証、権限状態、QA056保留型は対象外。旧二namespaceのprivate反射は履歴保全、当source `f7ff078a19cf28f1dbd8c43eb8b7490d521b5f54` から撤去。

| Test ID | 独立期待と結果 |
| --- | --- |
| PT-QUALITY-002 | 固定値と時刻の同一性、nullだけSQLSTATE 22004と固定診断。成功。 |
| PT-QRY-SCOPE-001／003 | 固定byte frame、元役割と固定legacy区別、null・未知・別route／magic・切断、入力所有。元2件成功。 |
| PT-API-STATIC001／002 | それぞれRequiredColumnとQuestionQueryScopeFrameがfinal、唯一private constructorとstatic member。JDK宣言で確認、通常件数に加えない。 |

3件全成功、F/E/Sと対象選択漏れ0、NullAway指摘0。RequiredColumnの無フィルターは行3/5、method1/2、class1/1、branch2/2。QuestionQueryScopeFrameは行27/29、method6/7、class1/1、branch21/21。未測定の四行・二methodはprivate constructorのみ。実API/DBや六製品正式coverageは未成立。

PG42922、2026-11-23 JST、dev-foundation、Core `e8368d22c4da2ec841f008df793594d3be9066af`。実行command、原JUnit、当実物CRC、入力・SHAは公開 `evidence/01_PT/018_NK-OPS-001/evidence/PG42922-api-two-namespace-without-private-reflection-v1/manifest.json` SHA-256 `e91238145723c1eb62f5243e0dc1735b00fefa2188034c8dcbd3c8417e79fe75`。
