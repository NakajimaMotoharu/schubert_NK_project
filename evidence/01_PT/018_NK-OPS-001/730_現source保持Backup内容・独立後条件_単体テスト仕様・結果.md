# NK-OPS-001 現source保持Backup内容・独立後条件

## 保持handle/後続skip是正（2026-10-13 12:02JST）

2064readOnlyactual1/operatorc82db1019/UTC02:58:19.622110→25.170913：旧manifest oracleが同run-step単一行を要求し、合法resumeの後続SKIPPEDを拒否。BUG1205/YKT973へ先行起票、旧slotと失敗を保持。新2066独立oracleはmanifest id/attemptの元SUCCESS一件を厳密選択、後続rowは別id/attempt・同business date・ALREADY_SUCCESSFUL/SKIPPED/全4counter0・started=end・content完了後だけ許可、未知/重複/逆時刻を拒否する。元canonical/hash/owner/byte/SQL後条件を変更しない。歴史1259全negativeも保持、独立2PASS（旧1＋新1）、新2068はfullclosure/entry構成PTを追加した別readOnlyslot。Backup/restore/start/prune/SQL更新0、実2068未実行。command=`python3 -B tools/quality/pg2068_retained_backup_replay_history_post.py`、W同slot manifest。全品質/正式は未完。

PT-OPS-PG2064-BACKUP001、OPS009/UI251/SS341343354/QA047/SSC283。currentProductionSource0fd734195b4d5338f6b7e860e087cce561d49562/PG1846、既run4148e3e8-f107-431a-ab27-d6e6d1f1772e/cutoff2026-10-12T18:20:32.598894Z。元BackupはPG1638で作成した保持原本、参照templateもその版を保持し当PG1846との役割を混同しない。

前提：2062actual0/一回用runtime退役・全資源0、2051資格済17工具/元全24-32-187のSHA。操作：別current全post/十Ref内で既manifest・物理file三件をNOFOLLOW/owner属性/hashで三読、DBbatch後条件/SS独立manifest oracle、config.tar allowlist8と正規signed/effective・承認済fixture oracle、pg_restore --listのみ。期待：全元資産保持/crypto header/size-hash/DB件数・run/cutoff/profile/recipient一致、正常Unref/close、Backup/start/restore/prune/SQLwrite0。秘密key・credential/archive実体・dump-listはGitへ出さずhashだけ記録。

独立source境界PT1PASS/生成actual全静的0、当sourceMain変更なしにつき重複全Maven不要。実2064は未実行。commandは既PYTHONPATHで`python3 -B tools/quality/pg2064_current_retained_backup_content.py`、clean固定source必須。結果manifest=W/pg2064-current-retained-backup-content-v1/manifest.safe.json、失敗時は障害先行/旧slot保持/実Backup再送0。正式1964PT/53scope/全leaf0/coverage未完、IT/ST未実施。
