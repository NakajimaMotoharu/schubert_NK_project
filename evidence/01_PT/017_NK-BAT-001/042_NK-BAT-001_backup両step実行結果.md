# NK-BAT-001 backup両step 実行結果

正式PT-WEB-20260913-12、source 2abb30ff800edd3e3fe68d3f9fe73de062c6bba8/dev-foundation、2026-09-13 08:53:53～09:09:54 JST、Maven15分59秒/exit0。全1391 PT（Protocol80/Storage58/API660/Web241/Batch311/CHR41）、failed/error/skipped0、6 Java module全line/method/class/branch100%、5 Production static未解決0。既存3固定pathの限定レビューを維持、coverage除外なし。15collector/38scope・38負canary合格。Batch全88class/452method/2779line/1503branch missed0。

BackupStepRepository、独立14列とread70/new240/replay70・全380故障位置、UTC/JST・NULL/不明pair/同接続rollback/別接続並行を認定。対象1class/9method/81line/64branch missed0。BUG191～194/YKT151～153は045の全14所有者の修正/非該当・追加130複合と元2反例を含む全回帰で完了。SSC061はこの両step DB境界を完了し、生成/信頼reader/実backup/7世代/親は別未完了とする。

commandはwork/pgpt_foundation_verify.sh PT-WEB-20260913-12（固定JDK25.0.4/Maven3.9.12/PG18.6/JDBC42.7.13、421参照）→019/017 negative→018全scope収集/validate。evidence/manifest.jsonへ実行日時/対象source/branch/環境/command/終了code・sourceFiles hash/全files hashを記録。独立expectedはinput/backup-pair、actualはoutput/backup-pairの同Test ID、全PT結果はoutput/results.xml、coverage/batch-jacoco.csv/xml、logs/BUG-191-194-YKT-151-153.mdへ対応。

PG169 reader16件は設計だけで、この1391へ算入しない。実NKCHR/IT/STとPGPT工程全体の完了ではない。

以下は起票時の履歴。

PG168/SSC061・PT-BAT-210～217。仕様のみ先行、未実装・未実行・認定加算0。全PGPT完了・実backup生成・親結線・IT/STの完了ではない。
