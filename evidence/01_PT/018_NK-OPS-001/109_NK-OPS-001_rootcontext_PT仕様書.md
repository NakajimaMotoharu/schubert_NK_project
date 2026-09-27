# Root起動context PT仕様書（PG296・未認定）

NK-OPS-001 / RootStartupContext.create/capture/recheck/observe/properties/start/ascii、NativeIoのproc/Unit読取。RD SYS-002/004・OPS009/UI212・251/SS342・343/SSC086・087/D04・05。
kernel proc/PID1/system manager/fixed Unit認証をhost SPI前に実施、A取得後とexec直前に同snapshotを再検査する。全permit/root/Ops/schemaの代替ではない。

| PT-OPS-ROOTCTX Test ID | 目的・fixture/入力/操作・独立期待値 |
|---|---|
| 001 | literal boot/Invocation/PID42/start12345/init5/cgroupとmanager7property、2観測一致、API/Web、activating/start・active/running |
| 002 | UID非0/proc以外/init exe違い/zero・大小文字・改行不正boot/Invocation拒否、Unit照会前遮断 |
| 003 | PID範囲、括弧を含むcommのfield22、startlongMAX/overflow/zero/先頭0、短いstat/閉括弧欠落/死状態/PID namespace不一致を拒否 |
| 004 | 各7property欠落/重複/値不正/未知、loaded不成立、cgroup違い/複数rowを拒否 |
| 005 | ASCII/長さ4096境界/control/null、2観測drift/recheckboot変更、IO原因の固定redaction |
| 006 | 固定systemctl argv/clear環境、exit非0/timeout/interruption/起動null、所有process終了 |
| 007 | stdio close全位置/未知cleanup優先、normal原因をStorageResourceScope固定診断へ畳む |
| 008 | 実proc読取/通常UID拒否、PID1 exe通常UIDaccess denied、固定link port正系、実未配備Unitはshow exit0でもnot-found |

Native014は隔離VMの固定API名transient Unit/実rootでkernel proc/boot/Invocation/MainPID/cgroup/A前後recheck成功を独立観測。工具だけで業務main/現許可/全配置の合格にしない。
固定kernel path5methodのDMI portability指摘はEXACT指定・対象methodだけの既存方針でレビュー。null/security/coverageを抑制しない。正常/境界/異常/例外/null/TOCTOU観点は上記、業務再送は対象外。110/provisional PG296にcommand/環境/hash/実行結果。
