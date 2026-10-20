# 1284 JMS同lock完了flagのPG/PT

NK-MSG-001/ArtemisReplyConsumers.closed/close/ready、UI212231/SS321342/411451、PG-D460、BUG1544/YKT1304。群1478開始0.25/0.75/2pp固定。旧source870/1281実L76M12C1B22全miss0を選定根拠にし、旧PASSを新sourceへ輸入しない。

LOCKEDFLAG001：sourceと当生成Jarで全closed読取/更新がclose内の同stateLock保護下にあり、lock自体private finalでconstructor以外に再代入無し、正常close後だけclosed=true・失敗時再試行/停止拒否は不変と確認する。readyはclosedを参照せずstopping/startedのvolatile読取が必要で、そこを改変しない。Sync/WebLog.closedのready lock外読取、既Question/WebBroker.closedの同lock保護も横展開の個別非該当根拠へ残す。

LOCKEDFLAG002：旧/当原Jarから当classfileを独立構造parseし、closed fieldのaccess_flagsだけがPRIVATE|VOLATILE→PRIVATE、他全byte不変であることを確認する。コードのmethod descriptor/命令/exception edges/public ABIは不変更。実Production methodをexpected計算に呼び出さず、この比較を実行PTや実測coverageへ加点しない。

LOCKEDFLAG003：Test/source oracleは不変更の全Web917＋他guard8＝925/150を当snapshotで一回実行、既正常start/ready/close、失敗close再試行、同一Throwable、factory/null/unknown・public ownerの並行/停止試験を確認する。六format/compile/型null/SpotBugs0、当class四counter各100を要求し、未網羅/未実行を合格へ補完しない。rawPMDは当冗長volatile一件だけ減ることを独立source/全851/1667/原XML/六Jar・全診断列で確認。

PTPRE037=PT_DEFAULT。予定command `PYTHONPATH=tools/quality:tools/quality/vm/050_s1:/home/mini/codex/project1/work/toolchain/pyflakes-3.4.0/runtime python3 -B tools/quality/pg6106_locked_flag_selected.py`。既925profileの通常owned temp/in-process Artemis/loopback/Node fixtureのみ、新onlynamespace/固定commit、実VM/本物DB/原本/failed-cohort/intent/permit/拒否操作0。後続全体/native/CHR/451/trace全終了依存/正式は別未完。新source/実時刻/command/OS/tool/終了/inputexpectedactual/coverage/hashを結果へ保存する。
