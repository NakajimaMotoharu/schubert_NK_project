# 試験DB fixture SQL異常・修正前PT

## 修正前原結果（2026-10-22）

両source3f785147ae7f2dace5bb79a6d5a16cd0de458289/archive7e5016f44d3af2c086c0f29970ae5fdee4793505d1fd4a3867e8a1c14cde0f75固定。bootstrap元run pg6922-db-fixture-red-bootstrap-v1/session47155は真正Maven1/phase001、実8件4suite（宣言15/8の残7/4はnot-run）、静的完了protocol/storageだけ。batch元run pg6922-db-fixture-red-batch-v1/session21521は真正Maven1/phase001、実15件8suite、静的完了五module（batch未実行）。両observerは既終了、sessionの再pollはunknownで再付着・再起動しない。

両元XMLで新三methodの正常24表/接続role/明示stopと設定null/空/blankはPASS、002だけが「confirmed started fixture must stop before constructor failure escapes」のPID残存AssertionFailedError。finallyのown dataDir/PID/command/user照合・通常stop0後にA02/B02それぞれownedResidualStop=trueを確認。各slotの旧失敗・自己生成原入力は私有保持、旧失敗の合格化0。

独立原reader6926は全archive入力固定・Production851/物理1669同値・同source・上記一失敗/markerを照合しexit0。公開manifest `evidence/provisional/PG6926-db-fixture-red-original-v1/manifest.json` SHA256=97db1cbbeefa2a43961686b891d15b82fc34579ceb431f93f9aa2f8b8267693d、各元XML/hashを内包。初回readerはCharacterization四Mainまで混入した855対851でexit1/manifest無し（BUG1634/YKT1387修正前登録）。src/境界へ是正、管理五/pyflakes0、元試験を再実行せず実二原資格成功。読取toolの再実行はPT件数に加点0。

これでBUG1633を実再現できたが、SQL後cleanup是正・greenは未実施。以後両新Test bytesを固定し、fixtureだけknown-start後catch/stop/元例外・割込保全へ修正して新only green21/10へ進む。Production coverage対象無しでtargetFour100=null、正式/個別受入/工数率は不変。

1513/BUG1633/YKT1386/PG-D514、F02群.4/1.2/3ppを先行、fresh86/残14のraw reset2864/2865観測は別保存・同窓/実費推定0。Production Main/旧assert/gates不変更。二fixtureへrepository引数portと開始前null/blank検査だけを導入し、SQL/Flyway後のcatch/stopは旧未修正のままで再現する（この段階を完全是正としない）。

新BatchFixtureOwnershipTestとApiLogFixtureOwnershipTestは各三methodで1513のB01..03/A01..03に対応する。正常schema期待値はDDL上のschubert20表＋schubert_web_session4表の修飾名24件を固定列挙し、adminのinformation_schema BASE TABLEのソート結果へ比較する（table listをproduction methodから作らない）。通常接続roleはbatch=schubert_batch、bootstrap=schubert_app。SQL異常fixtureは自己生成repositoryに固定SELECT 1/0、SQLSTATE22012を期待。

SQL失敗の結果としてPID fileが残ることをassertFalseで反証し、finallyは当dataDirのPID file NOFOLLOW/内記dataDir/現process command postgres・argvのdataDir/同file所有userを照合してから当一時clusterだけpg_ctl fast stopする。stop exit0とPID file消失後だけ安全markerを出力し、redではownedResidualStop=true、greenではconstructor自身のstop後にfalseを期待する。markerはTest ID/booleanだけで、PID/port/raw secretをGitへ保存しない。TestはCleanupMode.ON_SUCCESSで、失敗時の自己生成data/input/logをprivate slotへ保全する。実配備/VM/Root/cohort/鍵/permit/Unitへアクセスしない。

修正前はbootstrapでMavenが先に失敗するとbatch依存moduleへ進まないため、red-bootstrap（Api新3＋六guard12、宣言15/8）とred-batch（Batch新3＋六guard12、宣言15/8）を同source・別fresh slotでそれぞれ一回実施する。別moduleの同じ失敗対象を再試行するのではない。未実行module/静的解析を完了扱いにせず、二つの元XMLと当cleanup markerを独立収集する。greenは同新Test bytesを固定し、両新6＋既Web3＋六guard12=21/10で一つに束ねる。

test_support_profileは全Main1669/format-beforePT/compile-null-Werror/六module selected/static/実case inventoryの判定を維持する。Test fixtureだけが対象なのでProduction coverage targetは空・targetFour100=nullであり、空集合を100%としない。既Main coverage/正式1964/53/canonical17/工数null・全HOLD/PTALT代替0不変更。

format/skipTests compile0、管理三/工具pyflakes0を確認済。現時点で新red/greenの実PT0、Source/終了code/元XML/hash/当PID終了後条件は真正実行後に追記する。開始未確認の外部processを推定stopせず、実行中sourceを変更しない。次は保存pushclean→6922 red-bootstrap一回→元結果→同source red-batch一回→両原資格→SQLcleanup是正/同oracle green、通常小群で停止しない。
