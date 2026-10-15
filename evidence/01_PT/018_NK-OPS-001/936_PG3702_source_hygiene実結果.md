# source hygieneと固定静的診断の実結果

仕様935/BUG1313～1315/YKT1079～1081、NK-OPS-001/F03・SS352/354/411/451。base実配備4856/PG3420は不変更、feature候補Main5224dd641976df502f3d1f278d73ec55f5ff9711。正式1964/53・個別17/190・工数null・QA051final保留を維持。

## 独立実証と実行結果

PT-F03-3686-001：JDK25実Compilerの純3（通常/static/継承/入れ子・shadow/未使用・曖昧/未知拒否・UTF16）、宣言/array/annotation/初期化順/for保持/文字列TAB値の純1、cwd負系純1、生成70非変更境界純1、Git source履歴の独立temp repo純1は成功。管理試験としてProduction PTへ加点0。

002/003：PG3688初回stageは末尾空classpathを拒否してactual1、原失敗/source8ec495114/payload5206acdbを保持。BUG1314先行d15c96f9a→修正69bd29efd。元全六XMLのjava.class.pathとsurefire.test.class.path/user.dir/basedirを照合、empty一つをその元module絶対cwdへ明示解決、全classdir byteを真正3712 Jarへ照合。new-onlyPG3690は2026-10-15T21:46:01.269530～21:46:33.226020Z、actual0。全849/六module/531wildcardを候補186fileへ展開、前後全resolved member/type/constructor bindingと非import宣言/literal値同一、元source不変更。原server manifest3377d69c4aca3034c273e30c35258630a724c22663760e08ed9fe462aa7ad282。

003/004：PG3692は2026-10-15T21:49:49.234480～21:50:20.989851Z、actual0。113同時宣言/282変数を分離、実体LayoutFieldCatalog（SourceLayoutFieldCatalogは誤記）の389行×7TAB=2723を同値escape、固定GJF1.36.1/skip-reflowing-long-strings適用。合計214Main（API46/batch77/bootstrap11/protocol1/storage7/web72）、全六compiler再照合0。自動分離しない889構文候補はそのままで**全849 fixed Checkstyleが0**、対象違反を除外したものではない。

Checkstyle14.3.0/原Jar SHA754e218ab1fcabb1e1c5f8530e9d3aa37636806c22987bb279dd907a6ee749b2、全rule SHAa7c6086cdb7905d55026e9d5bfbb7c81f5fb3825f73cc060d060da64e3266b75は不変更。元645（531/113/1）→新0/exit0、新report2c1b438c426339e8759a5f5cec897b42c3527bd6af324f56ea2db3e292af35f7。新candidate全manifest2ddbf3636e5a4b9c9407f2aa94bfc7bb8a0e8d4c8c4aa651d6d451f7efa5cf3b。

PG3694 stage/applyは214fileのorig/new hash、regular sourceだけのarchive、git apply --check、intent/fsync、適用後全849のexact matchでactual0。Main commit5224dd641、Currentbaseline/fixture/70再現生成artifact/上位設計/規則/generatorは非変更。元raw失敗/成功/原本を保持し、VM配備・起動・DB更新なし。

PMD7.28.0は同固定全category/priority・Java25 record修正overlayを維持して新candidate実849byteを一回解析、PG3696 PMDexit4/raw2217/processingErrors0、全23rule件数は元3422と同一。旧current3856のtyped auxは全binding同一の**限定静的解析用**で、新Main build/nativeの代用ではない。

BUG1315：Git誤pathspecで元3696のsource欄空、診断内容を消さず資格未完とした。先行62ca3978c→修正1c236cf9e、三Git箇所/独立temp repoで管理・Testの新HEADとMain identityを区別、空scope拒否。PG3700別read-only actual0で元payload/全849実入力/元snapshot1dc31941b/候補5224 Git全blob/現在byte/report ecd378617cdef6513246b475ee5f343c1f97a26e132731832490445b86123515を結合、元空sourceは保持。PMDを再実行していない。回収manifest fcb7c465e7a21fdb5ea83cc6e916e4b43c668d0753f4414eaf2d176e03a8d169。

## 再現command・証跡・未完

`python3 -B tools/quality/pg3688_import_candidate_stage.py`（修正後new-onlyPG3690）、`pg3692_hygiene_candidate_stage.py`、`pg3694_hygiene_candidate_apply.py stage`/`apply`、`pg3696_hygiene_pmd_diagnosis.py`、`pg3700_hygiene_static_source_recovery.py`、`pg3702_hygiene_public_results.py`。環境PYTHONPATH=tools/quality:tools/quality/vm/050_s1＋既存pyflakes3.4.0、JDK25.0.4/Maven3.9.12の既toolchain、追加installなし。再実行指示ではなく、全new-only原command/時刻/終了/入力hashは各PG379/実server manifestに保存。

公開PG3702-hygiene-static-v1は全849 source SHA・変更214 SHA・全六semantic proof・Checkstyle/PMD・原診断/独立recovery hashを保持。raw DB/token/credential/nativeは含めない。005（新Main全体回帰/native/四100/CHR/451/trace）未実行。Checkstyle0はF03全0ではなくPMD2217の適用性・是正が残る。BUG1314/1315は有限工具scope再試験完了、1313は修正済/後続全体未完。通常小受入で停止しない。
