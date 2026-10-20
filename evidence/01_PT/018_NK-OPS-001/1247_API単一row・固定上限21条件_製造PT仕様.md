# 1247 API単一row・固定上限21条件：製造PT仕様

PG-D449/BUG1516/YKT1276/PTPRE025、WBS-F03が費用主担当。着手前見積0.5/1.5/4共有pp、全体campaign別費用は今回は発行しない。原v3v4/個別開始費/専有費nullを保持。旧source288062f39の全3973は1246で閉じて原証拠を保全、Main/Test固定解除可能。

機械可読program/class/変更condition一覧は`evidence/provisional/PG5964-api-sql21-plan-v1/manifest.json` SHA256 **56b461725810f8a706b0c1e9dd092dabf68f631a99593462bc01b7ca9784c2b8**。全16before/予測after SHA・全21findingId・token/出現回数・private int/long定数とAPI169class/1010semantic Test参照を含む。計画作成時のoracle照合未完フラグは履歴として保持し、以下で先行照合した。製造適用は本仕様/先行台帳の後。

独立根拠=SS323§2 N9/version0～999999999、SS331/332各PK・更新/監査・Inbox SQL後条件、SS351§4 details serialized1024UTF8 byte上限、各queryの単一PK/owner projection。既UserCommandServiceTestはSQL literal/固定actor/SQL後条件と監査失敗時全rollback・oversized username1024、QuestionCommandServiceTestは直接SQLでversion999999999を設定して取消/削除の独立code/状態を確認する。17 affected-count checkは同じSQL実行の直後一行を要求、0/複数を成功へ変換しない。Mediaは0/複数projectionを同じ固定例外へする。新expectedをProduction methodから生成せず、既各program PT仕様/固定SQL後条件・null/異常/fault port/境界/再送を維持する。

対象16=UserAuditWriter/UserQueryAuditWriter/UserRequestAuditWriter/LogQueryAuditWriter/QuestionCommandService/QuestionMutationAuditWriter/QuestionQueryAuditWriter/ScenarioAuditWriter/JdbcInboxCoordinator/MediaRepository/AuthSessionRevocationService/AuthSessionService/AuthenticationContextVerifier/LoginAttemptRepository/LoginAuditWriter/SessionAuditWriter。Program/RD/UI/SS/TestIDは各既source Javadoc・program PT仕様を継承（新method0）。変更Test/oracle/SQL/transaction境界/DDL/resource/POM/Current0、公開ABI不変。新sourceの全API1010/169＋六guard11/6を一回実施し、原XML/actual/branch/commit/入力fixture/独立期待・実際/counter/hashを後続結果へ記録する。

coverageは16targetのLINE/METHOD/CLASS/BRANCH各整数100・全分岐/例外/null/再送/並行の既Testを実測で照合。compile/null/SpotBugs六module0、無除外PMD raw1451→1430は予測に留め実値で判定、Checkstyle/処理error0、全851source/1666physical Mainの宣言16ownerとnested/debug差・他同byte/公開ABIを独立確認する。除外/抑制/不足counter0補完/無意味assertion/旧PT輸入なし。5962既baseline16四100/f67f7d6bは対象選定のみ、未実施新sourceのPASSではない。

実command=python3 -B tools/quality/pg5966_api_sql_selected.py、未使用WorkPG379/pg5966-api-sql-selected1021-v1、JDK25.0.4/Maven3.9.12/offline/既固定toolchain。事前定義/実169API source inventoryの純fixture三件0。初期TDDで既単純regexがDisplayName内の括弧を解釈できないことを検出し、コメント/string/textblockを字句分離してannotation引数を平衡括弧で読むローカルinventoryへ限定修正、Disabled/parameterized/factory/nested/重複/非voidを拒否。Production/Test body/元試験変更0、未完成工具fixtureの失敗をProduction障害やPT成功へ数えない。

実VM/Root/現在所有/原本/鍵/failed-cohortはHOLD、当通常PTは拒否PT代替でない。最終同source全scope/global/native/CHR/451/trace/正式1964-53/17-190/QA051final/工数nullは別未完。
