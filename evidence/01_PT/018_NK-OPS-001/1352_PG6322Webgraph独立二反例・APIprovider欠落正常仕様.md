# PG6322 Webgraph独立二反例・APIprovider欠落正常仕様

NK-MSG-002/MQ006008/MON003・UI213241242・SS324§8/9/354/SSC322323、BUG1572/1573・YKT1323/1328。SSC323のdesignだけPR184/source99c82317af3034f90470137bb042e12d598df0ba→main363fbe5621f1572ef4cfd42f291f7c2bc52c7d12通常squash/fetch確認。三文書10insertのみ、未受入実装/試験/tool/evidence混入0。artifact登録100identity上限一回失敗/再試行0。

Main全851は原86/6320資格済 `65facffca6123ab4314864b4e934b6d4b007404e` 同byte。変更はAPI OutboxDispatcherTestの新normal一、Web Dispatcher/ReplayWorker各新反例一だけ。既red二Test/oracleは不変更。元76731 pinJDK25.0.4/既Maven正規Spotless真正0・三Testだけ整形。新red53/10実宣言/元86資格・all851/三target明示・wrong qualification hash拒否の二工具Test0、Production PT未起動。

GRAPH322003：JMSExceptionのlinked欠落・SQLExceptionのnext欠落を固定非fatalgraphへ入れ、既専用temporary API DBで通常Report(1,0,1,0)、open2/ERROR/attempt1/JMS_SEND_FAILURE/next NOW+1秒/lease nullを確認する。元red001/002の入力/期待/fixtureは変更しない。新Mainが既実装済みでも実未実行を合格へ計上0。

GRAPH323001：WebLogReplayWorkerの自己所有actionが、JMS linked Exception.cause Error、SQL next.cause Error、cause/suppressed循環重複の固定graphをthrowする。期待はterminal true/nonrunning/action1/completedCycle0/failedCycle0、finallyで当workerをjoinする。Error無し/nullable provider edgeのgraphはfailedCycle>=2でrunning・非terminal・completed0を維持する。別process/実VM・Root・業務処理の起動/回収ではない。

GRAPH323002：既専用temporary Web DBに独立SS byte goldenからsynthetic codecで暗号化した一行をenqueueし、JMS取得だけで前記graphをthrow。fatal期待は元LinkageError identity・DB open1/claimのみ/PENDING/attempt0/error null/next NOW/lease graph/期限NOW+10秒、JMS1。非fatal nullable graphは通常Report(1,0,1,0)、open2/ERROR/attempt1/JMS_SEND_FAILURE/next NOW+1100ms（既jitter+100境界）/lease null。SS324§8.3/9と既backoff境界から独立算出し、production traversalや結果をexpected生成に使わない。元DB/Backup/鍵へ接続せず、Test用codecのzero fixture keyだけを使用する。

red command=`PYTHONPATH=tools/quality:tools/quality/vm/050_s1:/home/mini/codex/project1/work/toolchain/pyflakes-3.4.0/runtime python3 -B tools/quality/pg6322_web_graph_red.py`。clean Test-only commitから新only pg6322-web-graph-red-v1へ一回。原86/全851の保存資格を入口とし、確認のための中間4045全体を反復しない。宣言53/10は期待総数でPASSではない。元真正終端/失敗/未到達/hash回収までMain/Test/gates固定→二Web MainPG→当同oracle/APIも含む89/15/原資格/必要同source品質をまとめる。

matrix数のJUnit水増し0、未実行/失敗/未知coverageと拒否PT代替完了を成功へ補完0。群1537の当初.5/2/6・追加発見/残見積を分離、原/v4/実N-T専有費工数null・正式1964/53/17/190/QA051final/PTALT不明/実環境HOLD/全保全維持。freshused37/残63/reset1793082864/secondary不明、通常小群/commitでは停止しない。
