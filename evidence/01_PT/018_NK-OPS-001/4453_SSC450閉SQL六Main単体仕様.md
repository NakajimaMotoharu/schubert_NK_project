# SSC450 閉SQL六Mainのliteral実行境界・単体仕様

Program NK-MIG-001、canonical owner/cost WBS-P019-03、受領F03。BUG3132/YKT2603。対象: AssetStagingTables、MigrationMasterColumnVerifier、MigrationMasterConstraintVerifier、MigrationMasterContentVerifier、MigrationMasterFinalizer、MigrationMasterReferenceVerifier。追加必要依存Aのみ.4/1.2/3.6pp cap4、元F03 C残2.4、S/V元上限・原見積りを変更しない。内部表現の補足はSSC450へ登録しSS311/354/main反映後にPGする。Master実体/DB/Backup/鍵/VM/native/Root/QA056四型の操作は含まない。

LITSQL-001: 固定表/列/ORDER/DDL/query全byteと実行順を不変にし、private stateless SQL操作をclass初期化時に固定登録する。各JDBC呼出位置にcompile-time constant式を直接置く。共通可変registry、外部SQL選択口、SQL難読化、suppression/解析filter/flag緩和は追加しない。Assetの三表prepare/count/insert、Column/Constraint各六query、Content七query、Reference六count＋全inspection、Finalizer五MAX/五setval/六ANALYZEとconstraint phaseを全件対応。旧sourceとのSQL等価証明は補助であり、PT期待値をproductionから生成しない。
LITSQL-002: 元whole TestはAsset32・Column26・Constraint22・Content29・Finalizer30・Reference21＝160。既独立literal SQL/metadata/row/固定hash/順序/timeout/fetch/bind/例外identityとclose counter/借用connection非操作/null/並行fixtureを保持し、Test本文・期待値を実装へ合わせて変えない。入力DTOの構築は入力fixtureであり検証本体の期待生成へ使わない。whole helper Testが必要なら原本を全件含め、source closure・追加件数・根拠を製品実行前に確定する。正常/境界/負/例外/並行の既Test ID全件を独立結果XMLへ一意対応する。
LITSQL-003: 取得済Statement/ResultSet/PreparedStatementは元scope/順序/一次例外・suppressed規則・null検査/固定診断を維持。callback登録は所有開始前、一SQLごとの可変state/新規callback確保をしない。新private関数型の真のNoCodeも物理集合に残す。DB実接続・実移行・性能・heap OOMEはこのメモリ単体で確認済みとしない。
LITSQL-004: 同sourceのRoot NullAway/lint-Werror/全CS/PMD全site・SB0/解析error0/missing0/全physical ClassStats、whole160＋必要helperのF/E/S/flaky/not-run0、CRC/init/XML/未filter対象六sourceのline/method/class/branch100と全共通helper未達を明示する。除外/旧exec合算/試験からprivate ctor呼出で100を作らない。全六sourceの公開APIと不変source/必要byteを照合する。
LITSQL-005: 独立postはsource/Unit/各TestID/SQL literal corpus/actualcommand/exit/input+log+XML+coverageSHA、原Raw8/原成功歴史証拠と新結果を区別する。Source/Core/Unitの境界を分離し、program全体受入にはF02/F03・原本/QA051 final・実移行後条件を別途照合する。今回の六局所成果を元P01903/元190/全451へ自動昇格しない。

実行commandは確定closed profileと同run manifestへ保存する。期待値は各既Test fixtureのliteral SQL/row/JDBC後条件及び承認SS/DDLに由来、同production methodを呼びexpectedを作らない。BUG3132/YKT2603は実PT・静的・独立postの対象全件が揃うまでOPEN。通常製造/PTを続け、定型報告や小受入を停止理由にしない。
