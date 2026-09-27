# PG310 root親・backup全終端契約 PT仕様書

NK-OPS-001、SYS002/004・OPS009・BAK/BKO、UI251、SS341 §5/6・343、SSC093、BUG271/YKT205。対象はRootStartupContext.MORNINGとBackupUnitTermination、続く親worker接続。実装前仕様、実行/coverageは未実施。限定成功を正式run24/全backup/業務R2/R3へ加算しない。

| Test ID | 対象・目的 | fixture/input/操作 | 独立期待値・根拠 |
|---|---|---|---|
| PT-OPS-ROOTCTX-001 | MORNING固定主体 | root literal PID42/boot111…/invocation111…、固定朝Unit manager7fieldとkernel cgroup | 同固定Unit/PID/boot/startticks、2観測一致。既存API/Web観点保持 |
| PT-OPS-BTERM-001 | cold厳密不存在/存在時全process | Unit18field inactive/dead/PID0/Job空、4field Slice=system.slice Delegate=no group空または固定値、host5ancestor literal root0755/sys0555/CG0555/Slice0755 | leaf一点MISSINGのみquiescent、bus全processは不存在時未呼出。存在時bus全process空と安定照合が必須。全FD閉鎖後だけ返却 |
| PT-OPS-BTERM-002 | 実効配置全byte/field/境界/null | 4field独立literalを欠落/重複/未知/CR/NUL/非ASCII/上限/別Slice/Delegate yes/別cgroup/別Idへ変える | 全拒否。null契約違反を正常化しない、byte所有は全終了消去、秘密/出力を診断へ入れない |
| PT-OPS-BTERM-003 | metadata/FS/ACL全条件 | 各ancestorとleafのmode/uid/gid/nlink/size/dev/ino欠落/誤型/境界、sysfs/cgroup2不一致/ACL/非root | 全拒否。devinoの前後変化と同FS親子不一致も拒否。非root/context拒否はhost open0 |
| PT-OPS-BTERM-004 | 不存在分類/Unit非空/前後変化 | 祖先MISSING、leafUNAVAILABLE/COLLISION、symlink、live Job/PID/state、bus非空/IO、Unit/配置/context drift | 祖先や一般IOは不存在扱いしない。liveはOptional.empty。停止結果の古いcache再利用0 |
| PT-OPS-BTERM-005 | IO/close compound/unknown | 全呼出位置にIO/Runtime/Error、全close位置、body+close複合、同Throwable、invalid/null port | 全取得済FDを一度ずつ閉鎖、未取得FD close0、unknown identity/ResourceScope優先規則保持、失敗を成功へしない |
| PT-OPS-BTERM-006 | interrupt/並行・反復 | 入口/途中/close後/context再確認の割込、独立instance同時実行 | flag維持・非成功、各owner独立・返却時owner0、fresh観測を毎回実施 |
| PT-OPS-BTERM-007 | 固定query argv/実IO | 固定BACKUP NativeReaderの独立argv oracle・fake process、realNOFOLLOW host viewはnative隔離VM | system busのみId/Slice/Delegate/ControlGroup固定target、env bus overrideなし、bounded query/全stream閉鎖。hostでrootを偽装しない |
| PT-OPS-BTERM-008 | Production native factory/正規host cgroup | 隔離VM固定root MORNING Unitでcreate/context capture→cold/停止後query | 真正PID1/kernel/UnitとhostNOFOLLOW証明、過去native025をProduction親済みとして流用しない。実測がなければnot-run |

親接続PT-OPS-BPARENTはM→原本→停止→A→全終端→INVALID→DB両step begin commit→request→startclient実終端→fresh0→stop/全終端→retireのlatch/unknown反例を独立検証してから追加する。DB/manifest/retention未接続を成功へ補完しない。

CommandはJDK25.0.4/Maven3.9.12、対象Batchと依存Storage/Bootstrap限定suite、report/SpotBugs。changed class全line/method/class/branch100%と必要native same-class-byte mergeを要求し除外しない。対象source/run、日時、OS/tool、branch/command/exit、input/独立expected/actual、全suite/hash、coverage、BUG/SSCと未実行範囲は143結果/manifestへ記録する。秘密/cookie/token/password/dump/private keyをGit証跡へ保存しない。
