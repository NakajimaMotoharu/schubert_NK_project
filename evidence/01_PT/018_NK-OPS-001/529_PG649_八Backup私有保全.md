# PG649 正規保持期限再試験前の全八Backup私有保全

NK-OPS-001、SS341§Backup保持/343/SSC230、BUG897YKT666/PG648後条件、WBS-N15.04既予算内。PG649-C001は固定PG647after9435…/current36fe/全Backup metadata9・hash/NOFOLLOW/新slot/操作0を純生成compileと独立bindingで確認。PG649-R001は全13childdir/38file（八成功bundle各4file＋五protected領域の既file）をRootreadonly、各read前後metadata9/hashと集合不変を検査して私有archiveをhost0600 new-onlyへ保存。archive全52entry/38payload＋catalog/13dir、各名/type/mode/size/hashを独立tar読取で再確認する。旧7世代archiveも保全、Gitへdump/master/credential実体/catalog/rawを格納0。archiveは後続の正規最大二世代削除前に完成するが、これ自体削除権限や保持期限合格ではない。

command `python3 -B tools/quality/vm/050_s1/pg649_binding_test.py`、実 `python3 -B tools/quality/vm/050_s1/pg649_backup_preserve.py`。新private=work/pgpt-vm/private/pg649-prior-eight-backups.private.tar、safe=work/pgpt-runs/PG379/pg649-backup-preserve-v1.safe.json（actual/files/bundles/protected/SHA/bytes/serverMutations）。現実未実行、正式/native/PT工程加点0。
