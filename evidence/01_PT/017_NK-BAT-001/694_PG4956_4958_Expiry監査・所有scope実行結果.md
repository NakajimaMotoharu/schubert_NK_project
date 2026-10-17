# 694 PG4956/4958 Expiry既成功監査・JDBC所有scope実行結果

仕様693/SSC304、BUG1396/YKT1162。PG4956元session97981 actual1はpreflightだけで終了。source c5e68f542、Main pathspecが子孫を含まず空列、strict差分検査で拒否。WORK/source/archive/Maven/PT未生成・未起動、当候補の新16PTはnot-run。format/static/coverage結果なし、全体合格へ加算0。終了は枠不足/PGPT完了ではない。

修正は明示再帰glob/actualGit独立試験を追加し、元拒否は正常化せずnew-onlyPG4958へ。実Git正一件/空・余剰拒否/namespace検査を経てclean corrected commitを固定する。PG4958 actual終了code/XML/時刻/command/coverage/Mainbyte・static/結果hashは取得後追記。Production配備04bb/PG4860・旧全3761/551/native80は不変更で歴史資格、候補へ加算0。秘密/rawSQL/credentialを保存しない。
