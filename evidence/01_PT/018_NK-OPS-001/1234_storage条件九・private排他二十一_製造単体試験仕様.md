# 1234 storage三十適用指摘の製造・単体試験仕様

PG-D446/BUG1507/YKT1267、WBS-F03主費、共通storageのWBS-P003-04/08・NK-SCN-001/OPS009参照追加費0。着手前費.5/1.5/4週次共有pp、原/v3/v4残予測は不変。旧source790/PG5886の3973は保全し新sourceのPASSへ輸入しない。

## 予定PGと独立期待値

| Main/method | 変更 | Test class/独立oracle |
|---|---|---|
| LinuxExecDescriptors.inherit | FD_CLOEXEC=1を命名、GETFD=1/SETFD=2/clear=0/復元=1不変 | LinuxExecDescriptorsTest/PT-OPS-XFD：固定command/argument順、借用FD不close、partial/複合失敗 |
| LinuxFilesystemClassifier.filesystem | 四既kernel magicを命名 | LinuxFilesystemClassifierTest/PT-OPS-FSTYPE：独立literal LP64先頭word、四family/未知/ABI/null |
| LinuxSealedProof.prepare/read | 必須seal=15を命名、ADD=1033/GET=1034不変 | LinuxSealedProofTest/PT-OPS-SEAL：fake固定値/書込量/EOF/8192境界/null/失敗、自己所有匿名memfdのみ |
| StorageAttributeGuard.file/existingFile | 正数最小=1を命名、48MB上限不変 | StorageAttributeGuardTest/PT-SCN-008：独立Unix属性map/0/1/上限/null/未知型 |
| StorageRootInspection.inspectOne | 既asset0/transfer1/backup2を命名 | StorageRootInspectionTest/PT-SCN-008-A07/A08：自己所有temp六root/固定mode・identity・順、実配備root不使用 |
| OwnedTransferDirectory全21排他method | private final ReentrantLockを取得前構築、lock/try/finally/unlock | OwnedTransferDirectoryTest16＋PrivateChild/Entry/ChildPublication/OwnedDirectoryFactory等：固定wire1,2,3・入出力/NOFOLLOW/部分保全/消費一回/再入/close競合 |

全storage既188ケース/27suiteと他五module11guard（protocolGolden3/bootstrapEnum1/apiEnum1/WebRange4/batchEnum2）を当source199/33で実行する。期待値はProductionの定数/戻り値から生成せず、既testの独立literal/手作りport/fault/真の自己所有fileを維持する。Test/POM/resource/Current baselineは不変更。caller monitorを保持した別workerの完了、inflight callback終了前のclose禁止と後の全FD解放、openDateの同一thread再入も維持する。時間測定による性能合否/ITST合格は含まない。

## 着手前判定とcommand

PT_DEFAULT。通常userのhost新only私有snapshotに限定し、offline Maven/全六format先行→選択package/JaCoCo/SpotBugs。storageの既self-owned一時FD/anonymous proof/child process fixtureは元受入profileと同じで、実VM/current/Unit/原本DB/Backup/鍵/permit/失敗Rootへ接続しない。危険/拒否境界探査や拒否操作の別経路実行ではない。source/command/副作用の変化は再判定する。

予定入口：canonical PYTHONPATHで`python3 -B tools/quality/pg5904_storage30_selected.py`、後続`pg5906_storage30_static.py`。新only namespace、実行前clean source/fresh枠>10。全851 source/1666物理Main（six outerと必要nested/debugだけ差）/公開ABI不変、無除外PMDの当九/二十一消失・他rule保持を独立照合する。line/method/class/branchは実XMLのcovered/missedをそのまま記録し、未知/未実行を100へ補完しない。coverageやPT代替の加点は実結果後だけ、formal/全体/native/CHR/451/traceは別未完。

結果は実時刻/OS/JDK/tool/branch/source/command/終了code、全input/output/XML/hash/counter、BUG/YKTと同sourceへ接続して1235以降に保存する。当仕様時点ではPG・当試験は未実施。
