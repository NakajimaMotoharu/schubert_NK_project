# BUG1575旧Test期待是正・元54中断保全

元PG6364/tool64530/source11ecc762fddd6a4812a7cd644cdaa437b2ae636bは2026-10-21T04:47:06.222159Z～04:56:03.578861Z/537.356702秒、agentによる自己所有fixture中断後に真正1/Maven1/phase[0,1]。新START324001/002のXML2/2成功11.262秒は観測済みだが、元54は全体未完。封緘XML24/9、残30/6は未報告（中断class内の実行済みsubcaseも未封緘のためPASS0、全て未実行とも推定しない）。原manifest a6f2ba42bde0d81b71d5526e955e8d9e5bc7f2779940b8375e11143e9abde896、archive7c78590d2d279bba7060f2fe873dbf8105498b80b9468f5d984030a96f21dea4、部分START XML f82d008bd6f920862dfe962997d466dd5c7961891080bbee1303639b0f18df1c。6366資格は未実行で、失敗元54を合格へ変換しない。

自己所有の再認証：Mavenの起動直後記録argv hashはshell→JDK execで変化しており、その旧hash一致を捏造しなかった。元runner親・Maven開始ticks・元commandの全canonical tail・専用snapshot cwd・同uid/JDKと、Maven→shell→Surefireの現在親子/leaf ticks/argv hashをpidfd取得後に再照合。2026-10-21T04:56:03.360778ZにこのSurefire JVMだけTERM、10秒内pidfd終端、Maven自然帰還1。後読取で当Maven1339091/shell1340141/Surefire1340143不在。Surefire実exit codeは直接回収不能なのでnull、TERMから143を推定0。公開 `evidence/provisional/PG6364-web-startup-interrupted-v1/manifest.json`にscope/根拠/前後条件を保存。実VM/Root/業務サービス/原本DB/Backupへの操作0、当3actor以外の全資源解放を認定しない。

## 修正するPTと独立根拠

BUG1575/YKT1330を修正前起票。SS313/342/354 SSC324は最初UNKNOWNで非復帰・後続close0を要求するのに、既scr133 startup部分は2close/return、scr131末尾はsuppressed2/returnを期待していた。Production都合の緩和ではなく承認済みSSとの不整合を是正する。scr133通常closeの同一SQLException/一回close/固定例外assert、scr131全null/未借用/実業務startup validation、他7test/実HTTP等は保持。二旧startup部分だけ、無資源の所有childへ同一Throwable mode3、worker RTE/reply checked mode1/4の非復帰を移す。nullable Replay正常closeは明示counter1へ残す。

新START002の既default五mode/独立カウンタ・frame/正常保持/割込後/固定診断・child終了expectedは維持。共通fixtureをtest-only helper化し、旧二Testは該当modeだけを選択（五modeを無意味に重複再試行しない）。追加のstartup.suppressed0は強化assertionであり、同一Throwableのself-suppression無しも保持。Test数54/15不変、削除/skip/not-run成功化0。全Production Mainは11eccと同byte、gates/Current/旧red/source/保全物を不変更。

## 次の実行

元6364へ再付着/同namespace再実行せず、新PG6370 `pg6370_web_startup_retry.py`で訂正後sourceから54/15を一回。工具は真正中断manifest/新2XML/ownedstop-postを読取し、差分を二Testだけに限定、clean保存を要求する。`PYTHONPATH=tools/quality:tools/quality/vm/050_s1:/home/mini/codex/project1/work/toolchain/pyflakes-3.4.0/runtime python3 -B tools/quality/pg6370_web_startup_retry.py`、真正0後だけ同環境`pg6372_web_startup_retry_qualification.py`で原XML/六Jar/851Main1667physical/前完全資格18からの二Main差分/PMD-CSを照合する。新工具正負二/pyflakes0、元59959正規format0。新compile/PTは未実行、sourceは保存後beginに固定する。実HTTP/JMS/PGは既自己所有temporary fixtureだけ、元実環境HOLDに触れない。

手戻り原因=既helper直接呼出のoracle横断漏れ、元9分のwall timeを週次token/専有費へ換算しない。原/v4/群開始.5/2/6は固定し、手戻りと新発見/計画完了を区別。freshused41残59/reset1793082865/secondary不明、usagebc77d6ba/N-T/専有費工数null。正式1964/53・17/190・QA051final/PTALT不明代替0/全保全維持。通常再試験/commitで停止せず、当原資格・必要同source全体/164F03/全横展開へ継続する。
