# JDBC UTC境界 横展開実行結果

PG160/057/SSC056、BUG167～170/YKT128～131。現時点は関連探索103件成功であり、全体正式認定は未完了。SQL新10件（DB241～250）・Batch新8件（BAT082～089）を正式02の1205件に遡及追加しない。

修正前反例、対象23class一覧、例外境界6箇所・追加MIN/MAX、故障注入各位置、探索command/環境/終了code/hashと横展開の対象外理由は[evidence/run-references/logs/BUG-167-YKT-128.md](evidence/run-references/logs/BUG-167-YKT-128.md)。正式run/source/4coverage/静的解析/結果/manifest hashはクリーン実行後に記録する。Current baselineを変更せず、実NK CHR/IT/ST完了を宣言しない。
