# NK-OPS-001 普通採取親FD権限・署名source単体テスト仕様書

対象：NativeCoveragePrivateFile.export、LinuxDirectoryCalls.openDirectory、PG471新only運用工具。RD SYS002004/OPS009/TST004、UI212251、SS333342343/SSC193194195、451。BUG754/YKT534。PG470/d204全3328は旧source成功として保存し、新sourceへ流用しない。業務画面・電文・DB・Current/DIF・元budget・2FD・私有role0700/exec0600は不変更。

| Test ID | 目的・独立期待値 | 操作・fixture | 結果分類 |
| --- | --- | --- | --- |
| PT-OPS-NPARENT195001 | Root0711の他UID readなし、O_RDONLY directory openはEACCES | 実VM新隔離/var/tmp fixture、真正999:981、Linux固定O_DIRECTORY/NOFOLLOW/CLOEXEC | 旧不整合の再現、正式/native app代用0 |
| PT-OPS-NPARENT195002 | 同Root0755親FD、自己role700にCREATE_NEW600、literal46byte、inode uid/gid/link、sync・normal close | 上記別新親/新file、production methodでexpected生成0 | 限定OS成功 |
| PT-OPS-NPARENT195003 | 両roleの閉agent argv/output=none/INV、API既transfer維持、role専用RWだけ、null/未知/agent追加/改行拒否 | pg471_prepare_native_test.pyの手書き全文及びuid/gid/mode/type/link/dev/inoのnegative vector | 152独立assert、native操作0 |
| PT-OPS-NPARENT195004 | 同PID1/boot/INV/job/元timeboundの正常doneだけ、missing/null/他型/境界拒否 | pg471_parent_done_test.py、固定manager literalと元30min | 77独立assert、native操作0 |
| PT-OPS-NPARENT195005 | source固定fresh全6の全PT/XML/FES0/静的6zero/前後byte、line/method/class/branch全missed可視化 | pg471_full_v1.sh新40桁HEAD、JDK25.0.4/Maven3.9.12/Node24.19.0 | 旧/中断/別sourceは不算入、100未達なら未受入 |
| PT-OPS-NPARENT195006 | 正常owned逆順停止/M/A/DB/原本Backup旧5exec保全中だけRoot親711→755同inode、4新role、新Unit閉profile、両Root普通session/TERM/全kernel | 新署名・新only工具・同source frozen bytes、現D3真正cohort固定 | 未実行、native fileだけで正常推定0 |

001002 command=`python3 -B tools/quality/vm/050_s1/pg471_parent_permission_probe.py`、新fixture及び私有logはWorkPG379へ保持。003004は各python3 -B工具、005は固定source後一回実行、006は005実0及び新candidate全artifact/署名検証後のみ。環境/時刻/branch/source/actual exit/各hashは353・safe manifestへ追跡。中断・failed・skipped・not-run・full成功でも未網羅は合格算入しない。元原本/Backup/stash7/Current/privateは保全、raw exec/log/credential/DBはGitに出さない。
