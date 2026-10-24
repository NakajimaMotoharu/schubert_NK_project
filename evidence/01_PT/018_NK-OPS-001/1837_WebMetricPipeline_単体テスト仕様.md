# Web metric dependency・pipeline組込PG／純粋単体テスト仕様

NK-OPS-001/RD171 MON005～013/UI252/SS312351/PG-D626、group2068/P018-09/C07追加費0。開始fresh48残52/reset1793382075・3/6/10pp/cap10、前群終了47→今回48の共有境界差1は2067で別記録・専有費/新予算へ変換しない。

WebServiceMetricBinding.withHttpObserverはapp依存Mapのnull entry/key/value・型整合・二重型・既observerを検査し、immutable copyへfresh pipeline observerを一つ追加する。入力Mapや値の所有は移さず、異常をcatch/format/再試行せず、検査前のobserver生成なし。新WEBSERVICE015～022=8＋同変更Main必要旧14/既HTTP22=actual44/2。

|新ID|fixture/操作|独立期待|
|---|---|---|
|015|空Map|observer一entry/出力map immutable/入力不変更|
|016|String/Integer依存・入力変異|値identity保持・出力snapshot不変/新observer一つ|
|017|null Map/entry/key/value|境界拒否・owner signal0|
|018|Class/value型不一致・primitive key|拒否/入力不変更|
|019|observer既登録|置換/二重登録せず拒否、元Map/value保持|
|020|entrySet provider Runtime/Error|元identity/呼出一回・再送/formatなし|
|021|二Map組立→二fresh observer/二request completion|別observer/同recorder count2・DB/full出力/SDK借用|
|022|不正Map providerの二重Class entry|曖昧上書きせず拒否、observer生成前のsource順序もmetadata照合|

NativeRuntimeはcontextをHTTP組立前にpartial fieldへ捕捉/initし、DEBUG bindingありだけMapを拡張、STDは元依存Mapを保持。WebHttpServerは既request trace valve後/admission前にobserver追加、observerあり/trace依存なしをserver取得前に拒否。これはPG source/compile/staticのみ、actual start/close/default/pipeline動的/coverageはUNRUN_HOLD/null。held nativeを切り出して代替実行する試験ではなく、新しい非resource Map境界だけ普通に実行する。

8946 normal六module→8948 actual44/2→8950 binding/既Handler二Main同source四100/static0→8951二caller静的PG→8952全physical/三Main差分/232owner/五edge/既業務・停止source保持→1838/scan/push。実VM/Root/native/DB/socket/credential・WebHttpServer startupは未実行。command/UTC/環境/source/exit/XML/coverage/BUG/hashはmanifest/resultへ。原4222/既成功の確認再演なし、formal1964-53/原190新受入0/QA051final/工数null/全actualHOLD保持、通常継続。
