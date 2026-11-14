# Scenario二表転記・独立20仕様

NK-MIG-001/MIG003005006/MIG-DAT004005/DAT004/FUN004、UI254、SS311/331/34310.1.4 SSC353、WBS-P01903.02。

SS34310.1.4の二temporary stagingから初期target二表へ、既ScenarioStagingTablesにtransfer(Connection,int expectedFiles,int expectedEntries)を追加する。callerは既認証migration actor/排他単一Connection・同一transaction/実COPYが当宣言datasetと一致/他全table・参照・NFC型・asset等の前検査を保証する。expected件数は独立manifestの非負int、file0でentry正は拒否。部品は借用ConnectionのautoCommit=falseを必須とし、新しい接続/URL/driver/権限/commit/rollback/closeを行わない。既prepareの二SQL/診断/APIはbyte不変。PG SDK実行/実DB操作HOLDを解除しない。

一Statementを所有し30秒queryTimeout。固定順にtarget schubert.script_files count0、script_entries count0、staging pg_temp.nk_mig_script_files count=expectedFiles、nk_mig_script_entries count=expectedEntriesを確認。その後固定列のINSERT INTO schubert.script_files(11列) SELECT 同11列 FROM pg_temp.nk_mig_script_files ORDER BY game_id,display_order、続いてscript_entries(12列/generated body_search除外) SELECT 同12列 FROM pg_temp.nk_mig_script_entries ORDER BY display_orderを実行。各update countは宣言件数と一致必須。最後に両target countが宣言件数と一致することを確認する。schema/table/列は定数のみ、入力からSQLを生成しない。IF NOT EXISTS/DROP/DELETE/再実行/修復/業務Consumer登録を追加しない。既存target行、件数違い、途中失敗、close異常は成功にしない。callerがtransaction全rollback/discardを行う。

scalar取得はnonnull ResultSet、一行存在/getLong(1)/wasNull=false/宣言countと完全一致/次row無しを必須とする。ResultSet毎にtry-with-resourcesで終了し、単一Statementも全success/SQL/Runtime/Error経路で終了。null Connectionは既固定input IAE、負件数/不可能件数は固定input IAE、null Statement/ResultSet/不正結果は既固定SQL診断。元SQL障害/主障害とclose障害のJava抑制関係を保持する。SQLや生値をloggerへ渡さずtoString固定redacted。targetのFK/CK/UK・identitysequence最終化/他master/ANALYZE/全migration/実DBの正しさは別条件であり、当二表のcount成功から推定しない。

新PT-MIG-TRANSFER001..020: 全SQLと八操作順の独立literal/正常count、空宣言とintMAX値、null/負/entryのみ/autoCommit拒否、null Statement、六scalar各位置のmissing/null/mismatch/extra/nullResult/executeQuery SQL/getLong SQL/next SQL/close SQL、主SQL+close抑制、二insert各非一致と元SQL失敗、ownedStatement終了/借用Connection非変更、失敗後別正常入力、fixedredaction、finite8worker64task/Future5/finallyshutdownNow-await10。全てJDK JDBC Proxyのメモリだけでdriver/DB/file/socket/Root/native/aru操作0。旧STAGE001..018の全assertionは変えず、必要whole38/1Main/1physicalを同source通常Root静的/NullAway/lintWerror/一exec/独立CRC-init/XML/四100/実Codeと照合する。元成功18の確認目的再演ではなく、この同class横断変更の必要回帰である。

追加不足1.15/3.45/6.9未較正を、詳細+PG新20 .8/2.4/4.8cap5、必要normal38 .35/1.05/2.1cap3に分離する。元費用/SV上限保持、専有費・実token null。実DB/COPY SDK/全ETL/Rootnative/CHR/global451/ITST/全HOLDは未受入。
