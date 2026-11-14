# NK-DAT-001 V030音声role互換・DDL単体仕様

Program NK-DAT-001 / WBS-P004-01、費用は共通原因BUG2943のWBS-P01903へ一回帰属。RD MIG003005006/DAT004/TST、UI223242254、SS311331343/SSC396397、BUG2943/YKT2472、識別訂正BUG2945/YKT2474。V030と030 rollback templateが対象。PG32606の旧V001..029 hashと3046独立SQL golden、PG32654現在Program/SQL body hashが独立期待値。

静的確認ID PT-DB-AUDIOROLE030-STATIC001..005: 001旧29SQL byte同一、002前進三DDLだけでrole varchar11/byte1..11、003切戻し七statementと明示TX/ACCESS EXCLUSIVE/既値>8なら固定RAISE、004無切捨て/改名/role-grant/他表列変更0、005正規Program/owner/source/artifact hash/Java39入力同一。これはsource静的確認で製品PT PASS・実測coverage・実DB安全を意味しない。

実DB Test ID PT-DB-AUDIOROLE030-001..008はすべてNOT_RUN_HOLD。前提は拒否HOLD解除と既正規auth/所有/隔離scratchDB・元Backup/全schema snapshot・承認済みsource/BOM一致であり、本資料が実行許可を発行しない。001 V029→V030/Flyway history030正常一回・旧29checksum不変、002実型varchar11/byte CHECK1..11、003movie_audio11保持/他列不変、00412byte拒否/NFC/NULL契約、005PK/UK/FK/index/role/grant/24table/75制約/原本不変、006>8byte存在時rollback全体拒否・値とschema不変、007<=8だけの隔離DBで元型/constraintへ原子的切戻し、008中途失敗rollback/再実行/競合lock・全connection/transaction返却を確認する。期待は明示catalog/postconditionと独立literal/前後snapshotで算出、Production methodから生成しない。

将来の実行は既正規DB試験経路のsource固定commandを当時のfresh認証後に記録する。client ON_ERROR_STOP=1必須。原本DB/現稼働server/未認証DBへ試し実行しない。DatabaseMigrationTest/MigrationInventoryはV030/30へsource更新済みだが本scopeではcompile/runしない。実行日時/環境/branch/対象commit/command/終了code/input/期待actual/DB後条件/coverageを取得してからmanifestとBUG/YKT再試験を更新する。現時点はcommand未発行・exit/実際DB結果/coverage=null、未実行を合格へ算入0。
