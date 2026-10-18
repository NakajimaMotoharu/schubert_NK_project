# Startup ViewOwnerのprimitive登録・全逆順drain

BUG1432/YKT1196是正追補：最初のsource673/PG5240-v1は829PT全成功/Owner四100でもSpotBugs RuntimeException汎用throw1で不合格として保持。固定4.10.4 ThrowingExceptions.sawOpcode実bytecodeはATHROW時の型がRuntimeExceptionであることを検出する。汎用Throwable scratch/castへ型を失わず、closeのnative catch内に元Runtime/Error union primaryを保つ非再帰三phase（first/known/drain）へ内部是正する。secondary scratchは取得前確保boolean bitmapとし、後続unknownは全native試行後だけ固定suppressedへ変換する。全64golden/既期待・identity/Reason/順序は変更0、synthetic method移動・sneaky throw・抑制/除外を使わない。修正sourceはpg5248→pg5250実bytecode→pg5252公開→pg5254分類で新規資格し、旧pg5240終了1/829・全counterを0化/転用しない。

WBS-P018-03.02、群1211開始.8/3/8共有pp固定・親03非加算/先行.01未受入/実費・工数null。BUG1414/YKT1178の同原因、SSC308補足SS333/343/354/914はdesign-only **abf662cd3→origin/main19e591804/PR161**、通常CLEAN/MERGEABLE/check無し確認後merge・remote祖先確認済み、実施branch33dfb24a1。PR添付100上限拒否は保全し迂回0、未受入code/tool/evidenceはmainへ混在0。RD/UI/外部/原本/current/Unit/exec前service→host消費/A借用規則の変更なし・新QA不要。

対象StartupAdmissionFile.withView/ViewOwner。owner/primitive int slots/secondary失敗bitmap/全portを初回native前に確保し、容量はruntime段数N＋root1/app1/entry1＝**N+3**。各openはclosed/満杯・必要parent/nameの内部不変条件を取得前に検査し、native有効FD後は非負/既保持duplicateをprimitiveで判定して格納/返却、new/boxing/grow/callback/追加helper呼出しを挟まない。負FDは新所有無し、duplicateは既FDの新所有と見なさず元owner一回のみ。Math容量算定/配列確保の失敗はnative前で資源0。

closeは論理consume flagを先に確定して全FDを逆順一度ずつ試行し、drain中のcallback/new/suppressed/例外正規化確保0、事前scratchへ失敗を保持。全試行後だけ既ResourceScopeと同じIO Reason/unknown identity/秘匿suppressedを合成する。単独Storage IOは既suppressed無しのReasonを保持、複合IOはUNAVAILABLE、primary IO＋secondary Runtime/Errorはsecondary優先、他は元primary＋固定Storage IO suppressed。DirectoryCalls.closeは失敗時もFDをconsumeする契約で再試行しない。論理消費/close例外をkernel正常解放やUNKNOWN業務成功へ読替えない。実heapOOMEを誘発/再現したとは扱わない。

新独立StartupAdmissionViewOwnerTest **8case/PT-OPS-VIEWFD-001..008**：001 FD319/320/321逆順とidempotence、002 null/容量0・負/closed/満杯/parent・name境界と取得前拒否、003各openの負/duplicate/有効境界0、004三open×IO/Runtime/Error、005三closeのN/I/R/E **64組**、006既suppressed/同一throwableの秘匿合成、007bodyとreleaseの故障/全FD試行、008独立owner並行・状態分離。既StartupAdmissionFileTest9のhost/private原値・readonly・同OFD・contend・差替拒否・全IO/metadata/compound/exec前消費/並行と実Nio契約も同sourceで実行する。

005の期待はSS333から独立固定した4×16文字golden（順に最後/中/最初FDのclose結果N/I/R/E）：primary型 `NIREIIRERRRREEEE` / `IIREIIRERRRREEEE` / `RRRRRRRRRRRRRRRR` / `EEEEEEEEEEEEEEEE`、追加suppressed数 `0000000001110111` / `0000000001110111` / `0111122212221222` / `0111122212221222`。unknown identityの位置は `xx22xx2211111111` / `xx22xx2211111111` / `0000000000000000` / `0000000000000000`、xはIO正規化又は正常で元unknown無し。expectedの生成にproduction use/mergerを呼ばず、原golden/fixture値/順序/回数/全FD試行・error優先順位をassertする。

当source予定**829PT98suite**（既812＋既9＋新8、算術は予定のみ）、新whole予定3845/559/1661は未実施。pg5240_selected→pg5242_bytecode→pg5244_public→pg5246分類、1074結果へsource/run/環境/tool/command/実日時/exit/input/XML/TestID/coverage/BUG/hash保存。六format先行0/NullAway・ErrorProne0/三static0/全storage四miss0、Owner全line/method/class/branch100とwithView/FD取得前容量・primitive有効経路・drain前後を実Java25で検査し、全764物理差分を限定する。未実行native/whole/F03/CHR/451/QA051final/trace/引継ぎは別受入、原237/追加発見を分け、正式1964/53/歴史17/190/工数null不変。原本/DB/Backup/鍵/stash/Currentbaseline/native保全、実VM操作0。

管理上の欠測：最初のmetrics importを隔離main設計treeで呼びmodule不在終了1、event未追記/branch準備のみ・source変更0。実施treeから1210/1211を一回追加し、開始見積りはdesign/code編集前固定、原失敗を0補填しない。正常PR作成/merge以外の再操作0。利用枠残10%以下新着手停止/5%付近保全、通常小区切り停止0。
