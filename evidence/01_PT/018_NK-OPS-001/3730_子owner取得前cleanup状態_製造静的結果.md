# 子owner取得前cleanup状態：製造・静的結果

Program NK-OPS-001/Test infrastructure、関連SS311312341343/411451、BUG2477/YKT2215。source8e50c410/Production Main7aed不変。PG23190独立exit0、manifest `evidence/01_PT/018_NK-OPS-001/evidence/PG23190-owner-preallocation-independent-v1/manifest.json` SHA256 `f52fb8f0ec906933ea9d1df2727065ce72fa4195b64362b80d966ce1fec13011`。source修正と承認済み静的代替の結果で、元native/process PT PASS/covはnull。

|静的Check ID|class/method|独立期待/確認|
|---|---|---|
|SRC-OWNER-PREALLOC-01|OwnedTestProcess constructor|state準備後に唯一のProcessBuilder.start、直後はfinal captureとreturnのみ|
|SRC-OWNER-PREALLOC-02|close/closeStream|private list容量8、独立144抽象pathの最大記録6、初回TERM前の直接new無し|
|SRC-OWNER-PREALLOC-03|五caller八constructor site|.startだけhelperへ移動、全他token/argv/--no-fork5/期待値/return/owner順を元へ復元|
|SRC-OWNER-PREALLOC-04|awaitExit/reaches/process accessor|全他token不変、旧wait5+5/interrupt/identity cycle guard/同owner一回を維持|

old owner自体のnewメモリは引数評価前なので、その確保を取得後と誤認していない。実問題はcloseAttempted後のArrayList確保/初回growthが終了試行を阻害し得るsource経路。ProcessBuilderを渡すconstructorへ揃え、list capacity8と固定UNKNOWN IOExceptionをinstance初期化、最後のstartをfinal ownedChildへ直captureした。

23178 own parse-format0/元Testcompile0、23180新helperだけproc:none/Xlint-Werror staticcompile0・受動javap0。実bytecodeでcleanupFailures put14/terminalUnknown put27→start40→ownedChild put43→return46、JDK25 ArrayList positive-capacity branchのanewarray10を確認。close firstTERM前にnew/array系命令なし。source否定8/bytecode順序否定4。OOMやVM/OS解放の実測・保証ではない。

23182現六source typed PMD raw28（Thread16/cleanup catch10/null負例1/Throwable identity1）をsource/ASTmethod/body hashと具体的所有根拠へ束縛、個別非該当/適用0/未分類0、CS0。元29は不変24+変更5の82理由を再束縛、新helper13は別計上。全29engine再演や全F03/451受入ではない。359初draftは期待literal内line comment後のnewline不足で拒否し23186へ保存、元source変更/engine再演はせずguardを是正。

全実Product start/stop/wait/Root/VM/DB/FS/native/OOM注入/代替fixture実行0、own静的tool processだけ。元Unit/Main六静的/covを再演せず、実PT/全工程完了へ換算しない。current442/whole94/正式1964-53/新leaf0/工数null。実command/exit/OS/SDK/全hashはmanifest/公開rawと3729へ、IT/ST未実施。
