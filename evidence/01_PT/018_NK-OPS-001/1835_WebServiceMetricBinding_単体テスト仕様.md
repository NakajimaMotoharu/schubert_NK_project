# Web DB＋HTTP terminal metric binding 単体テスト仕様

NK-OPS-001/RD171 MON005～013/UI252/SS312351/PG-D625、group2065/P018-09・C07追加費0。開始fresh47残53/reset1793382075・3/6/10pp/cap10。新WebServiceMetricBindingは既DB bindingとHttpMetricRecorder/HttpMetricValveを一つのcaller-held custom registryへ登録し強保持する。factoryはresource-free、DEBUG initialize時だけ借用pool/config参照、refreshはDB四getterのみ、HTTPは既terminal logで一回記録。STD contextはsetup/supplier未読。binding自体にpool/registry/server/workerの所有・close・start・I/O権限なし。

|新WEBSERVICE ID|入力/操作|独立期待|
|---|---|---|
|001|constructor null/未知mode|入力拒否/getter0/不正modeのseries0|
|002|factory null supplier/mode/callback/未知mode|境界拒否/取得0|
|003|STD/読まれるとErrorの参照supplier|setup/bean取得0、固定readyだけ/空bindings|
|004|DEBUG deferred→owner捕捉→init→render|pool/config各一回/init getter0、DB1/1/0/2・HTTP初期0|
|005|borrowed valve getter/refresh|同一valve強保持、DB四getterのみ/SDK open|
|006|standalone STD binding・valid terminal|詳細series0/DB未読、HTTP結果不変更|
|007|/login GET200 terminal250msを二回|counter1/timer count1・sum0.25、DBと同text/HTTP不変更|
|008|再dispatch/own並行terminal|同request一回claim/他request別、有限Future回収|
|009|null/欠観測terminal|owner signal/成功補正0、request metric0|
|010|pool supplier Runtime/Error/null|primary/後段config0/再init拒否/partial owner保持|
|011|config supplier Runtime/Error/null|pool→config一回/getter0/primary・再init拒否|
|012|HTTP成功後DB getter故障→明示回復|renderは元失敗/partial成功0、既HTTP countは再送せず1保持|
|013|owner terminal callback故障|元identity/自動再送0/SDK借用保持|
|014|quiescent owner close|contextだけSDKをclose/以後access拒否、借用bean close/control0|
|WEBMHTTP022|新binding terminal→context→既Handler memory GET二回|DB＋HTTP固定golden/200/ready1/byte長/header/close1、HTTP business count再計上0|

14新＋HTTP新一=新15、必要既HTTP21=actual36/2。既WebDbPoolMetricObservationTest.Fixtureはhelper compile-only。Request/Response/Connectorは自己所有・未起動、network/socket/JMX lookup/DB/VM/Root/native/WebHttpServer startを行わない。期待はSS name/tag・独立literal/order/250000000ns÷1e9、原例外identity/explicitHTTP値で作りproduction expected生成0。

8922正常六module→8924 actual36/2→8926新binding/既Handler二Main同source四counter100/静的0/CRC-session→8928全1835physical/旧1834不変・owner/private保持/borrowed protocol・旧HTTP21本文保持→1836/scan8930/保存push。全observer/recorder/context・実pipeline/endpoint/全451の100%とはしない。実NativeRuntime/WebHttpServer組込PGはこの有限部品群後に別依存として進める。command/UTC/環境/source/exit/XML/coverage/BUG/hashは元manifestと1836へ、formal1964-53/原190新受入0/QA051final/工数null/全actualHOLD不変。
