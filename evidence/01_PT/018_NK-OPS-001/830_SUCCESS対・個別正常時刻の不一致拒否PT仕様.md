# SUCCESS対・個別正常時刻の不一致拒否PT仕様

実2788/Test065de4bea/session47017 actual0、一JUnit二入力/FES-aborted-notRun0/javac0。追加coverage0：927/928の実gapは時刻比較でなくTWR closingのcompiler-generated ifnull（javap実bytecodeで確認）。日時対の拒否は既網羅済みだが当独立oracle強化として保持し、未網羅二branchの完了へ加点しない。actual同union残786/156/9/529不変、successfulBackup B22covered/2missed/L36M1全0。独立XML-case/hash資格は追補、null resource契約は別群で実再現し、除外・NPE正常化・人工到達で閉じない。

PT-MDB-2788-001、NK-BAT-001、Session.successfulBackup927/928、MorningDatabaseSessionTest.mdb2788001SuccessfulPairRejectsDifferentStartAndEndWithinValidBounds。主担当WBS-P017-01、RD BAK/OPS009/DAT009、UI251/253、SS331/332/341/343/SSC116/134/451。二個別rowの妥当性とpair一致の条件を分け、旧大幅な日時不正に対する拒否結果をこの二branchの網羅と取り違えない。開始.25/.75/2ppはevent0738。

隔離実PG/DDLs、二入力started_at/ended_at。固定run27880001/2051-04-09T15Z＋日差、原SUCCESS二行(target/success1/2、26/67bytes、開始/終了+3秒)を独立SQLでseed。successfulBackupの第二rowの該当JDBC日時だけ+1秒とし、各rowの開始<=終了<=観測(+3600秒)・microsecond・業務日・countは有効なまま、pairの開始又は終了が不一致となる。IOException/固定文言、注入回数開始1/終了2、commit0、接続閉鎖、原二SUCCESS全列/件数不変・client/advisory解放を独立確認。

private field/Root/native所有の偽造/Productionからexpected生成0。Source042/PG2654/full2770/当native2774不変更。構築済PYTHONPATHで `python3 -B tools/quality/pg2788_success_pair_timestamp_selected.py`。初期未実行、実結果/対象commit/XML/counter/hashは独立資格後に追補、全体新Test統合/正式/global100加点0。Root/Backup/ADMIN/VM/stop/配置/reload0。
