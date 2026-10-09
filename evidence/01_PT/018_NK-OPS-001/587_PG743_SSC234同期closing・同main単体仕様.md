# PG743 SSC234同期closing・同main単体仕様

NK-OPS-001/NK-ADM-001/NK-DAT-001、RD OPS009/TST004/AUT001002/DAT009、UI212225226241251、SS342343354/451/SSC234。分類4/internal measurement only、RD/UI/DB/業務/Root/API-Web/budget不変更。design source a99873e67→main design-only0d4a63cbe/PR72/main e5e4314e53fd520d10b96d47cf6b0f07e7ba42cb MERGED・origin再確認。mainは既SS正本を保持、451は実施branchだけ。限定review完了、hook順序依存でなく同期closing採用。

対象：FixedNativeCoverageTerminal terminal/closing/constructor(主担当P018-08)、Checkpoint.capture/Profile.supportsClosing/NativeCoveragePrivateFile.export、BootstrapAdminMain constructor/main(P010-05)、InspectorLauncher.completeAndClose/main(P004-04)。TERMINALを保持、same-owner/同checkpoint正常帰還後のCLOSING一回・無reset・new0600の正常close/dirsync/再読からmarkerを出す。agent無はI/O0、既業務status/receiptを保存、採取失敗非成功・collector資格未受入。source固定後 selected bootstrap/API依存reactor、static/NullAway/Werror/format/XMLを独立確認、新Productionのため変更群必要全6fresh。実VMの資格/所定全品質は別受入。

PT-OPS-CLOSE743001..005：literal snapshot/terminal-name/entry-return/snapshot/closing-name順、disabledfalse、nullfactory/role/戻り欠落/throw/先行・二重/foreign-thread、失敗terminal後closing拒否・他role拒否。期待値はSS固定literal、productionでexpected生成0。PT-OPS-NCLOSE743001：host実tmpfs/保持FDとmodeled ownerを区別し、六role中二だけ新closing許可、terminal原byte不変更・0600/link1/2create/2sync・二回目拒否/全FD返却。既NEXPORT617の全metadata/postcheck/write/force/close/hash/異常/null/fault matrixを同じexport経路へ適用する。

PT-ADM-CLOSE743001..003：同main独立operation/capture/closing/termination portで0/20/50/70、disabled/present、既診断→terminal-return→closing-return→終了順・closing IOException/Error固定50/完了marker無し・六null依存拒否。既BOOT707実Java25 subprocessでFQCN/0argvとoverride拒否/70/秘密出力0を検査。PT-DB-CLOSE743001002：receipt70/既terminal診断→closing/後marker、disabled/throwidentity/null・出力前拒否、terminal/業務throwではclosingへ進まない既構造。port試験は実admission/初期作成/ordinary Inspectorの代用でない。

試験初期実装TDD群/未受入、BUGを隠す合格読み替え0。実command/source/exit/XML/static/counter/hashは実run後追記、failed/flaky/skipped/not-run/別source算入0。Current/原本DB/Backup/旧terminal/旧失敗/private/stash保全。native closing collector latest-only/単調probe/markerの独立試験と実VMは次依存、本specでglobal100/正式/ITST完了を宣言しない。
