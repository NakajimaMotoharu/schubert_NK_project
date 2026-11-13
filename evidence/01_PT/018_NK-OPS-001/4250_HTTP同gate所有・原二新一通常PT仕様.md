# HTTP同gate所有・原二新一通常PT仕様

NK-OPS-001 / WBS-P018-06 / BUG-2799 / SS313342352 / UI212243253 / SYS004 AUT002 MON003。WebHttpAdmissionValve.invoke/log/Lease.ownedBy/complete、依存WebHttpAdmission全source。原whole2の全assertion/bodyを不変にし、新HTTPLEASE003を1定義追加する。

原2: terminalOnlyCompletionAndMalformedOrDuplicateCallbacks、fatalInvocationStillRequiresRealTerminalAndMissingNextNeverCompletes。null、拒否503/no-store、同request再入、終端欠落、重複callback、異型attribute、next欠落、fatalのidentityと実terminalまで保持を検証する。

HTTPLEASE003: 同じメモリRequest/ResponseにgateAのleaseを保持してgateB.invoke。固定ServletException「Web HTTP lease unavailable」、A呼出数1/B0、attribute同一性を独立literalで確認。B.logではAのactive leaseを完了できずA.drain(ZERO)はIOException、B自身は未使用なのでdrain成功。gateAを共有する別adapterは再dispatch可能でA呼出数2となり、同adapterの実terminal後だけAのdrain成功。後続重複logも成功でunderflowなし。ZEROは即時後条件の確認であり、待機や実serverを使用しない。production methodでexpectedを生成しない。

全依存はJDK25/通常Tomcat11.0.25/JSpecify/JUnit。SDKのcachedCentral SHA1とJAR/POM SHA256、constructor/static metadataをPG28986へ保存。defaultConnectorはHttp11NioProtocolのstateだけを構築し、NioEndpoint.serverSock/pollerはnull、LifecycleはNEW。init/start/bind/実HTTP/DB/JMS/Root/VM/actual4 class0。試験全3にworker/反射/実network/fileなし。

source固定後generic closed-host prestyle/RootNullAway compile/static/preflight/run/postを実終了codeごと確認する。Main2/physical3全体を保持、coverage対象はValveとLeaseの同一source2class。依存gateの未網羅は除外せず全scopeで残す。正式451/190・実HTTP・native受入は別条件。命令とsource/run/環境/終了code/XML/全counter/hashは各manifestへ保存する。未実行は合格にしない。
