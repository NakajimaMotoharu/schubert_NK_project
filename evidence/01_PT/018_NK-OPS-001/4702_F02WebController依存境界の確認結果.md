# F02 Web Controllerの直接依存境界の確認結果

2026-11-19 JST、PT-F02-ARCH-001〜012、BUG-3328、YKT-2701。PG40064の旧工具は12条件中4条件一致、JMSとファイルAPIの8条件を見落とした。PG40066、工具 `43eeb656b0fd7e0772885573eca9086420394598` で12/12一致。うち許容2、禁止10。いずれもJava 25でcompile終了0。期待違反を含むArchUnit子は両回とも真正終了1で、独立照合は両方の真正結果を照合して終了0。6合成JARを使い、24/24 classのimportを確認。別四規則の指摘0、検知用classは未初期化。

設計はorigin/mainのSS311 §5.2。Controller名または実Spring Controller注釈で識別してJMSを依存検査に含め、NIOとファイル専用I/Oの直接callを検出する。一般OutputStreamと間接Facade使用は許容を確認した。製品Core `ecf8a00fbd37720b80f8e107d59727723c706a12` 不変。通常製品PT、実行時検証、実測coverageの加算は0。F02の残条件はAPI/Webを含む同一source六実JARに対する型付き実行・照合、保留依存、全451、正式判定。

独立manifest `evidence/01_PT/018_NK-OPS-001/evidence/PG40068-f02-controller-fences-independent-v1/manifest.json`、SHA-256 `14561ac6e542dcf01dd06165d2360586e51ad8ffd0e1e9c6d175b7258d171ef7`。576／577、PGPT-20261008-6098。
