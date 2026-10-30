# 2893 G13 current11 artifact担当候補仕様・PG-D936

source6b53/normal14216、元registry1760/15312、G13.07群3285の0.5/2/5pp固定。十TestとApiStopBudget Mainという11 exact pathだけの内部責任候補であり、OS owner/runtime owner/起動権限/品質承認とは無関係。基準941 logicalのMain既担当をanchorとして、実全body/主subject method/SS/原TestID/元actual XML・sourcepinにより一件ずつ判断する。工程担当、suffix/module、多数決や単一helper呼出しだけでは定めない。過去PG-D655～657/673を全Testへ一般化しない。

| exact class/file | candidate primary/cost | original baseline anchor | 原Test件数 | 元結果 | 判断根拠 |
|---|---|---|---:|---|---|
| ApiNonSecretConfigTest | WBS-P018-01 | ApiNonSecretConfig.java | 7 | 2870 | SS343 §4–5; nonsecret API parser is the explicit subject |
| WebNonSecretConfigTest | WBS-P018-01 | WebNonSecretConfig.java | 7 | 2870 | SS343 §4–5; nonsecret Web parser is the explicit subject |
| ApiStopBudget | WBS-P018-05 | ApiProcessLifetime.java | Mainのみ | 2874 | SS342/351; baseline API lifetime owns first-stop budget and delegates begin/remaining |
| ApiStopBudgetTest | WBS-P018-05 | ApiProcessLifetime.java | 18 | 2874 | The explicit subject is the API lifetime first-stop budget, not generic clock/G03 |
| FixedServiceExecArgumentsTest | WBS-P018-04 | FixedServiceExecArguments.java | 5 | 2878 | SS342 §4.2 fixed ordinary argv policy, not an exec operation |
| FixedNativeCoverageProfileTest | WBS-P018-08 | FixedNativeCoverageProfile.java | 5 | 2882 | SSC193 profile parsing and role labels; runtime/native authority remains separate |
| TerminalNativeCoverageProfileTest | WBS-P018-08 | FixedNativeCoverageProfile.java | 4 | 2882 | SSC196 terminal profiles/checkpoint are primary; Identity/Map fixture is a shared P01804 reference, cost0 |
| FixedNativeCoverageTerminalTest | WBS-P018-08 | FixedNativeCoverageTerminal.java | 5 | 2882 | SSC234 same-owner terminal/closing control contract, not actual native export |
| ApiAdmittedConfigurationTest | WBS-P018-05 | ApiProcessMain.java | 8 | 2886 | SSC301 API Main data port is primary; parser/location/configuration record are shared fixtures |
| ApiReadinessPredicateTest | WBS-P018-05 | ApiProcessMain.java | 3 | 2886 | API Main readiness predicate is primary; no native promotion/admission is being qualified |
| RequiredColumnTest | WBS-P004-05 | RequiredColumn.java | 1 | 2888 | DAT009/SS331332354 required JDBC-result value boundary, not a JDBC connection or business query |

完全path/sourcehash/全subject path/必要literal token/原post hashは新pure helper RULESと資格manifestへ固定。Test主subject以外のConfig/Location/Configuration record/Identity/ServiceConfigFilesは関連共有参照であり、その既担当を移さず追加費0。TerminalProfileの実NSS代役を理由にファイル全体をP01804へ再配賦しない。ApiStopBudget MainはApiProcessLifetimeの保有field/constructor/begin/remaining委譲とbaselineP01805の一致から判断し、clockという一般名でG03/monitoringへ移さない。

旧canonical v1/旧全post.owner/原source-run/485.artifacts/原-v3-v4-v5/実費null/全受入を保持し、新v2 viewだけでUNKNOWN→REVIEWED_NOT_ACCEPTED候補とする。既logical rowがある場合は常に既baseline優先、11外はv1完全一致、anchor欠落/owner/cost不一致は拒否する。原XMLの10suite63methodは責任対応の参照だけ（新PT/coverage/native/正式0）。各Testの@Xml対応と原@Test数/hashを独立確認し、shared-codeの費用二重計上0/過去再配賦0/別source成功移植0。全G13/残UNKNOWN/受入依存は未完。

必要check：normal/current/snapshotの実入力pin、元registryで11全てUNKNOWN、既anchor owner/costと実body/原TestID/全subject、MainClockの実caller4関係、各元post/source/全case63、v1-v2の他全owner不変、baseline優先・欠落/異owner/異costの反例。pure metadataだけでProduct/Graph/VM/DB/keys/agent操作0。別独立postで全map/対象外/型/原counter不増/費用非変更を照合してから現行viewへ適用。原Mainの未達159L29M6Bと他5未達Sourceは担当候補化で閉鎖しない。結果2894/後続manifest。
