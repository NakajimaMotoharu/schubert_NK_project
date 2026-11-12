# P00806 本文delivery・stream・reader 全148通常PT仕様

対象Delivery3/Stream5/Reader4の全original12件＋sharedSnapshot6＋現Protocol130、合計148。関連FUN004/005/FIL001～009/UI234/237/SS3334～7/451。TestID R01～R03/W04～W05/RD03～RD04/SHAPE001～003/SNAPSHOTMAX001～003とProtocol原130。期待値は原whole source全文内のUI234手書きoffset/固定境界/別SHA計算。delivery用HASH=a64はprojection stubだけで実ファイル内容hash oracleではない。

正常・境界・異常: 0/1/199/200 inline、201/10000 FILE、4800x10000=48M、全field1728/record4800、JSTpath・count一致、publisher一回/失敗no retry、callerowned freshchannel・部分7byteI/O/zero/negative/IO/force/closed/位置size不正、先hash→rewind→decode同時rehash/順序・途中改変/null/required/reserved/UTF8/NFC拒否。Caller channel不閉鎖、不完全結果不返却。実DB/auth/nativeRootには依存しない。LargeResultReader実Rootwholefixtureは別HOLDを維持し本scopeへ含めない。

BUG2681は原StreamTestのpoolだけをfinite invokeAll/get10秒・finallyshutdownNow/await10へ修正。26896に逆変換で元source完全一致/whole5/16tasks8workersを確認。期待値/原TestID不変更・新定義0。一般2177全域未完は保持。PG26898 freshTestcompile0、26900 PMDraw6/終了4を保全、26902で各context（standaloneTest worker4・finiteclose1・手書きpartialread選択1）を明示非該当と分類。抑制設定追加0/適用0/未分類0/processing0/Checkstyle0/format0。Main14はnormal source/physical/static同一を限定reuseし全module認定へ拡大しない。

**I/O開示**: Stream/Reader wholefixtureはJUnit所有TempDirへ独立synthetic一時fileを書き、最大48MBを読み書きしてJUnitがcleanupする。Readerのfixture0640設定も自分の新規一時fileだけ。これは実Transfer原本/backup/master/native保持FD/root/credentialの操作ではない。テストのfile操作を0と報告しない。全190physicalを保持（Proto176/API8/Web3/Storage3）、実行class/Code/noCode/標準generatedfilter/CRCは独立postで別々に照合する。旧exec/coverage合成・手動除外0。

Source固定push後command: `PYTHONPATH=tools/quality python3 -B evidence/01_PT/018_NK-OPS-001/input/1388_scenario_current_qualifier.py run <fixed-source>`、続けて1391独立post。source/環境/実command/exit/全XML/counter/BUG/YKT/証跡hashは当run manifestへjoin。開始時はUnit NOT_RUN、失敗/skipped/flaky未合格。SOURCE_REQUAL .1/.3/.6＋Testfinite .05/.15/.3= .15/.45/.9 cap2を着手前固定、実専有費null。元P00806/2・全451・正式1964/53・原190は増加させない。
