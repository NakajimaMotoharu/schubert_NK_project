# NK-PRO-003 SSC308 限定実行結果

Source **6d7a54a0141b8969b846d13ed452c30ec51c5b15**、dev-foundation。仕様016/RD FIL001009・OPS009/UI237251/SS333343354/SSC308/BUG1414・1416～1421/YKT1178・1180～1185。新16case＝Factory12+Directory3+RootGuard004、既独立23と関連183を同じrunで再試験、合計222（算術合成の別run合格ではない）。

元command `python3 tools/quality/pg5120_root_elf_selected.py green --group factory`、元session18465・pg5136-factory-io-green-v6完了exit0、32suite/FES/flaky/notrun0、六Production formatをPT前に完了、NullAway/ErrorProne0・storage/bootstrap/batch SpotBugs各0。未compile moduleの新static成功は認定しない。Java25.0.4/Maven3.9.12/JaCoCo0.8.15/SpotBugs4.10.4.0、OS・実command/日時/exit/source/hashは下記manifest。親umask0077、Maven子0027。

storage全178PT/25suite、LINE1200/METHOD269/CLASS37/BRANCH537、各miss0。新helper acquire23行/1method/10branch、既use19/1/8、openRoot4/1、RootDescriptor ctor6/1/2・close2/1が各miss0。対象10methodすべてline/method/branch miss0、class等の全体四100とは別。

選択実762Main、旧e8ecと6変更+5追加/削除0/旧751同byte。新追加はAcquire/Release/OwnedAction/EntryOpen/RootDescriptor。必要な全体3830/558/1659は現差分からの予定だけで、実全体認定ではない。

独立 `python3 tools/quality/pg5138_factory_bytecode.py` 元39092 exit0。取得直後はIO/Runtime/Error保護下、portは取得前構築、Directory stateLockとEntryHandleはnativeopen前確保、RootDescriptor成功primitive後にboxing/heapwork無し、既use56opcode/全handler意味同一。明示Error注入と実bytecodeの証明であり、実heap OOME発生証拠ではない。

証拠：`evidence/provisional/PG5138-factory-bytecode-v1/manifest.json` SHA **5ce0522445487607c5e153c0874dce22e0ef43a14e743221f16d143273f85272**。選択全case/二coverageXML hash/静的/物理差の訂正metadataは `../018_NK-OPS-001/evidence/provisional/pg5136-factory-io-green-v6-metadata-v2/manifest.json` SHA **e3024935f72850494029c6ec21f110e06a019051b71ce9c1b2a81576f810efde**。元公開384a1470は二XMLのkey衝突があり、上書きせず履歴保持/BUG1421起票後metadataだけ訂正、Maven再演0。

失敗履歴はprivate PG379のv1 compile1/PT0、v2 lint1/PT0、v3storage4failure3error（子umask）、v4static1/v5static2をすべて保持。各修正前BUG1416～1419/YKT1180～1183を起票、期待値/coverage除外/静的抑制を変更せずv6で検証。bytecode比較表示padding初回失敗はBUG1420（保存raw無し/欠測明示）、元公開metadataはBUG1421。未実施を成功に換算しない。

Root9+待機2+OwnedDirectory5の16site限定是正。元68file237siteの残候補は所有/borrow/transferの個別判定・必要修正/再発防止PT未完で、BUG1414/YKT1178はOPEN。新source全回帰/native/CHR/451/正式1964PT53scopeは未更新。群1180費.8/3/8固定、主P003-08・共同P003-04分割null/非加算（訂正1183）、実費/N-T/消化率null。
