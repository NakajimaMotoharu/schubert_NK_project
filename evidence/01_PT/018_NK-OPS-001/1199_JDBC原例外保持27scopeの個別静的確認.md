# PG5770/5772 原例外保持27scope・54診断

WBS-F03、source9463、SS312/331/342・SSC063/199、元3932資格1196。開始.25/1/3pp維持、N/T/専有費/工数率null。対象の既PGは、catchで原Throwableをlocal primaryへ保持し同一instanceをthrow、finallyでStatement/ResultSetを閉じ、承認済みJdbcResourceFailures.replaceへ渡す27scope。捕捉を削除すると既知/未知/fatal/close優先順を失うため、警告消しのためのProduction変更はしない。

事前区分PT_DEFAULT（工具fixture/型解析のみ）。全849actual Main/当1664classと第三者Jar/annotationを固定、-proc:none -implicit:noneのJavac分析でProductionコードを生成・実行しない。DB/VM/Unit/原本/Backup/鍵/intent/permit/失敗cohortへ操作0。全回帰/PMD確認再演0、拒否PT代替0。

1. PG5770/40355 actual0、既独立catch fixture1成功/Javac lint-Werror0/全849current型解決、1090catch factsを保存。manifest **63e865210e51cdb6dcae78f0784d970b1bc1fa38aae403acab4f9e843b69d7e5**。単にfactsを得た段階では適用性未判定。
2. 元PG5592/JDBC typed27shape（manifest **f19448f741d78ef78472744f45dc07f4e0427943a1c46260c7538810b6ee9a33**）は古いPTではなくコンパイラによる厳密構文・symbol事実である。全27のsource hash・全owning classbyteとhelper byteが現在と一致した範囲だけ再認証。旧PT成功を輸入しない。
3. current catch factsと、二statement `localPrimary = caught; throw caught;`・直後のfinally開始行・exact Throwable local/null初期値・同resource close・正規helper/二argument・同secondary再throwが一致する範囲だけ結合。return/別exception/wrap/他代入/任意call/ finally無しは単体negativeで拒否。
4. RuntimeException/Error各1、計54診断を全source座標/型/所属method・当wholeのown suite＋JdbcResourceFailuresTestへjoin。SQLやIOException等の別診断、catch終了依存、残61以上の異なる形状はこの根拠で免除しない。

command: `PYTHONPATH=tools/quality:tools/quality/vm/050_s1:<pyflakes-runtime> python3 -B tools/quality/pg5770_current_catch_facts.py` actual0、続く `... pg5772_primary_capture_review.py` actual0。工具unit1成功、最終pyflakes0（初回未使用importを除去して再確認）。修正製造/新Production PT/実測coverage増0。

公開`evidence/provisional/PG5772-primary-capture27-v1/manifest.json` SHA256 **b22a70787187534deadba238364e708c3fd749ceb456392795b5e11a81cff487**、同`decisions.json` **ae131abf937b0c0ccb8cf9f900ee1efa667d1229b1c582cc0f8b79b8956d4e87**。各27source/method/catch行/finally型fact/body hash/当class/元caseを保存。全1582を再コピーせず、元PG5764＋PG5768＋本54のimmutable overlay、元診断の削除/書換0。

新個別根拠54、累計473（CONTEXT261/REQUIRED208/FP4）、未review1109、生1582保持。**F03/全体coverage/native/CHR/正式は未受入**。広域generic catchを一括免除せず、当27scope以外は保留のまま後続PG/PTへ継続する。
