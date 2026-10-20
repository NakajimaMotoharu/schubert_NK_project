# 1276 SSC311 Web factory所有のPG/PT仕様

NK-MSG-001/002、WebBrokerContexts.create/newFactory/configureOwned、RD MQ-001/002/003/006/008・SYS-004、UI231/243/253、SS321/343/354、PG-D458、BUG1537/YKT1297。設計正本main cec3c595c798ece14aba7a3aac16b16df8b9a4e1/PR167を反映後の実PG。1462開始0.5/2/6ppの内部stage0.25/1/3pp（非加算）を維持。

| Test ID | 入力・操作 | 独立期待値 |
|---|---|---|
| MQFACT311001 | 未接続の自己所有Artemis factoryを一回取得し12設定、null port/null return、取得IAE/ISE/NPE/Error | 設定順と12リテラルを独立固定表で照合、正常same live owner/close0/user/password未設定、取得失敗same Throwable/closeなし |
| MQFACT311002 | 設定1～12各位置×IAE/ISE/NPE/Error | faultまでの固定prefix、一回close、same primary、suppressed0（48内部入力を48JUnitへ水増ししない） |
| MQFACT311003 | primary4種×close4種、同一Throwable4種 | 独立表：close Error対primary非Errorのみclose優先、他はprimary、他方一度suppressed、同一はsuppression0、一回close |
| MQFACT311004 | 当生成Jarのcreate/constructor/helper/例外表を独立読取 | owner/lock/password portは取得前、取得後設定はtry保護、成功後はsame factory最終field格納だけ。公開ABI・既live close retry不変 |

JUnitは新3件。新Testは接続/sessionを開かず、finallyで自己所有locatorを解放する。実heap枯渇、実broker/VM/current状態やroot終端を検証したとはしない。null/endpoint不正/正常public create、credential消去、live owner close再試行、既consumer/assembly/並行等は当全Webを影響選択する。providerに新認証値を設定しない。

**PTPRE035 = PT_DEFAULT**。予定command `PYTHONPATH=tools/quality python3 -B tools/quality/pg6080_web_factory_selected.py`。wrapperはgit archiveの新only snapshot上で既Maven offline format/package/Jacoco/SpotBugs六moduleだけ、固定Node24.19.0でWeb fixtureを実行。全Web917＋他module guard8＝925件/150suite、Main1667、当WebBrokerContexts四counter全100を要求。自己所有in-process broker、loopback・tempfixtureだけ。VM/配備/本物DB/原本Backup/鍵/failed-cohort/intent/permit/権限変更・拒否再試行0。既6074の成功は新sourceへ輸入せず、source/branch/実command/JDK/OS/終了/元XML/coverage・全Jarとhashを実manifestに保存する。次は追加build/PTなしの独立原XML/全8511667/無除外静的/公開ABI/実取得順序、その後変更群の必要fresh全体。未測定・未実施・代替レビューをPASS/coverageへ加算しない。
