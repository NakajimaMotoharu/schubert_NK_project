# NK-OPS-001 検査起動wrapper・unit 実行結果

正式PT-WEB-20260909-40/source2dfbaaf533012c4720d1626241ec6243b74d7fcd、dev-foundation、2026-09-09 19:22:08～19:29:08 JST、exit0。新8 PT/全1067件PASS、failed/error/skipped0。6 Java module4coverage100%/Production5静的解析PASS、35scope/12collector/14負canary同run・source・hash一致。evidence/manifest.json SHA-256 `532cdffe87f8577fe7616b973e32571df614ab7192897657ff5d57f1f38865bc`、root manifest `5bf54aa70ad4e01eafc570202447c70ac19ee8c670396538b3449af405777dc6`。実sh・ShellCheck0.11.0/systemd-analyzeの50呼出しをlogs/method/連番.jsonへ記録。shellの全statement/条件/JVM成功・失敗/od成功・失敗/4code/defaultをmatrixで確認、class/methodは非該当でJava値を流用しない。全base directiveとprevious4profileの構文/値を確認。実unit起動・root credential配布/親OS/backup gateは未完了。BUG136/137/YKT107/SSC053の対象再試験は完了。以下は探索履歴。

001/PT-OPS-INBOX-001～008、SS341/342/343/352・SSC-049/053/PG-D-144。実装・探索8 PT成功、正式全体回帰/独立scope/trace/hashが揃うまで合格に算入しない。19:00:57 JST合同探索3は20件成功。実systemd配布・親OS/backup gateは別未完了。

探索1（18:53:05）はSC2194 1件で19/20成功、BUG-136をdc8215d7で修正前起票。専用変数へ固定値を入れ、抑止なしで探索2（18:54:55）20件成功。NUL追加探索は壊れたreceiptをexit0としたため1失敗、BUG-137/SSC-053/YKT-107をe20a45f4で先行起票、SS937cb33c後に全byte hex検査へ修正。探索3でNUL16位置/高bit/余分LF/od失敗/JVM異常/実Java負例・ShellCheck0・baseと4profileのsystemd静的verify成功。失敗runは正式合格に算入しない。正式39予定。
