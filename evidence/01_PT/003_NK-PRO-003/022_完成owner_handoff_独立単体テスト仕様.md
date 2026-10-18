# 完成owner handoff 独立PT仕様

Program NK-PRO-003、ResourceScope.handoff及びFactoryResourceScopeTest.factory013..018、RD FIL001～009/OPS009・UI237251・SS333343354/SSC308・BUG1414/YKT1178。設計onlyb1dccda20→origin/mainc6a7a541e/PR162（四文書、通常merge/remote祖先確認、添付100上限拒否保持）、実施648626cf5。414?ではなく411/451を適用、RD/UI/外部能力変更0。group1224主費P00308/P01712.03構成、開始.6/1.8/5共有pp固定・分割null/親12非加算、旧見積り/原237数を変更しない。

全port/primitive移管状態/条件付release/assembly callbackを取得前に構築。組立はacquire保護域内、完成nonnull T確認→最後のprimitive flag→即返却。成功時はhelperがRを閉じず完成ownerへ責任移管、未完成/null T/組立失敗は既acquireの一度release・IO Reason/unknown identity/固定suppressed優先を保持する。factory IO/Runtime/Error/null Rで組立/release0、null Tは保護中のNPE/release1。E型は既contract内・nullable genericでも完成ownerは実nonnull必須。返却後の実owner.closeは当helperの二度目処理にしない。

独立golden（production helper/use/acquireを期待値生成に呼ばない）：組立I/R/E×close N/I/R/E、勝者型は行順で`SSRE/RRRR/EEEE`、返却例外suppressed数は`0000/0111/0111`。Sは固定StorageIoException、I+NはMISSING、I+IはUNAVAILABLE、I+R/Eはclose元identity、R/Eはbody元identity。suppressedは固定UNAVAILABLE/no cause/no raw message、同object失敗をself-suppressionにしない。成功組立Nはclose callbackを呼ばず、未完成3行だけcloseを一度実施する。

| Test ID | fixture/入力・操作 | 独立期待 |
|---|---|---|
| PT-IOFACT-013 | 完成owner同一token、close callbackは呼ばれれば失敗、狭いStorageIoException型コンパイル | token live/同一owner、open1/assembly1/helper close0、呼出側で一度退役 |
| PT-IOFACT-014 | 三null port、factory IO/Runtime/Error/null資源 | port拒否はopen0、factory失敗は組立/close0、IO/unknown元identity、null RはNPE |
| PT-IOFACT-015 | 上記独立3×4固定行列 | 勝者/Reason/identity/秘匿suppressed/order・close1 |
| PT-IOFACT-016 | 組立null T、close N/IO/Runtime/Error | NPE・R一度解放/既優先/固定suppressed・helper成功0 |
| PT-IOFACT-017 | 同一unknownをbody/close、既suppressed付きunknown/IO | 自己suppression0、元unknown identity/既順序保持、IOはUNAVAILABLE固定化 |
| PT-IOFACT-018 | 二独立tokenを二threadでbarrier後に完成移管 | token/primitive状態共有0、両live/各open1・helper close0、呼出側各一度退役 |

旧12caseを改変せず新6を既25storage suite内へ追加。source commit固定→pg5296_handoff_selected.py green --group factory一回、全storage四100/旧acquire・use含む全PT、六format先行/NullAway・ErrorProne/三compiled static0/FES/flaky/skipped/notrun0。pg5298実bytecodeで取得前state/全port、完成nonnull後のprimitive flag→areturn、条件付release、旧全method opcode/handler不変、全764物理Mainを照合→pg5300独立公開。原237分類はclient未修正のため190/1/46から閉鎖加算0、Permit/Intentへの適用は後続別source。新whole予定3851/559/1661/native/全四100/451/正式は未実行、旧成功輸入0。

023へ全source/実日時・OS/JDK/tool/command/exit/TestID・fixture/期待/実際/XML/coverage/static/hash・BUG/SSCをallowlist保存、秘密実体0。既run先行照合/二重起動0、実DB/Backup/Unit/VM操作0、原本/鍵/stash7/Currentbaseline/native/成功失敗証拠保全。実heap OOMの誘発ではなく明示fault＋bytecode根拠として区別する。
