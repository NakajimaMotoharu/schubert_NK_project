# RO取得前marker拒否・対策

NK-OPS-001/SS343353355/SSC283/BUG1184/YKT952、PT-OPS-PG1870-RO001、716仕様。operator6d5c99dd9d468ec1765307ae6b89f3384dcaf38d、実1870stage0/22:34:00.786386Z～22:34:03.428905Z、prepare-ro1/22:34:32.626307Z～22:34:36.571624Z、logSHA04b16892344003dcfbebee1159f18b8bbca15b96c2005beccfe84561d88a64d8。fixture全81assertは0、実Java verifyInputClosureでM/A/DB/Ref/mount前拒否。

実Python preflightは終了0/PG1681_INPUT_CLOSURE_READY、実Java consumerはPG1867_INPUT_CLOSURE_READY＋LFを期待することを独立readで確定。source文字列置換の一部producer末尾を見落とした工具障害、old正常scope/RO成功に読み替えず保持。業務変更/新Root/Backup/stop/reload/Unit/current/approval/epoch/SQLwrite0。

新PT-OPS-PG1872-MARKER001：actualemitted Python printのASTliteralとJava ASCII consumer literalを独立expected b'PG1872_INPUT_CLOSURE_READY\n'へ一意照合、UUID f1772e/Root13原本/WARNING-failure/source old2741-new0fdを不変更。PT-OPS-PG1875-PRE001：directactualentryが実guest producerをowner前に一回実行し、exit0/完全stdout一致/stderr空・SHA・M/A/Ref/DB/mount0を私有safe資格へ保存してからJavaを呼ぶ。各独立1unique、計2PASS/static0。

次source固定→1873new全ABIfreeze→1875newstage→実markerprequal/prepare-ro一回→1876別fullROpost→正規publication/Unit唯一更新reload→次合法実WARNING/残PGPT。旧1870byte/slotを改変・再送0、Root/current/原本Backup/Current/stash7/privateは保全。停止条件未成立、取得前拒否だけで工程停止しない。
