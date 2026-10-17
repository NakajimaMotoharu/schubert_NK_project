# 694 PG4956/4958 Expiry既成功監査・JDBC所有scope実行結果

仕様693/SSC304、BUG1396/YKT1162。PG4956元session97981 actual1はpreflightだけで終了。source c5e68f542、Main pathspecが子孫を含まず空列、strict差分検査で拒否。WORK/source/archive/Maven/PT未生成・未起動、当候補の新16PTはnot-run。format/static/coverage結果なし、全体合格へ加算0。終了は枠不足/PGPT完了ではない。

修正は明示再帰glob/actualGit独立試験を追加し、元拒否は正常化せずnew-onlyPG4958へ。実Git正一件/空・余剰拒否/namespace検査を経てclean corrected commitを固定する。PG4958 actual終了code/XML/時刻/command/coverage/Mainbyte・static/結果hashは取得後追記。Production配備04bb/PG4860・旧全3761/551/native80は不変更で歴史資格、候補へ加算0。秘密/rawSQL/credentialを保存しない。

PG4958実結果：元39781 actualMaven1/資格1、source9cf56bdff5cf44ef8d067721a37c8bd59a1d574b、03:02:46.788380～03:03:56.807314Z。51PT/7suite・FES/flaky/notrun0、format0、storage/bootstrap static0、batch OBL二件、log82092d47482040f37c3814771a032a59df3c799b7f4763fb43aa59ea2bca1735。新16PT成功、verifySuccessfulAudit8line/1method/10branch・usingJdbc12line/1methodは全miss0（後者BRANCH非適用）。元条件body$2は20line/1method/8branch全miss0だが工具が無条件$1へBRANCHを要求し拒否。BUG1397/1398/YKT1163先行後に明示ownership/type＋actualbodyへ是正、新PG4960へ。旧51成功部分をgate合格へ変換せずMain差資格も当runでは未実施。

PG4960元91540はactualMaven1/資格1、sourcefece2e8a49bb55cee22a3c5127de1c164696d1b0、03:06:30.035993～03:07:07.933893Z。誤WillClose packageでcompile拒否、14PT2suiteのみ、新18not-run・batchcoverage/static未実行、format0/log9a466a24。BUG1399先行後actual JARのjavax.annotation.WillCloseへ一箇所是正し新PG4962へ。旧失敗は原snapshot/log/XMLと保全、合格へ加算0。依存追加/ルール抑制0。仕様693の最終commandはpg4962_expiry_success_selected.py（53PT7suite予定）。

PG4962元10176/source8ffe6876e、actualMaven1/資格1、03:08:25.696804～03:09:14.257434Z。Main compile成功、test helperのnested nullable位置でtestCompile拒否（BUG1400/YKT1164）、14PT2suite/新18not-run・batchcoverage/staticなし、format0/log66464809。javac実診断からtest型表記一箇所だけ是正しnew-onlyPG4964へ。Main bytes/期待値/検査要求を変更しない。最終command=`PYTHONPATH=tools/quality python3 -B tools/quality/pg4964_expiry_success_selected.py`、実結果追記待ち。

PG4964元61751/sourcea8a09d7f88268131107c3b75705ba528efeb3041、actualMaven1/資格1、03:10:37.645376～03:11:51.354427Z、53PT/7suite/FES0・format0、batch static二件はOBL_UNSATISFIED_OBLIGATION_EXCEPTION_EDGE、log87583063ea26edb950b680f7e41757d49a732d108a0ce753ab3bff3173cfffe5。実helper13line/1method、pure8line/1method/10branch、rowbody20line/1method/8branchは全miss0。qualityは不合格、raw元全保存。読み取りbyte診断も厳密guardで拒否：外側＋record三class変更/新二宣言、後三件はformatter起因の非debug disassembly全同一（BUG1401）。event1122の749不変という誤記は訂正1123を追記し、成功へ読み替えない。

477の限定ultraレビュー一名/read-only（追加spawn/VM操作0）でcallback構築gapを確認、SSC304追補をmainPR151へ反映。factory所有/新24PTへ是正後newPG4972へ。既成功51/53やpartial14を新sourceへ合算0、旧04bb/native80不変更、当候補のwhole/native/正式は未完。
