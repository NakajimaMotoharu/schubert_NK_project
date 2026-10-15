# Morning保持owner・割込非解放・子終端仕様

WBS-P017-12.03 / NK-OPS-001 / OPS009 / UI251 / SS341343/SSC137。PT-OPS-RETAIN3396-001。対象は`MorningStartupLaunchOwner.retain()`の非終了・割込非解放契約、Test=`MorningStartupRetainOwnerTest#retainsCallerLockAcrossInterruptUntilOwnedTermination`。Productionを変更せず、同packageの契約methodを公開可能な通常呼出しで検証する。private reflection・存在しないUnit・真正Rootの再演を使わない。

事前=固定JDK25/JaCoCo、既全3706/同28nativeと同a9 Main byte。親JUnitがnew-only @TempDir/output/lockを作り、返された専用Processだけを所有する。子は実FileChannel exclusive lockを獲得後にmain threadを割込み、retainへ入る。別witnessは割込を設定した後にだけ観測を開始し、Mainがflagをclearした事実を固定非秘密markerへ記録する。

独立期待値: marker二行の順序と完全一致、他processのFileChannel.tryLockはnull、200msの有限観測中に子は戻らず再度tryLock=null。親のowned TERM後は10秒内に真正child exit143（意図した負系fixture終了でありProduction Root成功ではない）、余分な正常帰還markerなし/err空。別processの新FileLockを実取得でき、kernel owner解放を確認する。NPE正常化やProduction methodからexpected生成をしない。no-op/割込による早期正常帰還ならmarker/実lock/生存条件で失敗する。

失敗時もfinallyでこのProcessだけへTERM→期限超過時のみ強制回収し、強制回収を正常受入へ加算しない。過去PID/VM/Unitへsignalを送らない。純粋単体でなく承認済み隔離OS component PTであり、bounded process観測のsleepは外部service依存や業務性能試験ではない。実DB・原本・Backup・credential・permitは使用しない。

子JaCoCoは現JUnitの固定agentだけを継承しappend=falseを拒否、子の真正TERM完了後に親も通常終端して同source host execへ加える。Main CRC/debug byteは全1643+全resourceで別照合し、既VMの28streamや別sourceへこのhost結果を捏造輸入しない。

実行予定=新-only `pg3396_retain_owner_related.py`、関連33case/8suite（batch三suite6、Protocol7/Storage8/Bootstrap5/API3/Web4）。関連周辺の既null/admission/同ownersequenceを保持し、六module正規format/compile/SpotBugs・Main byte不変を確認する。全体3707は必要一統合を別に完走するまで未認定。実command/source/exit/XML/coverage/hashは新manifestへ固定予定。現時点は未実行であり新PT/coverage/受入加点0。初回未実装TDD失敗と既実装仕様違反は区別し、後者は修正前にBUG/YKT起票する。
