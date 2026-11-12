# P01001 既存17件と現在依存159件の通常PT

Program NK-ADM-001、UserQueryRequest/Repository/Exception。関連RD FUN009/AUT/DAT、UI225/236/241、SS312/323§9.4/324/332、451。主契約・独立期待値は4088、製品改変でexpectedを生成しない。

既存全fixture: PT-ADM-CORE001～004（原値canonical/NULL LP/入力/null）、VAL001～004（layout/target/ページ/件数の独立typed期待値）、SQL001～009（公開JDBC interface proxy、固定SQL/bind/UTC/借用connection/RS→PS close/ADMIN/null/50件）。加えて実依存の現在Protocol130、Canonical10、Authorization2を同一runで実行、全159/新定義0。DBへの接続・driver・privilege・私有reflection・actual4・Root/native・鍵ringなし。Original UserQueryRequestTest/ReplayTest/ApplicationTest/RepoTestはwhole DB/actual4 HOLD、そこからmethod抽出しない。

現在Protocol3とCanonical2変更のため同依存sourceで再資格する。Main current eac757a58のUserQueryReplay5はsource-onlyPG別証跡で、この実行には含まれずruntime未資格。通常Main whitelist192物理全体をcoverage報告し、Repository異常分岐/QueryExceptionを除外せず未網羅のまま表示、全scope100や元190/451合格を宣言しない。UserQueryRequestと依存の四counterは個別確認。

準備工具1450/PG27052、既compile0回収・helper三件の是正1452（BUG2690/YKT2367）、静的1451/27054: configuredformat/CS0、PMDraw3はcanonicalの借用field/単一thread JDBC map/standalone classloaderの各文脈を1453/27056で分類。抑制なし。元compiler失敗後に製品試験を二重起動しない。

実行: `PYTHONPATH=tools/quality python3 -B evidence/01_PT/018_NK-OPS-001/input/1450_user_query159_qualifier.py run <固定HEAD>`。JUnit1.13.4/JDK25.0.4/JaCoCo0.8.15、UTC/JST設定・command/終了コード/input/sourcehash/coverage/XML/CRC/環境は27058/独立postへ記録。期待159/FESabort0、同一source/class-CRC/session、独立期待値は上記literalとSS byte offset/bind/SQL後条件。実PostgreSQL後条件とnative/auth終端は未実行の別gate。

実行結果・coverage・エビデンスhash・BUG再試験状態は実終端と独立確認後に追記する。coverageだけのassertionや除外を追加しない。
