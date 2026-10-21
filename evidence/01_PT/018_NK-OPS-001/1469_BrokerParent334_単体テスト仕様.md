# BrokerParent334 ordinary graph境界 PT仕様（実装前）

## 実行前固定（2026-10-22）

Main903b/全旧Test保持、新API config4method SHA b4c8fc0e50f047cb3732f298717bde29cf0b98e1b9ef9ccb2db464a469d1e1e5、API parent1 SHAe450d657a0d8045cb5a9db3eccfb60d966438969d6a0bd925a279ce59fec02a1、Web3 SHA5ab0f744557cf4619b09a06f7390956e3eb3fa7cd1cebd134fcb788611e9e189。formatter35902/管理三/pyflakes/diff-checkすべて0、動的PT未実施。実行前別pathレビューでrole/mode/arity・endpointのassertをfault capture外へ移し、spyはpublic role/mode/arityだけ記録、password引数は保存しない。open失敗でcaller-owned factoryをauto closeしていないこともcapture後に検査し、caller TWR終了時だけclose1/各三reverseを検査する。

`python3 -B tools/quality/pg6690_broker_parent_selected.py PHASE`（PYTHONPATH既三path）。新onlyAPI赤6690/17-9→実11-6 F5、Web赤6692/15-8→実13-6 F3を予測し、read-api/read-webで専用FACT334 message八件を完全照合する。原真正終端/原資格後だけ必要四Main・全新旧Test bytes固定。green6694=127/33（core83＋新8＋既API broker8/provider3/factory4/finite retention2/parent10、Web broker4/factory3/finite retention2）、原6696は直前83/8e521231の全Main mapに必要四source差だけを許し原Jar/XML/全8511667/actual counter/raw静的へ結合する。

既ApiFactoryNativeRetentionTest/WebFactoryNativeRetentionTestはsourceを確認し、未接続locatorと自分で開始するfinite child/watchdogだけ、実native admission/VM/Root/cohort操作なし。新変更がUNKNOWNの非帰還をcatchして進まないことの普通の単体契約として回帰し、actual native資格へ加点0。provider内enumの物理debug差が出る場合もowner/nested whitelistだけで機能差と決めず原bytecode/source blockを別照合する。fresh69使用/31残/reset1793082864/secondarynull/券0、N/T/専有費/工数率不明はnull、原/v4/開始予算は固定。

NK-MSG-001/002、ApiBrokerContexts/ArtemisConnectionFactoryProvider/ApiMessagingRuntime/WebBrokerContexts、RD MQ001～010/SYS004/UI231243253/SS312321342354/SSC334、BUG1604/1606・YKT1357/1359。設計only e48cd5e6d/PR198→mainb6f09c9a2cf918656e8b0500896ce963d6512257は二SS/914三fileだけ通常merge/remote確認、code/tool/evidence混入0、添付cap100一回失敗/迂回0、PG/PT未受入。

485現物でcost ownerを確認し主P005-03（API broker/parent）、P005-04（provider）/P005-02（Web broker）は共通参照追加費0。群ORDINARY_BROKER_PARENT_GRAPH/event1674の着手前低.5/標準1.5/高4共有ppは未較正・固定、原/v4・旧1672値は変えない。source903b8b93f/原83-8e521231をbaselineとし、旧f16f/4170/75a039af/tracef49aafdeと区別、旧成功を新sourceへ足さない。

## PT_DEFAULT・fixture/独立期待値

API/WebのConnectionFactory/JMSContext/consumer/owner interface proxyと、既testability portの未接続InVM locator factoryだけ。APIのApiFactoryOwnershipTest.ProbeFactory/WebのWebBrokerFactoryOwnershipTest.ProbeFactoryは入力thrower/実setting・close counterとして再利用し、expectedをProduction methodや既Test実行結果から生成しない。factory fixtureはcaller finallyのdisposeで自身の未接続locatorを解放、実接続/sessionは作らない。partial-constructionはpublic/既package portから三providerを組み、private fieldを反射で差し替えない。

password copyは既PTと同じ公開synthetic二文字だけ、実credential/key/session/master/DBを取得しない。supplier/createContextのRTE graphをcause/suppressed/JMSlinked/SQLnextで事前固定Errorへ接続する。コピー取得前にsupplierが失敗したら未取得とし、createContext失敗では既finallyの全zeroを観測する。roles nk_api/nk_web/TRANSACTED mode、setting callTimeout2000、plain非fatal診断はSS321と既独立ApiBrokerContextsTest/WebBrokerContextsTest・FactoryOwnershipTestのliteralをoracleとし、provider text/cause/suppressedをfixed catalogへ持ち込まない。

