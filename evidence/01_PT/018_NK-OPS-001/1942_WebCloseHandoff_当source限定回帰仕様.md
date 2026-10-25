# Web private lock変更後・未登録owner完了通知の限定回帰

2026-10-25 17:16 JST、WEB_CLOSE_HANDOFF_QUALIFICATION_V1、主WBS-P018-06。開始08:15:42UTC使用4/残96/reset1793513544/secondarynull、見積.5/2/6pp/cap10。Production64446不変更。原/v3/v4/v5予実・451・承認済仕様・モデル・全actualHOLDを維持。

## 実行の必要性と安全条件

64446ではWebProcessLifetime.closeのprivate monitorが明示ReentrantLockへ変わった。9248の既4件には、既close後に別threadがshutdownへ入るケースはあるが、別threadがfinishedを待機中に現closeが通知する交錯の当source資格はない。従って全4222成功確認や原test再演ではなく、変更されたcloseと待機側の結合に対する必要な限定回帰とする。原結果と新結果を足して試験数/coverageを作らない。

対象既存Test ID NATIVE-LIFE002、WebProcessLifetimeTest#life002ForeignHookWaitsForActualOwnerNotificationAndPreservesInterruptの一methodだけ。元Test source SHA c9cbb3629a84c507d7da7df3484aa0cf5807664400c38439ec5e1f6edbbb324b、compile上必要な未実行CallerMonitorProbe SHA e502853332c70415707eb38f8aa52e0096f54c4a106c21a51d23cb47cbbda9fd。JUnit selectMethodを完全名/一methodへ固定し、class全選択しない。元classには未選択HookDriver/native methodが含まれるが、それらを発見・開始・実行しない。Test本文/期待値/Production変更0、新ID0。

選択methodは未installのnew WebProcessLifetimeと自己所有platform Thread・latch/atomicだけを使う。worker自身のinterrupt通知→lifetime.shutdown待機、試験ownerのlifetime.close→三秒joinで回収。Runtime.add/removeShutdownHook/実TERM/ProcessBuilder/実main/provider/ネットワーク/DB/Root/UNKNOWN保持/私有raw/native実体/外部所有/鍵/intent/permit/配備には到達しない。未実行CallerMonitorProbeは型解決のためcompileするだけ。この純粋な有限component PTはPT_DEFAULTであり、拒否PTの再試行/代替実行やnative操作ではない。

## 独立期待値・受入

SYS004/AUT002/MON003、UI212/243/253、SS313/342/352、origin/main8b91944dfのSS342「通知のみ、owner完了待ち、close/exitしない」と元NATIVE-LIFE002のliteral期待値を正とする。owner未close時にstopping=true・finished=false・worker alive、close後はjoin成功・finished=true・interrupt保持=true、二回closeも成功。これらをProductionでexpected生成しない。主な観点は正常/並行/既割込/冪等・独立した完了通知であり、null/実hook登録/UNKNOWN/実nativeの全分岐は当選択対象外の未実行を保持する。

固定正常9246原989d9e912a0a6531ad8a2417467ddca6d37a292d6582206fb696b324c600ee46を再buildせず、全current input/六Jar hashを検査して使用。自己所有のfresh Test compile/JUnitだけ。found/started/succeeded=1、failed/error/skipped/aborted/not-run=0、選択method完全一致・実exit0・XML/hash/session/同sourceが必須。成功を推定で保存せず元終端を回収する。coverageは新しい当runだけを全WebProcessLifetime物理classへ照合し、missも公開する。旧exec union/部分class除外/100%補完0。

実行commandはPYTHONPATH=tools/quality:tools/quality/vm/050_s1:work/toolchain/pyflakes-3.4.0/runtimeのpython3 -B tools/quality/pg9580_web_close_handoff_host.py、独立post/coverageは別9582。OS/JDK/依存/source/入力/command/exit/時刻/XML/exec/hashを公開manifestへ保存し、candidate/raw秘密値は出さない。BUG1743/YKT1494の限定回帰であり、実install/IRQ UNKNOWN区間PTのHOLDは解除せず、障害CLOSED/全PT/四100/451/正式1964-53/17-190/工数nullを変更しない。前G07のJar digest選定は4493中7件だけで、全Jar公開証明を新群へ広げず新分類0のまま別工程へ移った。
