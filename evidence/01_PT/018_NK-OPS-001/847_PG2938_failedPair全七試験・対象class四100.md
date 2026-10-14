# 847 BackupFailureSnapshot全七試験・限定counter

Program=NK-OPS-001/BackupFailureSnapshot、SS341/343/354/355・451。Production Main=a9cb0ac9a、Test追加fd30f2be979af4ccae20a3637cce07bff99ba7e0、branch dev-foundation。PG2938/session46226は実行済み、下記は既存結果のtrace補記で再実行していない。

TestID→method:

| TestID | class内method・観点 |
|---|---|
| CFDB001 | cfdb001ActualBothLatestFullRowsAreReadWithoutMutationAndLockIsMandatory: 実DB二行/全14列/lock必須 |
| CFDB002 | cfdb002LatestIdentityAndEveryTerminalColumnRejectMismatch: 全列/terminal/最新identity不一致 |
| CFDB003 | cfdb003SnapshotInvariantUsesActualPairNotAFrameCertificate: constructor actualpair invariant |
| PT-CFDB-2916-001 | cfdb2916001FirstAndFinalIdentityDriftRejectWithoutMutation: 初回・最終identity逸脱 |
| PT-CFDB-2916-002 | cfdb2916002EveryNullColumnAndMissingResourceIsBounded: 14typed列null/statement・rows欠落 |
| PT-CFDB-2916-003 | cfdb2916003PairRejectsEqualIdAndForeignRunAtConstructor: equalid/foreignrun |
| PT-CFDB-2936-001 | cfdb2936001ProviderExtraRowRejectsWithoutCertifyingOrMutatingPair: malformed providerの余剰二行目 |

期待値はTest内literal fixture/独立SQLの全14列で作成しProduction methodから生成しない。実ローカルPostgreSQLでborrowed transaction/advisory/identityを検査、provider異常は実ResultSetへ限定proxy、元二row/SQL/関係資源の不変を独立再読する。null/未知/境界/異常を正規扱いしない。

```sh
PYTHONPATH=tools/quality:tools/quality/vm/050_s1:/home/mini/codex/project1/work/toolchain/pyflakes-3.4.0/runtime python3 -B tools/quality/pg2938_extra_row_selected.py
```

実結果: 全7/FES-aborted-notRun0/actual0。既2930の同Main host exec＋当selected execで対象classだけLINE63/METHOD4/CLASS1/BRANCH56全missed0。native輸入/VM操作0。新七Test集合の全体回帰は未実行、当class四100を全PGPT/正式や全体残数へ直接加算しない。

証跡: 私有PG379/pg2938-extra-row-selected-v1/manifest.safe.json、LAN manifest177219335b3ef96acd4e4f836706020268e65596e5e8cc281c3f4a540479a932、payload b1b5dca24bdb3f5d5f814f73d086a8a8758b08cf5662aa4c2383dc0608b72e67、XML e730d4d8e557bab31553763b25cb5e52419fda20216cff2089f29ca9bd470631、coverage XML4c880ad6633fef0adecce6e26d21e7a1c26effa3b74b6afe13136536baf34c6b、exec23f92a9a51bec6ccc8da94fbf1da6df82b2946e473623b5f18b9a633595db554。環境JDK25.0.4/Python3.14/既PGPT PostgreSQL fixture、実日時/command/対象sourceは同manifest/input。既BUG1251対象null/複合closeのwhole資格は846、ここで新障害を捏造しない。秘密/DBrawは非格納。