|Test ID（予定method suffix）|入力/操作|独立期待値と実行順|
|---|---|---|
|FACT334001 ApiOpenPreRedactionAndCopyCleanup|三API profile/二fault点×四edge Error、direct Error/非fatalcycle control|supplier1、create0/1、nk_api/mode0固定、未取得copyは不変/取得copyはzero。caller-owned ownerはcallerが全三を一回reverse close後に元Errorを判定、ordinaryは既fixed context unavailable/cause-supp空|
|FACT334002 ApiMultiOwnerCloseRetainsLateGraphAndSuccessfulPhases|第一close普通NoSupp RTE、次ownerだけgraph Error、残正常|close順2,1,0/各1、secret/context作成0、元Error。fixture故障だけ除いて明示component closeを再試行すると2,1だけ/成功0再closeなし、最後idempotent。実cohort回収ではない|
|FACT334003 ApiPartialConstructionClassifiesOnlyUnretainedSecondaryAfterAllClose|第三provider NoSupp失敗、先二ownerのclose graph|provider三profile順、close順1,0をすべて一回後に未保持graphの元Error。標準supp primaryなら既raw primary identity/個別reverse secondary順、同一object非自己抑制をcontrolで維持|
|FACT334004 ApiFactoryNoSuppSecondaryAfterOwnedClose|既unconnected setter fixtureの第一setting NoSupp＋close graph四edge|set callTimeout=2000だけ/close1、元Error、caller finally dispose。既直接primary/close表は旧独立domainへjoin|
|FACT334005 ParentNotificationAndGroupCloseAfterCleanup|public parentの未取得WebLog factory NoSupp＋通知graph、既Sync四context/返却済groupのlate graph|通知1・Sync全四close0,1,2,3/async未取得/業務0後に元Error。返却済全group closeは5,4,0,1,2,3、既成功groupを再closeせず未確認groupだけ明示再試行。private group偽造0|
|FACT334006 WebOpenPreRedactionAndCopyCleanup|二fault点×四edge Error、direct/ordinarycycle control|supplier1/create0/1、nk_web/mode0、copy状態・caller owner close1、元Error又は既fixed Web context unavailable/cause-supp空|
|FACT334007 WebCloseTraversesLinkedGraphAndRetainsRetryPhase|single ownerの四edge Error、特にJMSlinked、ordinarycycle|owner close1/secret-context0の後に元Error、故障を除いた明示component closeは二回目だけ/三回目idempotent、ordinaryは旧fixed close catalog/cause-supp空|
|FACT334008 WebFactoryNoSuppSecondaryAfterOwnedClose|既unconnected setter fixture第一setting NoSupp＋close graph|set callTimeout=2000だけ/close1、元Error、finally dispose。旧直接表/setting12/windowは既domainから当sourceで回帰|

各identity assertは専用FACT334 messageで、先に回数/順序/role/mode/zero-op/wipeを検査し、fixture未知操作・別失敗を予定反例に算入しない。Error objectと期待整数/list/文字列は事前固定、production encoder/mapperでexpected生成0。親の非Error childは実componentのcause carrier/直接Error契約を前提に最終mapper前で点検し、反射や到達不能扱いでbranchを作らない。

## 実行前判定と品質依存

実broker/DB/network/credential/service/VM/Root/cohort/intent/permit/actual native操作0、拒否境界を探す試行ではない。既UNKNOWN非帰還policyは権限解除/正常成功へ読み替えず、普通callback returnとfinite own child fixtureの単体契約を必要範囲で回帰する。実native資格/CRC/所有/後条件は別HOLD。

新三Test class八methodを予定。compile-first全六/format/null/staticを維持、赤はAPI新5/2＋baseline12/7=17/9（API停止実11/6・予定F5）、Web新3/1＋baseline12/7=15/8（Web停止実13/6・予定F3）。各新onlyrunで真正1/phase0,0,1/source/archive/XMLと八専用Error identity failureを照合、別compile/error/skipped/flakyは加点0。Main変更は両元終端と原資格後だけ、全新旧Test byteを固定。greenは旧core83と新8/旧factory/broker/parent domainをjoinし、実宣言数を独立inventoryで固定してから開始する。原Jar/XML/全8511667/必要四Main差/coverage/PMD rawを照合し、関連群の必要同source全体/四counter/F03/traceへ進む。

現当群PG/PT未実施、Test source hash・run/command/日時/OS/JDK/終了code/input-oracle-actual/coverage/BUGSSC・manifest hashは着手・元結果へ追記する。全体件数や未測定coverageを先に合格化しない。formal1964-53/個別17-190/工数null/QA051final/全HOLD/PTALT代替0・原-v4維持。
