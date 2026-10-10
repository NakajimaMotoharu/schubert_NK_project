# cold全事前資格・固定親子退役仕様

NK-OPS-001 / SS343353 / SSC245246 / QA047 / BUG1017～1020・YKT786～789。新only operationで旧Java5463/start1373880/argvfcb09442…と子5489/start1373951/argv8067…を退役する。Root/DBrow/namespace/mount/current/原本/Backup変更0、旧unknown正常化0。

PG1059-v4 Source361fac8abaf2004ad2fbdf9bc31ab98fac3f52e8、08:32:57.382204～08:33:00.838372UTC/3.456168s actual0、fulltwo-read/他client0/同ROpeer/全tenfull32/原値不変/observer正常close。beforeprivateSHAce521c73dc0f91d303065ddcb3f8f9c0350b0a142c6a17eb88a9798f1bb6e544、scriptSHA72f870b67af03d9809785f1a8efe14128d0b74707a46fd31d4b1cfc42444b472、logSHAa9cdad6de169dd7fa1edcc5f8f2c4b8e2a866c1033f91168d72be2b794ba220d。旧actual失敗は保持、v4成功へ合算0。

PT-DEP-1060001/002：rawqualified beforeをNOFOLLOW held proofへ束縛、newslotは既v4の内側で原ancestorを不変にする。親子両pidfdを事前束縛、親予約/元whole再読→普通TERM一回/実親PID0・server全client/advisory0・M/A0・元値再読→同世代子（PPID1/全authority/FD/currentbus）予約・再読→普通TERM一回→子PID/bus/全FD0・全元値二読・newRefFD正常close。全callback/予約/send/wait/close変異はRefFD内UNKNOWN、一回を再送しない。metadata7427の退役済成功を親子へ流用しない。

親終了に伴い子も既に終了した場合は、子PID/bus消失・全後条件を独立に確認して二度目の停止を発行しない（最大一回原則、oldchild正常close/exitはunknownのまま）。生存なら元同世代FDへだけ送信する。別reaper/未同定child/別server peer・外部変化は拒否し、勝手に期待値を変えて進めない。

独立oracle：PT-DEP-1049001～009の手書きstateful sequence/各失敗/timeout/null/同PID/悪世代/既terminal childで最大一回を検証。1060 guard2は固定pair/qualified fullhash/zero-peer postと禁止operationsを確認する構造試験で、実経路を代替しない。host9+2 PASS、当newsource全helper qualificationとactualは後記。必要Java四coverageは未更新、正式PT24/1964/53と候補d5/host3563を保持。

実行command=`python3 -B tools/quality/vm/050_s1/pg1060_cold_owned_tree_handoff.py`（未発行）。主旧hostexec30116は退出を別採取しactual/旧UNKNOWNを保存、新退役actual0から143/正常を推定しない。source/run/終了code/hash/DB後条件/旧child未知とnew observer normalcloseを別manifestにする。Handoffだけではcold準備/Root/PGPT完了0。
