# PT・IT試験観点詳細設計

## SSC341 Morning既知SQL catalog境界・独立故障PT（2026-11-13）

SS332 SSC341、SS341/343、BUG2852/YKT2359。production分類methodをexpected生成に使わず、fixtureで事前固定したError/unknown object identity、SQLSTATE、固定catalog、literal close/wipe/operation件数と既typed優先を期待値とする。元20変換siteはPG29726の公開source hash/行/捕捉型で固定し、queryのResultSet/Statement二scopeとexecuteの所有connectionを別に確認する。

|Test ID|独立入力・期待値と後条件|
|---|---|
|PT-MDB-CAT341-001|非fatal SQL/Batch例外の既固定IOException message/cause/suppressedを保持、成功へ戻さず取得済connection close1/credential消費1。|
|PT-MDB-CAT341-002|SQL cause/suppressed/nextの各Errorを元identityで伝播。未知provider文字列を新catalogへ出さない。|
|PT-MDB-CAT341-003|非fatal自己next/相互cause/suppressed循環は有限帰還し既固定診断、同一Throwableの再利用も自己抑制しない。|
|PT-MDB-CAT341-004|最外known SQL内Error＋未知cleanupの二故障で、分類後の実Errorがprimaryとして保持される。owned close/credentialwipeを省略しない。|
|PT-MDB-CAT341-005|非fatal SQL primary＋未知cleanupは既cleanup元identityの選択を保持、SQL graphだけを理由に元非fatal型順位を変更しない。|
|PT-MDB-CAT341-006|body成功＋SQL close内Errorは成功値を返さず元Error、SQL close非fatalは既固定IOException。close再試行0。|
|PT-MDB-CAT341-007|SQL/Batch primary＋SQL secondaryはprimary graph→secondary graph。片方/両方Errorと両非fatalを独立に確認。|
|PT-MDB-CAT341-008|checked IOException/CleanupStoppedException primaryの既固定化/typed policyは不変、SQL専用確認を一般化しない。|
|PT-MDB-CAT341-009|未知Runtime/Error primaryの同一性・fresh固定secondary・suppression無効/同一objectを既表どおり確認、raw secondaryを公開しない。|
|PT-MDB-CAT341-010|null/欠落・取得前拒否・credential consume/wipe/Properties clear・Session callback後失効と異thread拒否の既契約を退行させない。|
|PT-MDB-CAT341-011|query rows→statement→owned connectionの必要close各1、未取得close0、追加commit/rollback/SQL/stop0、原role/SQL/bind/timeout/所有後条件を維持する。|
|PT-MDB-CAT341-012|当source whole MorningDB/owner/実DB依存の関連回帰・全scope四counter・NullAway/静的・原本/同run/同budget/終了依存を照合し、部品source reviewを実所有や正式451に代用しない。|

実環境の前提未成立なら製品PTはNOT_RUN、coverageは未測定として残す。新しいfake DB/Root/issuer authority、held Testのmethod抽出、拒否操作のprobe/retryを行わない。独立した既許可host作業は継続できる。PG/静的代替は製品PT PASS・実測counter・正式1964/53・IT/STに加算しない。


## SSC340 条件付きNN・複合CHECK NULL負例PG/PT（2026-11-13）

BUG2846/YKT2405、SS331 SSC340、WBS-P004-01.01～03。独立期待値は次表の正常/拒否結果とSS331に置き、production SQL式やproduction methodをexpected生成器にしない。各負例は他のNN/FK/state/size条件を満たした合成rowを使い、SQLSTATE23514に加えて対象constraint名を確認する。他制約やFKによる拒否を当条件の再試験成功へ算入しない。

|Test ID|入力・操作と独立期待値|
|---|---|
|PT-DB-NULL340-001|MUSIC M/IのkeyNULLと空/257byteを拒否、1/256byteを許容。|
|PT-DB-NULL340-002|MUSIC roleNULL/未知値を拒否。M/I/Nごとの正規組合せを固定literalで許容。|
|PT-DB-NULL340-003|VIDEO両NULLを許容、どちらか一方又は両方の非NULLを拒否。|
|PT-DB-NULL340-004|MUSIC N/keyNULLを許容、N/key非NULLを拒否。|
|PT-DB-NULL340-005|失効済sessionのreasonNULL/未知値又はrevoked_atNULLを拒否、既6値reason＋時刻を許容。|
|PT-DB-NULL340-006|未失効session両NULLを許容、時刻又は理由が残る組合せを拒否。|
|PT-DB-NULL340-007|Notification ERRORのcodeNULL/message有及びcode有/messageNULLを拒否、既5code＋messageを許容。|
|PT-DB-NULL340-008|非ERRORのerror pair両NULLを許容、片方/両方有を拒否。|
|PT-DB-NULL340-009|Inbox ciphertext有/keyNULL及び逆片方NULLを拒否、両NULLの許容は既state/sensitive-result条件も同時に確認。|
|PT-DB-NULL340-010|snapshot両NNでbyte29/1,050,000を許容、28/1,050,001/不正keyを拒否。暗号実体ではなく非秘密合成byteでDB長/ペア条件だけを試験。|
|PT-DB-NULL340-011|USER/QUESTION/JOB/SCENARIO_FILEでidNULL又はuuid有を拒否、N12 min/maxとUUID NULLを許容。|
|PT-DB-NULL340-012|AUTH_SESSIONはUUIDだけNN、NONEは両refNULL、PROCESSINGは全関連NULL。半端/未知type/範囲外を拒否。|
|PT-DB-NULL340-013|版28の不整合rowを保全したupgradeは版29validation失敗・rollback、旧row/旧constraint/旧checksumを保持し、成功履歴を捏造しない。失敗履歴の有無は実DB/Flyway契約に従い観測する。|
|PT-DB-NULL340-014|正常upgrade/validate/冪等再適用、旧28resource byte/checksum不変、24table/159CHECK/FK/UK/index/rolegrantとschema履歴六列の不変を照合する。|
|PT-DB-NULL340-015|明示optional NULL/QA050未知expiryの保全、既state/lease/operationtoken/owner/参照・暗号/保持の他gateを退行させない。|

PGではappend-only DDL・主担当artifact・版一覧・独立SQL fixture・TestID・rollback手順/traceを一貫させる。実DB PTは固定source/run・必要権限/所有が成立した後に行い、whole候補の抽出・fake authority/DB・無許可SQL実行をしない。HOLD中のPG強化review/許可静的代替はNOT_RUNのDB PT、未測定coverage/null及び残存リスクと分離して記録し、PASS/四counter100/正式451/IT-STへ混ぜない。全体の既coverage100%・同source全scope/run・CHR/DIF・終了依存は緩和しない。


## SSC335 Web管理lock/join残budget PG/PT（2026-10-22）

BUG1627/YKT1380、PT-WEB-MGMT335001～003。自己所有ephemeral loopback HttpServer/実executor、有限latch/watchdogと二workerだけを使い、実VM/Web/Root/cohort/原本/鍵/permit/Unit操作を要しない。旧Mainで零budget競合・lock待機中IRQ・既IRQでstartとの競合の有限反例を保存し、同Test bytesと全既oracleを固定した是正後に通常PTする。入力null/負/>30秒、正常/再close、stop/join不確定、取得前準備・例外優先は旧表も維持する。

held第一ownerを解放する前の固定IOException・cause/suppressedなし・IRQflag・vendor stopの回数を独立literalで確認し、停止要求後のlate promotionを拒否する。finallyで当fixtureを解放し全Future/worker/実executorを回収、実同port再bindを確認する。時間測定だけで成否を推定せず、第一ownerを保持したまま第二が帰還するlivenessと後条件で判定する。vendor自身の非帰還/全体nativeは未検証のまま、実Root/既HOLDを解除しない。

新/旧domainの元XML/同source原Jar/四counter・静的raw分類・必要全体/traceを照合する。未実行PTや既data-only sourceのsubsetを新Main/global100へ合算しない。代替PTの免除ではなく通常PT、正式/工数率・実環境完了へ加点0。
## SSC334 ordinary broker/親runtime PG/PT（2026-10-22）

BUG1604/YKT1357・1606/YKT1359。自己所有ConnectionFactory/JMSContext/consumer/owner interface proxyと未接続ActiveMQ locatorのsetter fixtureだけで、API/Web supplier/createContext四edge fatal graph・finally copy wipe、API多owner/Web単owner closeのlate graph・全必要順/数・成功phase再close0を独立Error identity/整数literalで検証する。実credential/DB/network/VM/Root/failed cohort/permit/実native操作を発行しない。fixture locatorはcaller finallyでdisposeし、報告close失敗を実環境の解放成功へ変換しない。

provider/Web configureOwnedのNoSupp primary＋close graph、API partial-constructionの第三provider失敗からreverse closeをすべて試行してからのfallback、親runtimeの未取得Web-log factory NoSupp＋通知graph/既取得Sync全closeを反例化する。標準suppressionでraw primaryへ保持できるpartial factory outcome、直接primary/closeの既表・same object非自己抑制・非fatal固定診断は別controlで維持する。parent closeはpublic/既testability portから実childを組み、reflectionでprivate groupを偽造しない。

production methodでexpectedを生成せず、事前固定Error object・SSのrole/setting/diagnostic literal・明示close順/zero-op/wipe表を使う。原counterexample/同source input hash→必要PG→全新旧Test bytes固定/既domain→原Jar/XML/全Main/四counter/静的/traceへ結合する。実測不足/native/CHR/正式・拒否PT代替は分離し、代替完了や実環境所有の証明へ補完しない。

## SSC333 ordinary startup/multi-close secondary PG/PT（2026-10-22）

BUG1604/YKT1357。自己所有JMS interface proxyだけで、NoSupp Runtime primary＋通知/closing側のcause/suppressed/JMSlinked/SQLnext Errorを固定object identityで再現する。startup通知一回/close必要全数・順序を先にassertし、その後の元Error選択と、普通非fatal時の既catalog/cause/suppressed・same object非自己抑制・直接primary/直接closeの既優先を確認する。期待値は事前固定objectとliteral counter/table、Production methodをexpected生成へ使わない。

Sync四contextは第一close失敗からも各一回を試行し、成功済phaseは次の明示component closeで再closeしない。全close前の早期fatal throw、追加ACK/commit/start/業務再送、診断の公開JSON漏出を禁止する。onUnconfirmedは普通callbackの呼出/引渡し・正常return後だけの分類を観測し、実native非帰還UNKNOWN・所有の資格をproxyだけで認定しない。既SSC332/通常domain・当source全体/四counter/静的/traceとjoinし、native/拒否PT代替/正式認定へ混ぜない。


## SSC332 ordinary consumer graph/rollback実証 PG/PT（2026-10-22）

BUG1602/YKT1355・1354、PT-JMS-CONS332001～008。自己所有のJMSContext/JMSConsumer/BytesMessage interface proxyだけを使用し、外部broker/DB/VM/Root/原本/鍵不要。最初のbody getterに固定Runtime/JMS/Errorを注入し、DLQ/processor到達0、rollback回数・owner通知・ready/terminal・元Error identity/後続配送無処理を独立counterで確認する。expectedは事前固定object/整数literalで、Productionで算出しない。

API三consumerは確認済rollbackでもcause/suppressed/JMSlinked/SQLnext内Errorをhalt/既通知へ分け、通知正常return時は元direct Error同様returnする。ordinary cycleは有限で確認済だけretry、配送別reset/context別stateを保つ。Webはnull/preflight未確認、rollback Error一回性、graph/direct Errorの通知後identity、通知Runtime/Errorの非優先、ordinary confirmed retry/停止後無処理/public onMessage互換を検証する。

原反例→必要PG→同新旧Test bytesで既domain・同source必要全体/四counter/静的/traceを照合する。局所proxy成功をprovider実測/実native/Root/PGPT正式認定や拒否PT代替へ転用しない。未実行/UNKNOWN/別sourceは加点しない。

## SSC331 ordinary local audit/terminal callback PG/PT（2026-10-22）

BUG1601/YKT1354、PT-WEB-LOCAL331001～004。既sourceでprimitive logger Runtime内包Errorの破棄、terminal Runtime graphの固定catalog化をpure System.Logger/Runnable/DataSource proxyで独立再現し、DB/VM/Root/外部JMS・実鍵・session発行を要しない。expected Errorは入力とは別に固定作成したobject identity、通知順/回数・DB/identifier0、JSONの明示literalで判定し、Production methodでexpectedを生成しない。

logger cause/suppressed/JMS linked/SQL next（isLoggable/log各fault点）→通知1後の元Error、callback graph→logger graphの選択、直接logger Error通知0/直接callback Error通知1の旧優先を確認。非fatal cycle/same object/両ordinary/disabled loggerは有限帰還し、従来fixed IllegalState（cause/suppressedなし）又はfalse、成功loggerは通知0を確認する。provider canaryをJSON/catalogへ保存しない。元callbackを再試行せず、HTTP応答/DB/JMS/識別子発行を追加しない。

当四Test・既REQUEST/projection/Web port域と必要な同source全体/四counter/静的/traceを区別する。未実行/失敗/別source/nativeは合格へ補完せず、拒否PTの代替にも混ぜない。SSC331補足/必要PGは実Root/cohort/permit等の操作権限や未特定拒否scopeの解除を含まない。

SSC330（BUG1593/YKT1346）：自己所有DataSource/Connection/JMSContext/consumerのinterface proxyだけで、API/Web双方のDB primary又はclose graphだけのError、JMS cause-linked-SQLnext又はclose graphだけのError、非fatal循環/未知値/null、直接primary/直接close優先を独立literal/元Error identity/counterで検証する。close各一回、DB失敗時JMS開始0、後続ready0、非fatal固定診断/cause null/suppressed0を要求する。pure graph全edge/重複/循環/優先及びsecondaryの同一object/別object/null/suppression無効も確認し、caller finally/TWRで残るcloseの後条件を別に照合する。PT-API-READY-GRAPH330001..003/PT-WEB-READY-GRAPH330001..003等、修正前red→PG→同oracle/既domain・当source品質へ結合。実DB原本/VM/Root/鍵/permit操作・拒否探索を行わず、PT代替/native受入へ外挿しない。

SSC329（BUG1592/YKT1345）：最初のpublic JdbcSyncRequestProcessorを自己所有JDBC proxy/固定request/clockだけで試験する。SQL又はProtocol primary＋close Error、直接Error＋rollback/close故障、同一Throwable close、cause/suppressed/nextとcycle/非fatal、通常commit/rollback/closeの順と各一回・結果未返却/元Error identity/固定診断を独立counter・literalで照合する。未修正sourceの目的赤を保全してから最小PG/同oracle greenを行う。共有分類の全edge/null/重複・循環・優先は別pure graphで網羅し、各mapperの変換/SQLstate前呼出・borrowed/owned資源境界をsource/JVMと当methodの独立PT/XMLへ結合、必要な直接faultを追加する。PT-TX-GRAPH329001～、113候補と非SQL marker catchの全適用性matrix・必要同source全体/四counter/静的を要求。実DB原本/VM/Root/鍵/permit/cohort操作・拒否境界探索は不要、PT代替やnative受入の意味にしない。

SSC328横展開追補（PG前）：RevocationRetryCoordinatorのJDBC transaction境界もnextを欠くため、PT-REVOCATION-GRAPH328001..003を追加する。SS314の対象を三Main/新九Testへ確定し、初期二Main/六Testの記述より本追補を優先する。固定SQLException.next→cause Error、cause/suppressed/nextの循環・重複/非fatal有限帰還、既root/causeの優先をpure fixtureで検証し、既RERUN005のSQL/cleanup・再送間隔・資源後条件を非回帰とする。旧graph成功を新edgeへ転用せず、反例→最小PG→同oracle/既domain/当source品質を結合する。実wire/DB原本/Root/Unit/VM/cohort等を新しく操作する承認ではない。

SSC328（BUG1591/YKT1344）：ordinary認証/session JDBC分類のcause/suppressed/SQL nextをpure固定Throwableで検証する。APIはcause先だけのError、SQL next→causeのError、WebはSQL next先だけのErrorを元objectで捕捉し、普通catalogへの変換を許さない。cause/suppressed/nextの混合cycle・duplicate・Error無しは有限帰還、直接primaryと既edgeのError優先順位はSS314どおり不変更、非fatal診断は従来の固定redactionを維持する。新Test六methodの独立期待と修正前red/二Main PG/同oracle green、既認証/session domainの自己fixture PT・同source四counter/静的/必要全体を結合する。実DB原本/Root/VM/cohort/credential/permit等の操作を行わず、その保留解除や拒否PT代替の証拠にしない。既wholeや別sourceのPASS/coverageを算術合成しない。PT-AUTH-GRAPH328001..003/PT-SESSION-GRAPH328001..003。

SSC327/PT-OPS-WEBOWN327001～007：自己所有temporary PostgreSQL（既production Flyway）、loopback ephemeral Artemis/HTTP、synthetic credential set/Ready、TempDirのrootだけでWebNativeRuntimeの実start/healthy/ready/closeを検証する。固定経路のdefault bindingは別にsource/JVMと独立literalで照合し、実Root/auth/署名をfixture成功へ置換しない。通常起動のRoot Ready callback一回・borrowed credentials不消費・同32routes、未完startup/verify失敗/false/null・重複start/close、五handle公開と終了後未ready、private ownerLockのstart/close競合を制御latch/有限deadlineで確認する。Reflection/private field書換え、実メモリ枯渇、実Root/cohort/Unit/VM/permit操作を用いない。null port/設定/collection要素と固定native path/port key拒否をnegative testし、cleanupは自己所有資源だけを確実に回収する。直接I/O portは全callbackを取得前に完成させ、即時owner field格納と検証前後・管理owner捕捉後promoteを当JVMで照合する。実行PT/静的順序/未実施nativeを分離し、当sourceの必要全体/実counter/静的/CHR/451は別条件、IT/ST完了を宣言しない。

SSC326（2026-10-21、PT-OPS-COMPLETION326001/BUG1581/YKT1320）：自己所有のpure Java CompletionProgress clock/sinkだけでIO/Runtime/Error主障害×sink/clockのRuntime/Errorを独立fixtureで与え、failure通知が外へ二次障害をthrowせず元catchのretainへ進めることを確認する。正常固定literal/主障害秘密不出力/null拒否とphase診断の元失敗伝播は非回帰。失敗/未実行を合格へ含めずred→一Main PG→固定oracle green、同source JVMのfailure保護域・completion catchのfailure→retain順序、必要静的/全体を確認する。実Root/DB/Unit/VM/intent/permit/cohort操作は不要で、拒否PT代替や実native証拠にしない。

SSC325（EXEC325001、BUG1578/YKT1320）：Web借用frameのdummy close IO/RTE/Errorと診断通常/RTE/Errorを自己所有最小child JVMだけで組合せ、start/await/stop/close各一回・再close0・非復帰・外側finally0を通常間隔及び割込後に確認する。失敗前反例・同一oracleのPG後検証、既正常/null/start-await例外の関連PT・必要同source全体・取得前policy/JVM到達性fenceを照合する。実Web/Root/DB/VM操作や拒否境界探索ではなく、dummy daemonの終了を実native解放・全coverageへ加算しない。

SSC324（START324001/002、BUG1574/YKT1329）：Web startup cleanupを外部接続無しの自己所有dummy資源/最小child JVMで独立検証する。正常はReplay→replies各一回、Replay無しはreplies一回、null boundaryを拒否する。checked/RTE/Error及び同一startup ThrowableのReplay close失敗では後続close0/外側finally0/非復帰/再close0、Replay正常→replies失敗でも非復帰・外側finally0を、正常保持間隔と割込後で明示counter/frameから観測する。失敗前sourceで反例を保存し、同oracleをPG後に再実行、関連component実HTTP/JMS/worker試験と必要同source全体を行う。fixture終了はdummy daemonのみの終了であり実native owner解放成功へ加算しない。PG強化レビュー/静的と実PT/coverageは区別し、旧UNKNOWN/拒否対象保留は維持する。

SSC323（2026-10-21、PT-IDEM-GRAPH323001/002・BUG1573/YKT1328）：Web Outbox linked/next Error、cause/suppressed循環とError無し/null provider edgeを固定fixtureで検証。自己所有replay workerがfatalでterminal/非running・completed/failedCycle0、普通cycleではfailedCycle増加/非terminalであること、既temporary DBのfatal未mark/PENDING/attempt0/元leaseと普通ERROR/next時刻を独立oracleとする。APIの追加normal provider-null Testは既red期待を変更しない。旧source/未到達を成功へ加算せず、二Web MainPG・同oracle green/当原資格/全graph分岐/必要同source品質を要求する。一般session契約・実Root/current/cohort/native/拒否対象保留は別範囲として保持する。

SSC322（2026-10-21、PT-IDEM-GRAPH322001/002・BUG1572/YKT1328）：ordinary Outboxのcause/suppressed/JMS linked/SQL nextと循環/重複graphを固定Throwableで作り、Errorを同一fatalとして伝播し普通markFailure/次周期retryを行わないことを確認する。自己所有workerの一回open/固定診断/healthy false/終了と、既temporary DBのclaim後PENDING・attempt0/未mark/lease不変を独立後条件とする。Error無しのcyclic graphは有限帰還し従来の普通retry/ERROR・attempt/next時刻を維持する。二method内matrixをJUnit件数へ水増しせず、production graph methodをexpected生成に使用しない。元4043成功を本未試験条件へ移植せず、red→PG→同oracle green/全edge分岐/同source静的・必要品質を確認。実VM/current/Root/cohort/nativeと拒否PT保留を解除しない。

SSC321（2026-10-21、PT-IDEM-WEB321001～003/BUG1569/1570・YKT1323/1326）：Web通常requestとdurable log送信をsynthetic SS固定wire/認証済WLG fixture・未接続JMS proxyで検査する。非fatal Runtime/JMS/typed primary×close Error、元Error×close正常/別Error/同一Error、同一Runtime、primary無しのclose失敗を独立matrixとする。期待は元Error又はnonfatal上のcleanup Errorの同一性、異なる失敗だけsuppressed/self-suppression0、one-close、mode失敗時stage/commit/rollback0、stage failure時の既rollback、正常bodyの既property/body/commitとplain wire wipe。独立byte golden/固定Throwableを使用し、production methodからexpectedを作らない。matrixをJUnit数へ水増しせず、既API SS320/別source成功をWebの成功へ移植しない。red原結果→PG→同一oracle green、既real broker/DB正常・duplicate graph/再送・型null/静的/必要同source品質/actualcounterを確認。実Root/VM/current/cohort/native/PTALT保留は解除しない。

SSC320（2026-10-21、PT-IDEM-FAIL320/BUG1566/1567・YKT1323/1324）：ordinary API OutboxのJMS primary無し/typed/Runtime/Errorとclose SQL適用外/Runtime/Error、JDBC setup SQL/Runtime/Errorとclose正常/SQL/Runtime/Error/同一Throwable、rollback二次失敗を自己所有・未接続proxyで独立matrix確認する。期待は元Error保持、nonfatal primary＋cleanup ErrorはそのError保持、同一Throwable self-suppression0、close一回・未返却setup失敗ではclaim/commit/rollback/JMS0。既public型/固定診断・正常実DB/JMS/短TX・lease時刻・duplicate因果graphは非回帰。matrix入力をJUnit数へ水増しせず、未実行/失敗と元成功sourceを分離する。既whole6244のsource固定/原XML/Jar回収後に新実装/独立PTを進め、同source型null/静的/必要回帰/coverage・横展開を確認する。実Root/current/未知cohort/native動的PTの代わりにはならず、安全HOLDを解除しない。

## SSC319 callbackの確認済rollback境界

追加：rollback自体のRuntimeException/Error・試行前通知/正常後通知の順序とnull/例外を検査する。direct-processing Errorの一回rollbackと、既rollbackがErrorで不確定になった時の再発行0を分け、元Error identityを保つ。preflight/前配送/別contextの確認を流用しない。未実装red/失敗/未実行の入力は合格へ算入しない。

三consumerと実listener/二delegating wrapperについて、null・session mode preflightのRTE/不正・正常rollback/不確定rollback・directError・fatal通知例外、配送間reset、Sync四contextの分離、停止後callback拒否を独立入力/回数/状態で検査する。public互換entryの元例外identity/checked契約・既ACK/commit/rollback/DLQ/再送上限の非回帰も確認する。確認通知前の例外を通常retryへ混ぜず、通知は同context正常rollback後だけ、別thread/非同期で成功状態を書かない。単体proxyの成功を実Root/VM/current/cohort/nativeの実績へ合算しない。BUG1565/YKT1322/SS321342/SSC319。

## SSC318 UNKNOWN診断/tickの故障

取得前getter/class初期化と実factoryの順序を当JVMで照合する。tick故障後の再観測は独立nanoTimeで1000ms以上を検証し、IRQ/park早期帰還も含める。fallback自体のRTE/Errorでも外側markerなしを自己所有有限childで確認し、fault portは取得前に構成する。実JVMのOOM/クラッシュ等を故意に起こす試験や実Root操作へ拡大しない。

BUG1563/YKT1320/SS342343。自己所有有限childで固定診断RTE/Error・観測tickRTE/Errorを注入し、元release失敗後の同frame持続、close再試行なし、外側markerなし・IRQ/通常保持を独立確認する。診断不能時は期待stderr無しを明示して全EOFを検査し、任意診断の読み飛ばしにしない。子の143/有限観測を実Root/native成功に算入せず、process/VM停止とpersistent tick障害の残存リスクを保持する。

## SSC317 未start JDK管理HTTPの反例と保持

BUG1560/YKT1317/SS342。未start bind及び設定各位置のRuntimeException/Errorについて、stop正常返却を成功とせず固定UNCONFIRMED・native外側frame未解放/二重closeなしを自己所有有限childで独立検査する。子143/未測定を実native資格へ加算しない。正常start済みのHTTP DOWN/UP/DOWN・実executor終端・同port再bind・既例外/並行/budgetを維持する。vendor未起動時の完全解放は未保証の残存リスクとして記録し、解放成功の期待へ書き換えない。未受入code/全体品質は設計公開と区別する。

## SSC316 native保持接続の独立component PT（S3b）

三consumer/API親/broker/API-Web providerのnative entryの正常終了、partial startup/close Runtime/ErrorのUNKNOWN保持、API管理bind捕捉後start失敗・重複/停止後start拒否、inner roots/codecs/outboxから外側への解放順序を独立literal/実counter/JVMで照合する。normal componentの元例外順位/close再確認/TWR期待値は維持する。全callback/release portが各取得前に準備されることを実ClassFileと独立source fixtureで確認する。

保持の動的PTはJMS proxy/未接続locator/ephemeral HTTPと、当testが起動・所有する自己所有JVM childのみ。固定UNKNOWN診断/未帰還/外側finally marker不在、明示preinterrupt後も保有を有限観測し、そのchildだけ有限手順で終了・回収する。捕捉Mainの実agent記録を同sourceへ接続し、子143を正常cleanup/Root/DONE/実VM資格に算入しない。legacy正常/境界/null/異常/例外/並行/再送と六format型null静的・実四counter/必要全体を確認し、未測定を補完しない。現元1955終端までMain/Test固定、拒否対象probe/拒否操作再試行0・PTALT対象不明保持、実VM/current/DB/failed-cohort/intent/permit安全HOLD不変更。

## SSC315 API factory内部所有の独立PT（S3a）

三profileの12設定はSS321 literalから独立goldenで検証する。自己所有未接続factory fixtureの各setter全12・IAE/ISE/NPE/Error、取得失敗/null、close複合/同一Throwable/一度close/成功live/credential-freeを検証し、実VM/broker/context/原本DB/鍵へ接続しない。broker親は三取得の各失敗/null・全成功と逆順close/元primary同一性・個別secondary/未取得close0を確認し、actual JVMで全state/capacity/phaseが最初のfactory前、最後取得後のfinal格納だけと照合する。

既Testの期待値をproductionから生成せず、既partial primary順位をprovider設定の順位へ一括変更しない。新source影響PT/六format型nullSpotBugs/原XML/六Jar/全物理/当四counter・必要全体を関連変更群で確認する。native UNKNOWN保持・実親/CHR/451は別依存として未完、拒否PTを試し直す目的ではない。BUG1553/YKT1307/SSC315、S2実行source固定中はMain/Test変更禁止。
## SSC314 API JMS close所有の独立PT（S2）

PT-API-JMS-CLOSE001..006/1297は自己所有JMS proxyと有限latch/Threadのみで、三consumer/親group/brokerのfirst close Runtime/Error、確認済み子の再発行0、未知子の再確認・全成功後冪等、停止後DOWN/escaped supplier非受理・新callback処理0、並行closeの二重発行0、startup/fatal優先・nullを検証する。期待値は独立literal child別回数/順序/同一例外と実Thread終端。既「失敗後二度目正常no-op」oracleはSS342SSC158に反し、当反例・SSC314を根拠に補正し履歴を保持する。

当sourceの全既関連API Test/六format型nullSpotBugs・全原XML/Jar/物理差/当実四counterを確認し、未達を補完しない。変更群をまとめて必要fresh全体・static理由/traceを認証し、旧source成功を加算しない。実VM/current/DB/鍵/Root/Unit/failed-cohort/intent/permit操作0、拒否対象probe0、PTALT代替数0。BUG1548/YKT1307、fixture finally改善BUG1549/YKT1308は次の関連影響PTへ同梱し独立して記録する。

## SSC313 API管理HTTPの停止PT（S1）

PT-API-STOP001..004は自己所有loopback HttpServerと独立fault wrapper/有限latchだけで、stop Runtime/Error後の再close（同一例外/stop再試行）、stop成功後のexecutor未終端/0budget・再join（stop二重発行0）、lock待ち/待ち中割込、executor待ち割込のflag復元、既preinterrupt成功/既冪等、null/負/30秒超の未操作を確認する。期待値はSS342SSC313の状態/回数/actual thread terminalから独立literalで定める。故障は修正前915へ登録してから旧codeのstop再試行反例を実行し、fixture自身はfinallyで実server/workerを必ず終了させる。

対象ApiManagementServer close/promote/ready/constructorの全四counter100・全分岐と全既管理HTTP Test、六format型nullSpotBugs・原XML/source/Jar/全物理差・無除外静的を確認する。S1局所PTとS2/S3の親resource保持・native/Root/CHR/同source全体を分離し、旧3988結果を変更後sourceへ合算しない。実VM/既サービス/intent/permit/failed-cohortへは操作しない。関連1294/PG-D462/BUG1547/YKT1307。

## SSC312 HTTP取得前準備の独立PT

SS313/342のowner準備を対象とし、PT-HTTP-OWN001(API management)/002(Web management)/003(Web HTTP)でfactory一度・固定127.0.0.1/backlog32・取得IOException/IAE/ISE/NPE/Errorの同一性・null拒否・未取得のclose/owner通知0を独立fixtureで確認する。Tomcat supplierはchecked IOException非適用。既正常HTTP/拒否URL/情報5値/interrupt/失敗close再試行/所有callbackの全影響PTを併せて実施する。テスト自身が取得した実server/fixtureはfinallyで解放する。

未保護allocation失敗は故意のOOMで再現せず、実compiled constructorの全field初期化とexecutor/MVC/lock/address allocationがfactory前、取得後はnonnull/final格納/returnだけであることを独立JVM命令解析で反証点検する。全原XML・同source/全Main物理差・public ABI・実四counter・無除外静的を照合する。未到達branchや未測定nativeをPASS/100へ補完せず、新source全体は必要な変更群をまとめて真正結果を確認する。BUG1545/YKT1305、仕様1286/PG-D461、旧source成功の移植0。

## SSC311 Web factory設定・完成ownerの独立検証

SS321/343SSC311・BUG1537/YKT1297。MQFACT311001は既endpoint/設定12値/user-password未設定の独立literalを保持し、public createで全supplier/owner/lock準備→factory取得/設定→final格納だけのactual bytecodeを確認する。MQFACT311002はfresh factoryの各12setterでIAE/ISE/NPE/Errorを注入し、setter prefix/一度close・正常時close0でlive返却/取得失敗・nullで未取得close0を検証する。MQFACT311003はprimary/closeのRuntime各種/Error/同一Throwableを独立表で与え、通常は同一primary＋secondary一回、close Error＋primary非Errorだけ同close Error＋primary一回、同一Throwable self-suppression無しを確認する。ExpectedをProduction merger/helperから作らない。

fixtureのfactoryは自己所有・接続/consumer未開始、test専用解除で最終解放を確認し実broker/VM/current/鍵/原本へ接続しない。実heap枯渇を誘発せずJVM順序はPG静的証拠としてPT PASS/実測coverageと分離する。正常Web/既consumer全close/既live close retry・秘匿・password copy破棄/借用constructorのcaller所有を回帰し、四counter/型null/全物理/公開ABI/無除外解析・必要同source全体/native/CHR/451/正式を別資格する。失敗/未実行/別sourceを合格へ加算しない。

## SSC310 Expiry read局所の独立JDBC複合故障

SS331SSC200/332SSC063199310・343SSC304境界、BUG1530/YKT1290。EXP310001は未修正readに対しResultSet.nextの独立Error primary＋ResultSet.closeの独立SQL secondaryを与え、同一primary＋新固定BatchRepositoryException suppressed一件・逆順一度closeを期待する。SQL closeが元Errorを置換して固定例外となれば不合格。EXP310002はread二scopeの独立68合成表（SQL/IAE/ISE/NPE/Errorの全25対×二scope、同一Throwable×四×二、成功body/close故障×五×二）で同一性/固定秘匿/一度closeを確認する。68はJUnit case内数であり追加68PTとは計上しない。ExpectedはProduction merger/helperを呼ばない固定表で作る。

EXP310003は正常empty/完全Snapshot、null資源/必須列・不正投影/取得失敗/各getter未知/成功close障害、借用Connection変更禁止・guard順を確認する。既BAT287のreadRuntimeだけ未知provider同一性へ補正し、stageRuntime/finishRuntimeの既別scope期待・SQL/null/不正DB値の固定拒否は維持する。既実PostgreSQL Expiry stage/finish/idempotency/保持別run SUCCESS/rollback・監査不変とcaller影響suiteも新sourceで照合する。SS343SSC304のJavaTWR参照試験を保持して混同を防ぐ。line/method/class/branch100%を要求し、pure proxy限定結果を実DB/Root所有/native/旧source coverageへ転用しない。必要同source全体/CHR/451/正式受入は別終了依存のまま。

## SSC308 factory-owned IO例外matrix・wrapper取得順の独立PT

FFM返却先補足（SS343）：初回native前の三私有out slot/primitive状態・Arena完成handoff、全引数準備→PENDING→C呼出→正常復帰直後RETURNEDの順をactual bytecodeで照合する。全四返却scope、bus取得、request/reply/string/arrayのNULL/負/未知型、各C callのIO/Runtime/Error、返却slotへpointerを書いてから例外を投げる故障、decode故障、close例外/不正戻りを独立に確認する。未知返却が0扱い/free成功に変換されないこと、既知request cleanupの旧順・一度試行、UNKNOWNのslot/arena保持・次read0、正常時の三slot再用/arena閉鎖を固定call列・外側owner/状態・literal値から検証する。期待をproduction mergerから作らず、旧literal ABI/期限/owner再読/八targetを当source再検証する。原237内四siteと原外constructor/bus取得補足を別に記録、限定PT/全体/native/451の成功を合算しない。

完成owner handoff補足（2026-10-19、SS333343）：全port null/構築Errorが取得前、factory IO/Runtime/Error/null時の組立/解放0、完成nonnull ownerの同一identity/責任移管・補助側close0、組立IO/Runtime/Error/null時の同一R一次解放と既複合優先/秘匿・既suppressed/同一object、独立並行ownerを固定oracleで確認する。期待値をacquire/handoff/旧useから生成しない。取得前の状態/callback確保、完成nonnull後のprimitive移管→即return、失敗時のみ事前release、全旧acquire/use opcode/handler不変を実Java25 bytecodeと当source全storage四100で確認する。factory内部の各wrapper境界、原use237外の直接open/TWR/手動tryは追加母数・失敗例外/close優先も独立比較し、wrapper検索・限定成功・実OOM未再現を全体/native完了にしない。

StartupAdmissionFile primitive ViewOwner補足：N+3予定容量（root/runtime/app/entry）、FD319以上、負FD、duplicate既保持FD、満杯/closedの取得前拒否、各openのIO/Runtime/Errorと未登録FD無し、host/private同一性・exec前service→host消費を独立に検証する。逆順3FDのclose正常/IO/Runtime/Errorの64組を固定goldenのprimary型/identity/Reason/秘匿suppressed数・全FD試行順/回数で照合し、複合故障でも途中drainを省略しない。既suppressed/同一例外/idempotent/独立ownerも含め、expectedにproduction merger/useを使わない。全wrapper/scratch/portが初回native前、容量checkが各open前、有効FD後primitiveのみ、drain中callback/new/suppressed操作0を実Java25 bytecodeで証明する。実heapOOME/本物authority/未知close成功を捏造せず、新sourceの限定PT・全体/native/451とYKT全体は別受入のまま。

2026-10-18限定資格更新：source1c45f4ec6の537PT/73suite・六format先行0/三compile static0、共通storage四counter全miss0、immutable release16scopeは全port取得前構築とfactory直返却を実bytecodeで確認（1055/1056、PG5170 f97a2352・公開0769e9ea）。直前Source50bcのreadonly agent metadata新1を同大選択へ含め、checkedは15行/1method/36branch全miss0、NativeCoveragePrivateFile全classのbranch150/150を実測した。ただし同classの29行/12methodは未実行で四100ではなく、全new source/native/CHR/451は別受入。原237候補は52限定是正/1借用非該当/184未判定、追加prebuilt release1の非該当根拠も保存し、全体YKTを閉じない。既全体/別source/別scopeのcoverageや成功を合算しない。

native横展開PT補足：FileLock/SealedProofの有効primitive取得直後wrapper格納/返却、負値・dup自己同一・close一度/未知/compoundを独立literal/identityとJava25で検査する。Startup二owner集合はP→A、proof早期close後の集合closeはAだけ、並行早期消費・全IO/unknown/compound・未adoptのinput拒否close0を独立確認し、port全構築がadopt前であることを実bytecodeで証明する。既storage全suite/全四counter/静的と必要全体/nativeを別受入、実heapOOMEや未実行成功を捏造しない（003020、WBS-P003-06、群1186開始費固定）。

限定検証追補（2026-10-18）：source6d7a54a01・独立新16を含む222PT/32suite、全storage四counter1200行/269method/37class/537branch各miss0、六format/実compile三static0、取得直後保護域と旧use56opcode/handler同義の実bytecodeを確認（003016/017、PG5138 5ce05224・訂正公開e3024935）。Root11/共通Directory5だけの結果であり、残候補/新source全体/native/全正式品質は未完。失敗v1～v5/metadata384aは保持、既全体/旧nativeを転用しない。共通caller等の残候補は同規則と既独立oracleで個別修正又は非該当根拠・再発防止確認を続ける。

Root top補足：専用RootDescriptorの有効FD319（Integer cache範囲外）・負FD・open失敗・null callsと一度closeを独立literalで検証し、primitive保持で取得後boxing無しを実bytecodeで確認する。Root checkedにOwnedDirectory由来のIO Reason変換を加えず、同FD・同型・同一失敗と既close優先順位を保持する。fake DirectoryCallsが他native操作を呼ばれた場合はfailし、Root authority/本物起動の代用にしない。

SS333/343 SSC308。全port null/構築Errorがacquire前、factory IO/Runtime/Error/null時のbody/release0、正常nullable結果と同一resource一度close、body/close全IO reason・unknown型・同一object・既suppressedの独立matrixを固定literal順序/identity/秘匿messageで検証する。期待値を製造use/acquireで生成せず、SS333表のルールを直接assertする。既ResourceScope全PT・全Directory能力PTを同source再実行し、公開API既正常/境界/失敗/NOFOLLOW/transfer/close/並行の契約を保持。wrapper/stateLock/EntryHandle確保がnativeopen前、取得直後保護域前にnew/invokedynamic/boxing無しをJava25実bytecodeで確認し、実OOME発生や任意native成功を捏造しない。Root固定metadata/pin/世代/owner/期限/借用能力と新source実経路は別に資格、68file237siteの残判定と追加予防testまでYKT未完。旧成功/別sourcecounterの合算/coverage除外/安易なsuppressionは禁止。

## SSC307 Root待機の順序・期限・MISSING限定と割込み独立PT

SS343 SSC307、RootStartupPending。独立literal時刻/clock-owner-read-pauseの順序列を用い、API/WEB即成功、missing→成功、繰返しmissing→元期限、期限直前/同値/超過、後段owner/clock/自己世代拒否、観測IO/Runtime/Errorのidentity、null、割込み再設定/固定message/cause無しを確認する。sleep実時間を待って期待値を作らず、portの記録列・呼出回数・不実行をassertする。LaunchReadはMISSINGだけempty、他Reason/一般IO/Runtime/Errorは同一object、null port/recordは失敗を確認、nativeのstart-intent前提と同Scope内catch位置を維持する。fake成功は本物Root/Unit/権限/DB成功へ加算しない。既自己世代/StartupLaunchFiles・Root ELFと当新PTを同source選択し、六format先行・実compile三module static・元a2eccから累積予定Main byte差を照合する。変更群後のfreshwhole/当source native・四100/全正式は別受入。

## SSC306 Root ELF provider失敗・read-count同値の独立PT

SS343 SSC306。default SHA256/固定64byteELF caa6f4f5…fe8は元期待値のまま、package内factory faultでNoSuch→固定IO/no cause/no inputread、未知Runtime/Error同一identity、null/欠落はI/O前拒否を確認する。global Security providerを変更せず、Reflection/private呼出しや架空coverage除外を使わない。n>0・n==positionの同値整理は過大申告8193/position8192・負/零/count違い/EOF-position/size違い/上限正当値・超過を独立fixtureで確認し、拒否を弱めない。借用channelをdigestがcloseしない/呼出側ResourceScopeが同一資源を回収/作業buffer wipeの正常・例外を検証する。新source選択PT/静的/byte差を限定資格し、旧3791/10nativeを新source合格へ合算せず、必要変更群が揃ったfresh全体/同source実経路/四100・F03/正式は別に閉鎖する。

## SSC305 親start/endの独立比較と当保持pairの否定試験

実績追補2026-10-18：5102 end/start/旧end/null/bool/foreign/欠落の独立負例＋完全graph5件、5108全関数/三前像/実終端前提3件、5116全1650/two-pair/public4件が成功。5098/5096/5100の全原値/所有/各一回TERM/元143UNKNOWN/別post、是正5104五ABI・5106三phase・5108captured20/1.77017秒・5112 CRC/session/二単調・5114公開が全actual0。失敗byte/slot/中間fixture失敗も保存し、元3791/署名/Root/完了ABI再演0。dev-foundation9ce065ff7/1042・1043で追跡し、この限定是正の完了を四coverage全100/F03/CHR/正式/ITSTへ拡大しない。

SS343/353 SSC305、BUG1405/YKT1169。真正receiptのstart306951851178us/end308517705767usを独立oracleとし、終了比較へstart/旧end/null/foreignrunを入れた反例を拒否する。元3791/独立資格は再利用して検査目的で再実行せず、工具の全出力/parent receipt全byte・新release/BOM/namespaceだけを束縛する。現在pairのargv/exe/authority/cgroup/全task/全FD/同inode-OFD/子bus/SQL0・全原値を二読し、共有/run二時刻の合法単調変化と不一致を分ける。foreign generation/第三子/別FD/誤bus/DBpeerあり/不正proof/既予約/TERM直前変化ではsignal0、一回子→親/各15秒/30秒reap・全資源0・旧closeUNKNOWN/元exit維持と独立別postを検証する。正常fixtureを実権限にせず、各実操作は当現在値/耐久proofで資格する。旧source nativeを加算せず四100/F03/CHR/正式/ITSTは未完とする。

## SSC-285：署名拒否前39FDと最終emit閉包

QA047/BUG1305/YKT1071：最終Java/Python/fixture実出力のboot/source/BOM/signature stem/全Rootbindingを独立oracleで確認する。composer本文だけの成功・同じ旧値を持つfixtureの相互一致を資格にせず、旧b2d6/pg2654・未知/欠落/null/余剰/誤署名をM/A/DB/Ref取得前に拒否する。正常ABI/署名/実scopeに加え、この署名拒否がDB/Ref/サービス停止へ進まないことを独立に確認する。

回収PTは343の0～36/43/128閉集合39FD・全target/全9metadata/flags/linked path/ACL/OFD・子0/DB0/唯一M-Aと当host solegateを具体的fixtureにする。29/32共有/runの二時刻非減少だけを旧→freshへ限定し、逆行/上限超/他FD変異/未知socket/新child/DB・peer不整合を拒否する。fresh二読/耐久保存/各pidfdとTERM直前再照合・一回予約/15秒終端30秒reap・queued同inode取得の順序を正常/拒否/中断で確認、signal未発行の拒否と発行後未回収を分離する。

実後条件はJava/全FD/管理DB-advisory-MA/bus0・四ordinary/全TCP/全24/設定32/状態18/187/原本Backup/runtime/startup/native保持・新Ref正常返却・別wholepost。旧UNKNOWN/143を正常closeへ合算0。既に成立した当source親DONE10/全24/A01は再演せず証跡参照、未実施の正常ownedstop/nativeだけを新only版で閉じる。PG/PT結果をIT/ST完了にしない。

## SSC-284（PG/PT、2026-10-14、reload済み保持11FD・shared/runと宣言viewの具体化）

実最終283をlocal及びorigin/mainで確認。BUG1232～1235/YKT998～1001/QA047既承認内、RD/UI・業務結果・Root1800秒/Unit期限不変更、新QA不要。current Main3b7f/PG2126/BOM62213f・bootb2d6の当管理Java101019/t1808679/101FD、唯一Ref101050/t1808864/11FD、sole管理DB101048/PG998-native-stage/idle-TX/71419602、親M-A/同peer双方向TCPを新fullproofへ束縛する。sudo101017/他actor/業務Unitはsignal対象外。独立2342 proof a8eb610cff840dc9be93eb83f59d369097ec145d743c92e62d1e5344a41147ff、全24row/187/原本Backup/native/状態18/署名decl tripleを保持、partial runtime inode4223/4224・644bytes/SHA888ee856を全9metadataとACL/linked path/readonly flagsで照合。旧2332のUNKNOWN/143を成功に補記しない。

子FD0/1は親の対応pipe、2は固定refs log、3は当private systembus、4=/、5=/run、6=/run/systemd、7=/run/systemd/system、8=固定Morning Unit.d、9=同一zz-pg2316-once-resume.conf、10=当private SAVE。全11閉集合・Root権限/cap/cgroup/全task子0/唯一bus名とargv hashを二読する。4～10のO_RDONLY/O_NOFOLLOW/O_CLOEXEC及びdirectory flags、fd9 regular Root0644/nlink1/既byte・hashを検査、別FD/新file/未知差を拒否する。親31/90と子5は同じlinked /runの元dev/inode/type/Root owner/mode/nlink/size/ACLを持つ。過去proofからfreshへの差はこの三FDのmtime/ctimeだけ、旧時刻≦現在時刻≦当fresh測定上限として別保存し、子5のfresh全9値は親31/90と一致必須。他親99FD/子10FDは全9値・target・authority/bus/socket一致、時刻を0化・無視しない。

新only同一接続/十Refの中で全元像・全pair/DB/socket/OFDを二読→独立fresh proofを耐久保存→各pidfd前後・耐久一回予約・TERM直前にそのfresh像を完全再照合する。Refだけ普通TERM一回/15秒終端・30秒同ticksreap→bus消失/親全task子0/失ってよいFDは当子stdin/out pipeだけ→親だけ普通TERM一回/同有限reap→旧actor/全FD/DB/advisory/M-A/bus0・全元像二読・新scope正常→別全post。SIGKILL/DBterminate/他PID/旧toolhotpatch/VMboot/原本補修/permit-epoch変更0。未知は隔離、同signal/reloadを再送しない。

systemdの状態18と設定32を混同しない。partial file後のGC/LoadUnitでMorningのExecStart/DropInPathsが固定元UUID二引数/固定一fileを反映する場合、その既知deltaと全残30値を独立に検査する。正規daemon-reloadでは他UnitのExecStart宣言tripleは同値を維持し、末尾五実行metadataだけがexact CLOSED(n/a,n/a,0,(null),0/0)へ戻り得る。実状態18/Job/PID/invocation/bootと全他config・fileは不変更、余剰argv/unknown/状態変更を拒否する。このviewだけから正常reload・旧scopeclose・起動資格を推測しない。

旧同inodefragmentを再write/削除/再配置しない。署名済み20工具・reservation/logのbyte、固定helperのcontrol-flow（reload return/empty stdout-stderr/verifyの後でpost guardが拒否）、独立PID1/readbackの宣言/状態を相互照合して既一回reloadの実施を分類する。old closeはUNKNOWNのまま、正規owned回収/別全post後に、新M-A/実専用DB/十Refのverification-only scopeで元原本/全24/宣言32/187/partial inode/currentを正常照合し全scopeを正常返却する。さらに別独立postで全資源0・fixed effective --resumeを閉じてからだけ、別observer/一回durable予約/明示resumeを開始できる。verification-onlyでreloadや業務startを追加しない。旧entryをactual0へ書換えない。

PT工具のmkdir時刻にはLinux filesystemのcoarse clockが使われる場合がある。有限操作の下限は操作前に独立採取したkernel realtime-coarseと高精度realtimeの関係/分解能を検査し、既mtime/ctimeからの非減少・現在上限/全identity/content/唯一namespace deltaを維持する。壁時計を変更せずRoot cutoff・epoch・budget精度を緩めない。既partial原本に未採取の時刻を後付けしない。独立過去/未来/範囲逆転/型/null/unknown差の反例、全11FDとCLOSED宣言の再発防止PT、実正規回収/verification/newresume/各postが未完。設計公開はこれらやcoverage/PGPT完了の認定ではない。
SSC277：当Bootstrap31/90の共有/run同linked像と全他97FDを独立fixtureに固定し、旧29/32/別target/一方のみ差/chrono逆行未来/extra-missing/型不正を拒否する。hostqueueは正常引継ぎ/失敗保持を別oracleで確認し、元guest拒否を合格又は二次待機エラーへ置換0。全元値/DB0/一回TERM/有限reap/別wholepostはSSC276を維持、旧1724失敗の再送0。

SSC276（SS343/BUG1156/YKT924）：current99FD/子0/全原値・serverpeer/advisory0・socket0/soleM-A/OFDを独立証明し、旧livepeer仮定失敗を成功化しない。hostgate旧owner/foreign/reuse/競合と引継ぎ期限、全fresh像のpidfd/予約/TERM前差、FD余剰欠落/role/Source/null/bool/共有祖先chronoを各拒否する。普通TERM一回/有限reap/旧UNKNOWN保存・別全post資源0を実証。actual Expected constructorの正規3/4桁、suffix1/32境界、非numeric/桁過不足/空/null、role/database/readOnly/advisory全契約を独立Javafixtureで取得前検査し、現label拒否時のロック/DB/Ref/Unit callback0を確認する。正常new-onlyverify/existingADMINexecute/全postと同source nativeを別資格、正式/CHR/ITST合格へ自動加算0。


SSC275（SS343/BUG1152/YKT920）：旧実payload/tracebackのreserve→before_parent例外→send未到達を独立照合し、予約だけをsignal receiptにしない。旧101から当childpipe100/101だけ消失、現99全field/argv/ticks/権限/子0・soleDBpeer/MA/原本nativeを再認証、/run29/32以外の差を拒否。newhostcritical排他gateは同scope別管理接続の二重取得を拒否、同job付着だけ許す独立反例を追加。sameconnectionfresh99の各段階race/extraFD/peer/新子/未知/null/bool/時刻不整合を拒否、実新一回TERM15秒終端30秒reap/別全post/全元値と資源0を確認。旧slot再送/失敗成功化/coverage除外/人工到達0、正式/CHR/ITST受入は別。

SSC274（SS343/BUG1150/YKT918）：独立固定101FD親/4FDRef/soleDBpeer/全24-32-187/current原値proof、sameconnection fresh全像/耐久保存signals0を実証する。PID/ticks/argv/exe/UIDcap/cgroup/子集合/FD欠落余剰/再利用/ACL/OFD/foreignpeer・role/app/backendStart/双方向socket/advisory/busname/十kernel/原値差/旧noDBproofを各拒否。/runFD29/32二時刻だけ合法進行と全他field不変、fresh二読及びpidfd前後/予約/TERM前の単独変化は拒否する。子TERM後の当stdin/stdoutpipe消失以外のFD差・新子・bus残存を拒否、各一回TERM15秒終端30秒reap/別全post全資源0を独立検査し、旧143/UNKNOWN保持を確認する。次工具の依存閉包はarchive実basename/suffix/hash、bundle/署名、全helper/class/transitive importの欠落/余剰/foreign/null/bool/pathescape/hash差を取得前に拒否し、新only compile/stage/placeの実再試験で閉じる。形式coverage/CHR/工程/ITST受入へ合算0。

SSC273（SS343/BUG1149/YKT917）：FD29/32 target/runの過去時刻とfresh二時刻を別fixtureにし、合法非減少でもfresh二読/予約/TERM前後が変わればsignal0を検査する。dev/inode/owner/mode/link/size/type/ACL/linkedpath/namespace、95他FD/97set、argv/cap/cgroup/nochild/source/class、M3FD/AdupOFD/kcmp、DB/原本/全32config/187/native14/十kernelの各単独差・欠落/余剰/foreign/null/bool/未知/未来時刻/clock後退を拒否する。new-only同一管理接続・新Ref保持→完全独立fresh proof/耐久保存→pidfd前後/一回予約/TERM直前の同fresh像→15秒終端30秒reap/全後条件を実証する。旧143UNKNOWN/旧proof/時刻を保持し、一般緩和・人工到達・Production期待値変更0、正式/四100/CHR/ITSTへ合算0。

SSC272（SS343/BUG1146・1147/YKT914・915）：当289328/ticks5627480/Source4d6/PG1544/boot3d69の全argv/classpayload/RootUID/cap/cgroup/97FD・全taskchild0/二soleFLOCK・属性FD30/33/保持34/共有dup43-128を独立metadata/fdinfo/kcmpで確認する。欠落/余剰/foreign/PIDreuse/旧LABEL/Source/各identity四tuple不一致/別OFD/kcmp未提供・errno/負値/bool/null、DBclient/advisory非0/原本24DB・Backup/runtime/32config/187/native14・十kernel差は拒否。新Ref正常・完全proof二読→耐久一回予約/pidfd普通TERM→15秒終端/30秒有限reap→全旧97FD/M-A/actor0・DB0/全元値二読・新Ref正常を実証し、旧143/closeUNKNOWNを保持する。signal各fault/reuse/二重予約/unknownを成功化しない。別new-only四tuple修正/署名full187/unused配置・正常scopeを実再試験してから新source真正親/native/正式へ進む。工具試験をProduction coverage100又はIT/ST合格へ合算0。

SSC242/DEP864001..004（SS343）：fixed old832/2a/8bcb/861・old8bINVALID・完全DONE0/旧親9c08timeout143とunused signed862/e016/20b99dを独立before oracleへ結合し、genuine/pending/ISSUEDへ偽装せず全24/full32/tenRefs/実RODB生存・held FD/原本Backup/署名と個別mountROを検査する。別source/boot/parent/epoch/run/activation/欠落/unknown/既slot/未凍結・重複mount・foreign/malformed/rw、null/IO/Runtime/Error/DB喪失/期限・異thread・close不明/各有限公開段faultを拒否する。verifyの全非変異、activateの新UUIDv4INVALID同原本＋0400approval/current symlinkだけを独立raw/metadata/全24二読で照合し、最外scope通常返却・kernel/DB/advisory/M-A/Ref/bus/FD0で閉じる。既freeze/place/停止/失効/退役を二重発行0、旧parent143/RootDONE/旧nativeを新Source合格へ混入0。新genuine/CHR/global100/正式は別gate。

SSC240/RLOOK852001..005（SS343、BUG968/YKT737）：Productionと独立した固定anchor/begin/DONE bytes・historical SKIP時刻から、同Session pending参照→完全DONE/active退役→pending拒否→typedcompleted data-only参照を検査する。current SUCCESS/WARNINGの両正常、同run/別prior終了境界、observed未来/current cutoff/microsecond/上限/同JST日、unknown/別active/DONE tuple違い/全Graph二読競合/namespace/IO/Runtime/Error/異thread・失効・close/nullを検査する。current DONE終了<=historical SKIPを要求しない（時間の意味が異なる）。全元DB成功条件と同owner・budgetは維持し、原本/DB/permission書込0、独立例外identityとbyte/hash不変更をassertする。修正前は凍結2a/JAR/同sourceFixtureの実Sessionで旧拒否を再現する。新sourceの影響九suite/静的/所定全回帰→実真正親DONE_AFTER→ownedstop/nativeまで同source/run整合を維持、限定PTのみでglobal100/正式/ITST PASS0。

SSC241/REC856001..004（SS343、QA047、当DONE後failed親）：固定9c08 failed143/完全DONE/全intent無し/8b153538ISSUEDと現832署名を独立oracleへ束縛する。別親・旧PID再利用・generation/argv/cgroup/UID/cap変化・current/BOM/原本/全24/Backup/Unitconfig・DBserver喪失/Ref/FD/M-A/close不明の拒否、逆順ownedstop/native/vendor、十kernel終端→同epoch canonical INVALIDの順序を検査。Pair生成/intent退役/旧成功補完は0。全新scope通常帰還、独立24table全列・原本DONE/Backup/Transfer/credential/config/Unitbyte・資源0/元failed不変を実VMで確認してからruntime841退役へ進む。未実行を合格に加算0、当2a停止nativeは後続新source正式coverageへ流用しない。

## SSC239 fixed fresh system-manager readerの独立PT（2026-10-09）

SS343の固定full7/deadline4 fieldについて、公式systemd公開ABI/vtableから手書きinterface/type/byte oracleを作り、Productionからexpectedを生成しない。固定DBus request宛先/auto-start0/PID1/bus EUID0/unique owner前後、string NUL読取長/ASCII4096境界、uint32/64最大、Invocation長0/16/他長、NULL/欠落/未知field/型/異thread/interrupt/missing symbol/platform/library祖先uid-modeを検査する。native全呼出IO/Runtime/Error・取得途中fault・unref/arena close不明のcapability保持と次read拒否を独立stateful fixtureで確認する。

仮想元時計で接続認証/Hello待ち、連続複数RPC、引数準備後/timeout setter直後の期限切れを注入し、5秒全体・残1µs境界・次RPC0・期限renew0・通常closeと不明closeの区別を検証する。実259.5の同source未配備jarを停止中隔離VMでsystemctl before→native→systemctl afterへ比較し、固定全field/owner/回数/経過/FD/子processと全十Unit不変を記録する。property値やraw private credentialを公開logへ出さない。

各fieldの型と全分岐/例外/nullを451四counter100へ含める。固定security pathのEXACT理由付けをPT仕様と静的記録へ対応させ、coverage除外やanalysis全域抑制をしない。限定比較/少数PT/ホスト静的0から全体品質・旧timeout解決を逆算しない。新source所定全回帰/同source native・真正親DONE/owned停止、CHR/DIF/global/formalは別受入。IT/STの負荷中性能・本番Linux検証へ引き継ぎ、PG/PT結果でIT/ST合格を宣言しない。

SSC238/PT-OPS-DBLIVENESS797001～004：保持工具の同Connection/server現在所有を、固定backend/role/application/database/readOnly/advisoryと同threadへ束縛して確認する。正常wait/retainの各再確認、closed/null/異thread/各固定値差/SQL/Runtime/Errorを独立注入し、DB_NOT_CONFIRMEDへの一方向遷移・以降query/再取得0・正常close推定0を検査する。role60sを変更/解除せず、間隔内の長時間待機を実VMでread-onlyに確認、元parent1800sの変更も0。失敗scope隔離/正規handoffと新scope通常rollback/close/十Ref/FD/M-A/実DB/advisory0を別証跡で照合する。旧779143/喪失server0を新成功へ置換しない。工具試験はProduction PTへ加点0。

SSC237/PT-OPS-COMPLETION790001～004：実完了orchestrationのCaddy/Web/API各before/after、API-held、DONE前後を手書きliteral順序へ照合する。各境界のpeer/row/seal/receipt・close/元budget失効とIOException/Runtime/Error、nullを独立に拒否し、後続退役とDONEを発行0。同owner-threadとTX内純owner/TX外全evidenceを維持する。fixed phase/failure分類/経過だけの診断を、秘密を含む例外message/stack不出力の反例で確認する。初期重複fullの除去はCaddyの本来before/after gateが両方実到達する試験を伴う。BUG927の旧143は失敗保持、現停止query測定を原因/合格へ読み替えず、変更source fresh選択/静的0/所定全回帰/実親真正DONE・owned停止・当nativeと正式四100は別に実証する。

SSC236（2026-10-09）：343の現779保持toolだけ、PID/ticks/exe/argv/親子/同source hash・M/A実inode/OFD・十Ref/heldFD・serverbackend/advisory実0とobjectを独立照合する。全十kernel0/元42三intent/原本/全24-544/Backup/Transfer等二読→pidfd通常TERM各一回又は既終端skip→全旧子/FD/OFD/Ref/server消失・旧closeUNKNOWN維持→別freshDB/M-A/十Refで既INVALID既三intentだけtyped退役→39/全元値保持/新全scope通常返却を検査する。repeat callback二回/多回で診断書込0、最終一回receipt再作成拒否、各fault/foreign/PIDreuse/部分終端/close不明・readonlyheartbeat/同backend失活/未知を正常化しない観点を追加。schema/role timeoutを解除せず実60s lossを原因証拠へ残す。工具hostassertはProduction PTへ加点0、旧779/780/親143を新成功へ合算0。四counter100%/全scope同source/run/CHR/DIF/秘密trace・IT/ST別条件を維持。

SSC235（2026-10-09）：343のPG758現失敗profileを固定literal独立oracleで検査する。元143/RootDONE無し・同boot/Invocation/PID/ticks/security/launch/署名/full BOM、七現startup/41総集合、全24新現在原値/544/Backup/Transferと旧全私有証跡、連続M/A/専用DB/十Ref、逆順stopの予約前後・依存停止・各fault/foreign/第三child/PIDreuse/close不明・非秘密primary/secondary・隔離保持を対象とする。全十kernelとAPI/Web native・Broker vendor/PID1 witness後だけcanonical同epochrevoke/typedPair隔離退役、41→39/currentINVALID・他原byte不変・全新scope通常返却を独立照合する。途中760比較には当三table有限appendを明示し、停止区間は完全同一へ戻す。Requires/After順序非意味と他property順序意味、空ExecStop実PID1型認証、coldGC/十Ref取得解放の各例外をnegative試験する。旧773～776失敗と777readonly成功を別保存、工具assertはProduction PTへ加点0。正式四counter100%/同source/run/全scope・CHR/DIF/秘密trace条件不変更、IT/ST性能・本番自動復旧の合格を宣言しない。

SSC234（2026-10-09）PT追加：二role同期TERMINAL→callback/entry/診断帰還→CLOSING/marker→終了の独立literal順序、agent無しI/O0、null/foreign owner/先行closing/terminal失敗/重複/partial/metadata-session-byte/全close-postcheck失敗を検査する。same-main termination portでBootstrap0/20/50/70/診断順序を検査し、実Java25FQCN launch拒否/実VM既存20・正常原本資源後条件を別確認。採取点自身の末尾は同bodyport試験、私有reflection/人工authority/除外/連鎖dumpは禁止。当二rolecollectorはterminal→closing同source/frozenclass/単一session/actor/時刻順/無resetprobe単調・完了markerを必須としてlatest closingだけを採用する。欠落/partial/失敗からterminalへfallback/同session累積union0。Root/API/Web既採取・停止条件と451四100/独立oracle/全scope正式を維持する。設計公開は新sourcehost/native/正式の受入ではない。

SSC233（2026-10-09）PT追加：現completed21 seal/current36fe/PG631/601-ad15/正常STOP・664normal20/私有二input退役/全24-514を固定し、oldGC五項以外/他九Unit/設定/依存/18source/namespace/privateproof変異、原本未完/別run-cutoff-activation・owner/peer/DB/FLOCK違い、BOM/187/SQL/schema/同pin/全JAR差分違いを単独拒否する。新候補PG682source9bd/3489-516/static6zero/class1612(変更6/abstract7)から別newverify不変更・activate有限INVALIDepoch/Root0400approval/currentだけを許し、各前後関係/元raw保全・DB正常closeと0/Ref-bus-dirFD-A-M正常/独立全21postを実証する。AST/CLI compileだけでは推移graph成功ではない、host隔離import/実抽出functionnamespace正常＋依存各一件欠落拒否を予防必須とする。実Root/backend/SAVE/phase失敗・close未知を正常化せず新slotへ分離、旧143/UNKNOWN保全・操作二重0。候補署名/readonly/hostcore100を実新parent/native/global100/正式/ITSTの代用にしない。

SSC232（2026-10-09）PT追加：当PG662 verify import-before-main失敗の固定Java2141065/ticks11112630/argv4406b878…だけを対象とし、sudo親/他PID/子有/boot・exe・UID・argv・ticks・classpayload違い、error-only以外/新input既在、全20原値変異、peer/advisory非zero、他FLOCK ownerを拒否する。正常全20二読・当M/A inodeFD-FLOCK・新十Ref保持・durable一回pidfdTERM予約→当Java15秒消失/資源0/全原値二読不変・全新metadata scope正常を実証する。旧actual143/closeUNKNOWNを保持し、旧正常化/二重TERM/業務操作は0。新onlyv2は推移import graphを非Root・dbus非操作stubの隔離hostで正常/依存欠落拒否→実新verify/execute/post/nativeの順で閉じる。旧成功/失敗/native byte不変更、global/formal/ITST未受入。

SSC231（2026-10-09）PT追加：当36fe/PG631/schema028/currentBOM187・601297d0真正DONE/正常ownedSTOP/全資源0・全24-514とADMIN一件/空二source/18Unit source/四閉namespaceを別readonly全20二読後、SS343の新一回existing-only Bootstrapを実行する。独立goldenはCLI/null/未知cohort・署名/byte違い・ADMIN欠落/複数・source既在/旧credential復元・link/ACL/FD-path交換・非normal20/元30s超過・PID1/job不一致/普通UIDgroupscap0NNP/cgroup不一致・同INV/二重start・DB/原本Backup/他Unit変異・各DB/Ref/FD/close未知を拒否する。新credentialはprivateだけ・新native一つを当source/role/boot/INV/PID/start/終端窓/singleSession/NoMatch0へ束縛、Input退役同inode-byte/全正常資源0を独立確認。既存20を初期作成成功やglobal100/正式/ITSTへ読み替えず、旧source結果を流用0。空UserDBの別初期作成試験はこの限定fixtureへ拡張しない。

SSC230（2026-10-09）PT追加：固定completed/署名187/current36fe/schema028・genuine PID1/DONE・当正常ownedSTOP/full19/24-504を独立に確認し、新M-A/専用DB/samepeer/十Ref/保持dirFDのruntime635正規退役と全新scope正常/資源後条件を閉じる。独立literal argv/十九field・主要十18・全source/cred/native/原本/DB・七補助履歴/Caddy pairedの正常・null/欠落/foreign/current違い/未知file/同byte別inode/dirFD-path交換/ACL/mtime-ctime誤差/重複unlink/失敗reload/各close未知を拒否、原本修復/2ndstart/STOP/旧permit再用0を検査する。unlink後Unit sources18/他全byte保持・plain native Morning argvを確認し、旧未知を新normalへ置換しない。read-only全19/REUSED保持0と、新通常NEW_SUCCESS保持7実削除/Backup私有原byte保全は別受入。全同source native/session/NoMatch/coverage/CHR/formal条件は451を維持する。

SSC229（2026-10-09、SS343新一回用resume）：署名base/native独立golden・固定e492 --resume二引数、保持runtime dirFD/O_EXCL/NOFOLLOW/Root0644/ACL0/fsync、全19前後保持・元24-494/二BackupSUCCESS/epoch/原本不変を試験。主要十18属性全mutation拒否、七補助Execの同old又は同decl/exactn/aだけ、Morning新decl、Inbox/Bootstrap全configexact、Caddy両entryreset/片側混合/foreign/null/未知scope/別argv/partial/owner-peer-close拒否を独立matrixと実reload後条件へ対応。旧143/30/UNKNOWNを成功へ変換せず全newscope正常/資源0・独立post後のみ別observer/durablestart。同source真正親DONE/ownedstop/native/CHR/global100/正式は後続、IT/ST受入を宣言しない。

SSC228（2026-10-09、SS343固定failed30 pending profileの独立PT）：未完了active/graph-derived pending/completionEMPTYの全byte不変、別run/cutoff/activation、偽DONE、unknown namespace、署名/classdelta/SQL28、currentfailedPID1/INV/job/status30/予算、全24/494行・二BackupSUCCESS/元492全値、Backup/startup/epoch/Unit/sourcefiles・same-peer/owner/十九観測二読を独立literalで検証する。verify全不変、activate approval/currentだけ、epoch/active/DB/Unit変異を拒否。M/A/DB/advisory/十Ref/FD正常帰還とresources0、close/競合/半切替保全を分ける。別fresh resumeで同e492SUCCESSpair再検証・fresh worker/CONFIG・新二SKIP zero counts/bytes・八既成功参照/十attempt494→504・元原本同activationから真正DONE・owned停止/nativeを確認する。REUSED_SUCCESSの削除0/全旧Backup不変とBUG897 NEW_SUCCESS保持期限の実削除を別caseにし、hostfactory50や旧source成功をnative受入へ加算しない。全quality/CHR/DIF/同source正式条件を緩和せずIT/ST完了を宣言しない。

SSC227（2026-10-08、SS343の新candidate completed code-only）：独立literalで現oldPG548/source969/a224・新PG600/source23b/a634・完全DONE/run/cutoff/activationを固定し、全snapshot型/欠落/null/foreign/同peer/所有/namespace/有限delta/approval/epoch全fieldを検証する。旧ISSUED→同activation新UUIDv4 INVALID以外、DB482row/原本Backup/credential/native/Unit設定・履歴変更を拒否。fresh verifyとactivateを別new-only scopeで行い、全M-A/DB/十Ref/bus/FD正常・peer/advisory/FLOCK0/全原値再読を独立に採取する。PG5993457/511・静的六0は新candidate host成功、旧18nativeは非輸入/global四100未達/正式24-1964-53不変更。配備後に新source実Root/普通main/真正親DONE/owned停止/native/CHR/DIFと正式source/run全scopeを確認し、未実行・unknown・別source・失敗・skipを合格に加算しない。IT/ST完了宣言はしない。

## 1. 目的・状態・追跡

SSC-014: Username表示64byteと比較key96byteを分離し、U+0130×32/NFC/trim/Locale.ROOT/ギリシャ語文脈を独立literalで確認。旧64byte CHECKでの拒否を再現し、append-only V007で95/96受理・97/空/NULL拒否・UK維持・既存値非変更・Login audit64byteを検証する。表示/wireを拡張せず全scalarのUTF-8 lower最大3/2をJDK更新guardにする。

SSC-013: Login snapshotは独立UI232/234の688byteで検証する。成功AUTH_SESSION＋snapshot/0200、失敗ERROR/NONE/元0101・0106、初回role/期限の凍結、DB参照/AAD/hash/発行時刻不整合、key rotation/改ざん/NULL/SQL故障/100並行を含む。再送でsession/counter/監査の再更新なし。新Headerのbyte23はS（応答）、24はS（同期）をUI表から独立配置する。

詳細設計からPT（単体試験）・IT（結合試験）へ引き継ぐ分岐、境界値、異常系、競合、再送、権限、
性能・復旧の試験条件とoracle、証跡を定める。本書は試験codeではなく、後続工程の実装・実行契約である。

- 状態: `確定`。Broker再配送・容量、DB backup roleの権限、session同時上限oracleはQA-041～044/UIC-001～004承認済み
- 上位設計: UI 213、221～254、261、264
- 関連RD: TST-001～TST-005、TST-101～TST-103、T-001～T-004、PER-001～PER-010、AVL-003～AVL-010
- 関連SS: 311～353、[355_Characterization Test実行準備・PG開始gate](<355_Characterization Test実行準備・PG開始gate.md>)
- 関連QA/RDF/UIC: QA-001～QA-044、RDFなし、UIC-001～UIC-004

## 2. 試験階層・環境

| 階層 | 対象 | 外部依存 | 必須実行環境 |
|---|---|---|---|
| PT-pure | record/value/codec/validator/mapper/state machine/Range/parser | なしまたはin-process fake | Java 25、pinned Maven Wrapper |
| PT-component | Repository/migration/security/session/outbox/batch step | 実PostgreSQL 18、実file system、必要に応じ実Artemis | Containerまたは隔離local instance |
| IT-interface | Web→Artemis→API→PostgreSQL/file | 全component実process | Java 25、Artemis、PostgreSQL 18、Caddy |
| IT-operational | systemd/morning/backup/restore/resource/security | 実OS unit・volume・port | 16GB/256GB構成相当の隔離環境 |

H2、in-memory Queue、ObjectMessage、file代わりのbyte arrayだけで、PostgreSQLのconstraint/lock、Artemis File Journal/
transaction/redelivery、file systemのsymlink/atomic renameを合格扱いしない。テスト固有profileでproductionの認可・暗号・
redactionを無効化しない。

## 3. 共通試験契約

各caseは`Test ID`、関連RD/UI/SS、事前条件、入力・故障点、実行手順、期待HTTP/wire/DB/MQ/file/log、
後条件、実測値、証跡path/hashを持つ。時間依存caseは制御clock、並行caseはbarrier/latch、crash caseは
明示的failpoint名で再現する。`Thread.sleep`の長さだけに依存する合否判定を禁止する。

- 同一fixtureの初期化とcleanupをcaseごとに実行し、実行順依存をなくす。
- 期待errorはexception classだけでなく、wire result/HTTP、DB/MQ/fileの非更新、audit/error codeまで確認する。
- 機密値はfixtureに一意canaryを使い、log/metric/report/DLQ/property/DBの禁止領域で検索0件を期待する。
- 確率・競合caseは少なくとも100回反復と一意seed再現を行い、失敗回のseed/event IDを保存する。
- 合格はassertion数0ではなく、対象分岐・上下限・異常codeの要求coverage 100%をmatrixで証明する。

SSC-024: PT-IDEM-RO01～RO04はread-only Message snapshotと通常Inboxの照合共通性を確認する。不在を予約とみなさず、別Message同tokenを拾わず、保持期限/状態/row数非更新、row lock非取得、100並行、全identity/HMAC/key/NULL/JDBC故障を拒否する。最終writeのUK/再照合と復号・業務参照検査を省略しない。

## 4. PT詳細観点

SSC-025: PT-SCN-009-Q01～Q04で6 requestのUI234手組DATA、SS323 §9.1の全field順/ASCII名/type/LP null/数値/HMAC、keywordとquery正規化の分離、null/未知/UTF8/NFC/境界、実DB6分岐とDetail不在・entry/audio順を確認する。Header/meta変更をpayload HMACへ混入させず、同じdecoded値をSQLへ渡す。Request振分け部品は最終response/Inbox/file再送の完了には算入しない。

### 4.1 PT-CODEC（SS 322・323）

| ID群 | 必須観点 | 期待 |
|---|---|---|
| PT-CODEC-H-* | 256 byte header全field、offset、ASCII/N/X、protocol/layout/result、UUID、count/length | 全byte一致、未定義/gap/overlap/total不一致は恒久error |
| PT-CODEC-L-* | 64 layoutそれぞれmin/max、0/1/max record、`256 + data + record × count` | UI 233～236の宣言長と完全一致 |
| PT-CODEC-S-* | NFC前/後、日本語・surrogate・combining mark、byte上限-1/上限/上限+1 | Code-point境界でpadding、切断・暗黙truncateなし |
| PT-CODEC-P-* | Space/zero padding、sign/decimal禁止、control/NUL、invalid UTF-8、unknown enum | Decode/encode双方で一意error step/code |
| PT-CODEC-E-* | Error response filler、record count 0、body不足/過剰、上限1,000,000 byte | Result-code profileに従い、不正bodyはDLQ/process exit引継ぎ |
| PT-CODEC-AUTHERR-* | LGNRSP01/0106 retry0/1/900/901、message256/257byte、秘密field filler、他error retry0、31response全error組合せ | UI234独立432byte vectorとUI写しTSVで全byte検証。NTC0107例外維持、blank goldenだけでは代替しない（SSC-012/BUG-023） |

Golden vectorはlayout IDごとにencode完成byteのSHA-256、field境界hex、decode recordを保存する。

### 4.2 PT-AUTH（SS 314・352）

SSC-023: PT-AUT-007-R01～R04で事前確認の実PostgreSQL read-only、User/session row lock非取得、idle/transaction所有の不変、全認証拒否・NULL/未知role/JDBC複合故障、100並行、事前確認後の失効を最終verifyが拒否することを確認する。段階serviceのInbox/file再送gateは別途必要。

- Username NFC/trim/lowercase key、Login passwordのNFC前後と0/1/256/257 byte、作成password 11/12/128/129文字と255/256/257 byte、末尾ASCII space、
  PBKDF2-HMAC-SHA256のparameter/世代ID/rehash、先頭72 byte同一・末尾差分を含む全256 byte照合、存在/不存在timingの統計的差。
- USER 4/5失敗、IP 9/10失敗、15分直前/到達/直後、成功clear、disable/lock/reset、同時Login race。
- SSC-009/BUG-021: failure窓は終了一致を旧窓に含め、strict超過だけreset。初回1失敗＋終了時刻で4失敗のUSERはlock、終了+1nsなら非lockをCurrent/NK独立比較する。IPは初回1＋9失敗で同境界を検証する。lock有効性自体は終了一致でfalseのまま、DBではμs境界を照合する。
- Session 1/2/3件、idle 8時間直前/到達、restart、fixation、cookie hash、ciphertext/tag/AAD/key version改ざん。Current Characterizationの3件継続は`DIF-016`のみのoracleとし、NK PTは3件目Login後を`[最古=revoke、残り2件=active]`で必ず合否判定する。
- CSRF欠落/不一致/別session/再利用、SavedRequestのsafe GETとexternal/POST拒否、Logout POST、cache/header。
- USER/ADMINの全route/layout、owner/他人/不存在の404/403使い分け、Web/API二重検証、Web業務schema grant 0。

SSC-015: Logoutはknown contextのowner lookupからInboxへ入り、同Message再送で失効/監査の追加0、別Messageの既失効0200で元時刻/監査1を確認する。Snapshot/AUTH_SESSION/owner/hash/失効日時の不整合と鍵/DB故障はdeny closed。Known ownerの0102は元error維持、unknown contextはInbox0、通常業務のactor発行/idle延長0。LOGREQにない現在client IPを過去Login IPから補わず、失効監査SQL NULLとLogin/REPLACEDの当該IP維持を負/正常testする。

SSC-016: 固定Clockだけでなく受信→業務入口→Inbox完了→reply構築を各1秒進めるClockで検証する。業務row/critical auditは同時刻、Inbox expiresはcompleted+24h/7d、wire headerは構築時刻、replay DATAは元業務時刻・headerだけ更新、保存期限不変を独立Instant/byteで確認する。

### 4.3 PT-IDEM・STATE（SS 312・324・332）

| 入力 | 期待 |
|---|---|
| 同Message ID・同body | 保存済response replay、業務更新0、`0200` |
| 同Message ID・異body/layout/owner | Protocol/security conflict、更新0、警告証跡 |
| 異Message ID・同token・同fingerprint | 同owner/operation/targetの保存済結果、更新0 |
| 異Message ID・同token・異payload | HMAC不一致`0105`、更新0、SECURITY log |
| Current/previous/unknown HMAC key | Current/previousは許可期間だけ一致、unknownはdeny closed |
| RECEIVEDの取消vs開始 | CASで1方だけ成功、CANCELLED後処理なし、PROCESSING後取消`0107` |
| 論理削除vs再読込・通知 | Ownerから即時非表示、FKは残り、期限/状態前の物理削除なし |

### 4.4 PT-DB・SQL（SS 331・332）

- 全PK/FK/UK/CK/NOT NULL、DEFERRABLEの有無、ON DELETE RESTRICT、複合game FK、partial index predicateをcatalog自動照合。
- N12/N9の0/上限/上限+1、UTF-8 byte上限、timestamptz境界、logical delete/version、sequenceのmigration後値。
- 検索条件の単独/AND/escape、大小文字、sort tie、0/-1/1/最終/超過page、0/50/100/101件。
- SSC-017: ScenarioはCurrentのLIKE/ILIKE wildcard/escape解釈を独立fixtureで維持する。話者名同名集計（gameあり/なし）、6条件の同一statement count/page、代表voiceと非voice、file title/順序、Entry indexからのsequenceと展開後200/201/10000/10001 record、必須DB NULLの非補完を検証する。
- SSC-018: FK先Speaker名と保持labelが異なるfixture、NULL/空/ASCIIspace/Unicode blankのchapter/sectionでCurrent由来表示期待値を照合する。検索/明細speaker、一覧/現file/前後titleを全て対象とする。
- Query IDごとのindex利用候補、statement timeout、N+1不発生、ADMIN/USER/technical/migration roleの正負grant。
- Optimistic version 2更新、`FOR UPDATE SKIP LOCKED`複数dispatcher、deadlock/timeout/connection切断のrollbackとretry範囲。

### 4.5 PT-FILE・RANGE（SS 333）

- Empty/absolute/`..`/separator違い/NUL/Unicode欺瞞・各segment symlink・root symlink・hard link・open前後差替えを拒否する。
- Descriptorのsize/hash/MIME/suffix/owner/layoutを1項目ずつ改ざん、`.part`、欠落、短い/過剰file、atomic rename失敗。
- SSC-022: producer開始前の起動probeで、診断A/Bの実force/hash/属性・native no-replace collision・directory fsync、所有済診断fileだけの清掃を確認。既存業務ready非更新、公開不確定ready保全、清掃/close故障による起動不合格、full root/exclusive/readinessとの別gateを追跡する。
- SSC-021: shared storage抽出で旧/新package PTの欠落/重複を防ぎ、全module coverage/静的解析を継続。Web readerは既存dateのみread-onlyでopenし、保持inodeの属性/hash先行・4800byte decode・再hash/sequence後にだけ値を返す。最大48MB/10000件、100並行、内容途中変更、symlink/hardlink、属性/EOF/部分read/close故障、FD全解放・file非更新/非削除を確認。認可/HTTP503/logging・full root/readiness・実service UID分離は別gateとする。
- SSC-019: API writerの実libc openat/mkdirat/renameat2(NO_REPLACE)/unlinkat/fsync/closeについて成功・errno・同名100並行を確認する。Root/date差替え後も保持FD先だけを操作し、callback中のclose/reuseを防ぎ、途中open/close故障で所有FDを残さない。Java ATOMIC_MOVEの既存target置換を許容しない。Root admission/permission/nlink/readinessとwriter全体の故障試験は、この低level試験だけで完了にしない。
- Scenario 200/201/10,000/10,001 recordと48,000,000 byte、transfer 5GB/5,000/9,000件境界、朝削除cutoff。
- Rangeなし、`0-0`、`0-1048575`、1MiB超、open-ended、suffix 1/total/total+1、複数・不正・overflow、416と`bytes */total`。
- Inline/downloadのMIME/Content-Disposition UTF-8、HEAD、If-Range非対応の扱い、owner違反の非存在同一応答。

### 4.6 PT-BATCH・OPS（SS 341～343）

- 05:00起動のstep全分岐、lock二重起動、root/symlink/mount/owner/mode不正、中止時点でのresume。
- PostgreSQL dump/list/restore/hashの成否、新規directory atomic publish、7/8世代、同日再実行、backup失敗時の業務cleanup skip。
- 保持cutoff直前/同値/直後、PENDING/PROCESSING/DLQ/security hold、chunk commit前後kill、FK RESTRICT、個別warning継続。
- Config allowlist/unknown key、environment差分、credential permission/symlink、release/config/schema/protocol/hash driftの起動拒否。

### 4.7 PT-LOG・SECURITY（SS 351・352）

- Action/error/result/metric label catalogの全値とunknown拒否、field byte上限、CRLF/control、JSON encode、UTC。
- Password/hash/context/cookie/CSRF/HMAC/AES key・nonce、質問/回答、fixed body、absolute pathのcanaryが全証跡で0件。
- Metric labelがusername/ID/request数で増加しないこと、warning/critical直前/到達/回復とopen/count/close。
- CSP/CSRF/header/XSS/SQL/CRLF/path/MQ ACL/DB grant/secret permissionの正負test、DEBUGでもredaction同一。

## 5. IT詳細観点

### 5.1 IT-E2E・INTERFACE

1. 64 layout全てをWeb→Artemis→API→DB/file→replyの実BytesMessageで最低1回通す。Request/replyの
   transport/business/correlation ID、wire byte長、DB後条件、画面表示、log相関を同一証跡にする。
2. Login/Logout、Scenario、Animation/Music、Log、User、質問/通知/取消/回答・削除をUSER/ADMINで通す。
3. Web REQUEST JSON→technical outbox→WLGEVT01→`app_logs`をBroker/API停止跨ぎで再送し、source Message IDの欠落/重複0。

### 5.2 IT-CRASH・RETRY

| Failpoint | 必須後条件 |
|---|---|
| Request receive前/後、DB commit前 | JMS rollback/redelivery、業務更新0 |
| DB commit後・reply send前 | Inboxによる再受信replay、業務更新1 |
| Reply send後・JMS commit前 | Transaction rollback後replay、Webは相関1結果 |
| Outbox claim/send/JMS confirm/mark-sentの各間 | 未送信の取りこぼし0、duplicateはInbox/broker cacheで1結果 |
| Async state RECEIVED→PROCESSING、answer/notification/outboxの各間 | FIFO、state/answer/notification/DLQが説明可能な一意状態 |
| Reply遅延がWeb 2秒timeout後 | 別requestへ取違え0、late reply ACK/metric、token再操作で結果回復 |

Broker/API/Web/PostgreSQLの単体・組合せ停止、Broker reboot、API restart rate limit、network loopback遮断、disk fullを
故障注入する。Artemis File Journalの通常crash recovery、破損検知、Queue件数回復を証跡化する。

### 5.3 IT-ASYNC・DLQ

- Consumerを必ず1とし、同時投入順/FIFO、処理中の後続停止、business timeoutなし、空回答STUBを確認する。
- Temporary errorは初回＋3再配送。第1=1秒、第2=5秒、第3=25秒をQA-041/UIC-001承認済みの一意なtest oracleとする。
  許容差は計測開始点とscheduler精度を含めてIT環境で事前定義し、順序と設定値そのものを緩和しない。
- 恒久protocol errorは初回でDLQ・ACK・nonzero exit、DB不能の最終再配送はDLQとjob整合runbookを実行する。
- DLQ/Expiryのbody非表示、browse権限、個別replay、同Message ID Inbox replay、自動purgeなしを確認する。
- 321 §5.3のAddress別memory high-waterでPAGE開始、byte/件数page limitでFAIL＋9001、filesystem 90%でBLOCK＋readiness false、
  復旧後outbox retry・message欠落0をQA-042/UIC-002承認済みの一意なoracleとする。

### 5.4 IT-OPS・RESTORE・SECURITY

- Morning依存順、stop timeout、systemdの10分5回rate limit、Caddy 55160だけpublic、loopback portの非公開。
- Backup復元を隔離DB→新instanceの順で実行し、schema/role/constraint/count/Queue整合、RPO/RTO 24時間を測定。
- QA-043/UIC-003承認済みの専用backup roleで3 schemaをdump/restoreでき、batch roleではdump/任意SELECT不可、
  backup roleではDML/SET ROLE/復号key取得不可であることを一意なoracleとして検証する。
- Asset master 59,627 file/19,240,707,190 byte、Scenario 262/99,661、audio 37,256、link 35,201、video 20、music 129をhash/count検証。
- USERからADMIN/他人、直接Queue/DB/file/port、credentialのargv/env/log、CSP/CSRF/session改ざんを攻撃testする。
- DEBUG→STANDARD切替で詳細metric componentを停止しても、systemd/journal/DB/Artemis/disk/最小healthが継続する。

### 5.5 IT-PERFORMANCE・CAPACITY

| 負荷 | 判定 |
|---|---|
| STANDARD、同時10名×1同期request | End-to-end p95 <=2.5s、MQ待ち<=2.0s、取違え0、timeout/error率併記 |
| Search worst、Log 100、新規一覧50、Scenario 10,000 | Query ID・plan・pool・heap・wire/file上限内 |
| 20 media stream/Range 1MiB | 同時数上限、Range開始、FD/thread/direct memory、他画面p95への影響 |
| Async/Web log Queue 70/90%、transfer 3.5/4.5GB | Warning/critical、新規受付9001、既受付・証跡を失わない |
| 16GB memory・256GB disk budget | Systemd MemoryMax、PG/Artemis/JVM/direct/journal/paging/backup合計が上限内。ArtemisはQA-042/UIC-002承認済みのmemory/page/page-full/disk-full policyを実効値で検証 |

## 6. Test data・fixture

- `PT-BASE`: USER 3、ADMIN 2（active/self保護を含む）、各stateのQuestion/Job/Notification/Answer、各game/media。
- `PT-BOUNDARY`: 各fieldの0/1/max-1/max/max+1 byte、NFC/NFD、禁止control、同sort key、存在/欠落file。
- `IT-CURRENT-MASTER`: 264に固定したcurrent masterのread-only copy/manifest。原本を書き換えない。
- `IT-FAULT`: failpoint、Queue/disk/clock制御、ダミーcredential。Production credentialを試験に使わない。

Password・key・contextはGit管理しない。Fixture生成seed、schema/protocol/config version、master manifest hashはGitと
reportに固定する。

## 7. 証跡・合否・不具合分類

| 証跡 | 内容 |
|---|---|
| Machine report | JUnit XML/HTML、case ID、duration、seed、environment/release/config/schema/protocol |
| Interface | HTTP header/body hash、wire SHA-256/byte length、JMS propertyのredacted dump |
| Persistence | SQL assertion/query ID、constraint/index/lock、Queue/DLQ/Expiry count、file manifest/hash |
| Operation | systemd/journal/metric/alert、backup/restore manifest、failpoint timeline |
| Trace | RD→UI→SS→test ID、requirement coverage、未実施/除外理由・承認 |

Failed/flaky/skipped/not-runは合格に算入しない。不具合は(a) PG実装不具合、(b) SS設計不備、
(c) UI修正必要、(d) RD修正必要、(e) environment/toolingに分類する。(c)/(d)は対応台帳へ先に登録し、
上位期待値をtestに合わせて無断更新しない。

## 8. Entry/exit gate

PT開始は対象class/migration/configとreview、関連SS/test case、fixture、実環境の準備完了を条件とする。
IT開始はPT必須case合格、同一release artifact、全componentのconfig/credential、障害注入・rollback手順を条件とする。

PT/IT完了は必須caseのfailed/flaky/skipped/not-run 0、重大不具合0、trace/coverage 100%、証跡のrelease commitひも付け、
機密漏えい0、resource/restore実測値の設定manifest反映とする。Backup権限caseはQA-043承認oracle、
Address容量/paging/full-policyはQA-042承認oracleを必須実行し、`skipped`を合格にしない。

## 9. SS設計判断

| ID | 判断 | 根拠・理由 | 後続影響 |
|---|---|---|---|
| SS-D-051 | DB/MQ/file依存のcomponent PTとITは実PostgreSQL/Artemis/file systemで合格判定 | T-001/T-004、dialect・lock・journal・pathの代替実装差を見逃さない | Test environment/container/OS fixture |
| SS-D-052 | Crash pointを名前付きfailpointでDB/JMS/outboxの境界ごとに試験 | 時間依存でなく再現し、処理結果を一意に検証 | PGのfailpointは試験build限定、IT証跡 |
| SS-D-053 | Broker再配送oracleをQA-041/UIC-001承認済みの1秒、5秒、25秒へ固定 | Artemis標準倍率式とUI 231を一致させ、releaseごとの任意値化を防ぐ | 321/342/353/354/test dataを同値維持 |

## 10. 禁止事項

- H2/in-memory mockだけでPostgreSQL/Artemis/file結合を合格、flaky/skippedをretry成功で隠蔽。
- Productionの認可、CSRF、暗号、constraint、redaction、durabilityをtest profileで無効化。
- DB/Queue/fileをcase後条件確認なしに一括purgeし、二重更新・DLQ・取違いを検出不能にする。
- 実測が上位仕様と異なる際にoracle/設定だけを書き換え、QA/RDF/UIC/変更管理を省略。

## 11. 更新履歴

| 日付 | 内容 |
|---|---|
| 2026-08-31 | PT/ITの分岐・境界・異常・競合・再送・性能・復旧と証跡/gateを詳細化。 |
| 2026-08-31 | 横断監査でPassword試験をNFC・256 byte全長を扱う`pbkdf2-v1`へ統一し、QA-042/UIC-002のArtemis容量・paging pending oracleを追加。 |
| 2026-08-31 | QA-043/UIC-003の専用backup role、batch/backup相互権限、dump/restoreのpending oracleを追加。 |
| 2026-09-01 | QA-041/UIC-001承認を反映し、再配送時系列oracleを1秒、5秒、25秒へ確定。 |
| 2026-09-01 | QA-042/UIC-002承認を反映し、Address別memory/page上限、page-full FAIL、disk-full BLOCKの容量oracleを確定。 |
| 2026-09-01 | QA-043/UIC-003承認を反映し、backup/batch role相互権限、3 schema dump/restore、復号key非配布oracleを確定。 |
| 2026-09-01 | QA-044/UIC-004を反映。Currentの3 session継続とNKの最大2・最古revokeを分離し、NK PTの3件競合oracleを固定。 |

## QA-050承認反映：再試行のPT・IT/STと間隔調整（2026-10-03）

独立PTは期限NULL/推測期限非採用/遅延TOUCH、0000/0200のみ削除、一般0102と物理session削除後も保全、復号不能、100飽和後の継続、expiry±1µs、唯一claim/lease takeover、JMS待機中DB解放、鍵rotation/borrower、登録/commit/close不明とlocal破棄、実DB・Clock/latch/JMS競合を含む。API expired fence補足は既定User→session lock・監査・0102 ERROR snapshot不変と遅延認証拒否を確認する。

QA050承認に基づき、初期5秒/30秒/5分後の継続再試行を15分で実装する。ITおよびSTの性能試験で、再試行なしの通常業務を基準に同じ通常業務負荷へ再試行を重ね、問題が確認された場合に間隔を変更する。初期短間隔の挙動を15分定常平均だけで評価しない。

試験条件は正常Logout、API/Broker停止→復帰、既存session/物理削除済み0102/復号不能、due集中と分散、複数workerのlease競合、残件100/1,000/10,000の計画容量点と想定運用ピークを含む（件数は試験点であり実運用の残件予測ではない）。実時間の15分運転・反復滞留をIT/STで確認し、仮想ClockのPTだけを性能実測に代用しない。

既定性能基準（STANDARD同時10名×同期request、end-to-end p95<=2.5秒、MQ待ち<=2.0秒）と既定資源予算を維持し、timeout/error率・API/DB CPU・lock待ち/pool・Inbox増加/WAL・MQ/journal/disk・再試行残件/最古時間と解消までの時間を同条件で記録する。基準未達や再試行起因の資源逼迫があれば因果を確認し、DB/lease/送信制御等の不具合を単に間隔変更で隠さない。

間隔による負荷が原因なら継続間隔を調整し、同条件の通常業務性能・障害復帰・失効確認遅延/残件解消を再測定して採用値を決める。変更前後の設定値/source/環境/負荷件数/測定期間/比較結果/判断者を残し、UI226/242/253・SS314/343/354と変更台帳を整合してmainへ反映する。保持/削除proof・鍵保全・8h idle・wire/認可条件は間隔調整で変えない。IT/STの合格と実装/配備の完了は実証まで未完了とする。

## SSC309 exec中の世代とreadyの独立反例

PT-OPS-EXECGEN309001～003：API/Web固定世代の一時Z→同PID/startTicksのordinary復帰、Z継続中は終了false、二回NoSuch後のみ終了true。Zを初回Root/self/PID1へ使えず、X/x/未知、不正/別ticks、cgroup/Unit drift、未知IOを拒否する。世代guardの通過だけではreadyにならず、空cmdlineはsocket/HTTP前false、復帰後は完全ordinary/same-socket/HTTP200 UP/infoを要求し503を拒否。kernel fixtureはpidfd非終端を独立に観測し、業務Root再起動を使わない。元失敗raw state未保存と新再現を区別し、旧source成功/失敗nativeを新sourceの正常nativeへ合算しない。元期限/UNKNOWN/451四100は不変更、fresh必要全体と実nativeは別受入。

## SSC-437 CleanupKind親stepの固定metadata責務（2026-11-16）

CleanupKindの閉じた九種から親BatchStepへの対応を各enum定数のfinal parentStep fieldで表す。private enum constructorへ固定BatchStep引数を追加しObjects.requireNonNullで内部invariantを確立、step()はfinal fieldを返す。対応はNOTIFICATIONS→CLEAN_NOTIFICATION、QUESTIONS→CLEAN_QUESTION、SESSIONS→CLEAN_SESSION、OUTBOX→CLEAN_INBOX_OUTBOX、LOGS→CLEAN_LOG、WEB_RECEIPTS/BATCH_RUNS/INBOX_PROGRESS/LOG_PROGRESS→CLEAN_BATCH_RUNの既存九件を完全保持する。enum名/定義順/ordinal/values-valueOf/public method descriptor/function()/maximumRows()/親BatchStep.backup/SQL識別子/DDL/削除条件/transaction/実行権限/HTTP電文/画面/承認DIFを変更0。private constructor内部引数だけで外部binary method/type kindは変えず、enumは不変metadataで実処理/原本/所有/commitの証明ではない。元switch式のraw生成default1分岐6命令不足BUG3083は除外・到達不能宣言・反射で埋めず、責務を既定値に保持する表現へ修正する。元Boundary二Testclass四＋独立値四の全三class8のfixture/入力/独立期待/全sourceを変更0、新sourceのfreshMain10RootNullAway/全静的/同singleexec全8/current186physicalCRC-init/XML/raw全十Codeclassで再検証する。旧default四100/別source/rawを現source合格へ加算0、未実行/HOLDのrepository/SQL/DB/Root2Actual4/鍵/VM/native/aru/終了依存を代替0。内部詳細補足でRD/UI/QA変更不要、全WBS/正式受入は個別criteriaと終了依存が満たされるまで更新しない。

BUG3083/YKT2431、状態:設計確定・main反映前、PG/PT/全criteria・終了依存/正式未完。

## SSC-438 batch理由の固定診断metadata責務（2026-11-16）

BatchStepResult.Reasonの固定11診断を各enum定数のfinal nullable diagnosticSummary fieldで表し、private constructorの@Nullable String引数へ既定値を明示しsummary()はそのfield読取とする。NONEのみsummary NULL、ALREADY_SUCCESSFUL→step already successful for business date、BACKUP_UNAVAILABLE→verified backup unavailable、PROTECTED_RECORDS→protected records retained、ABANDONED→previous same-run attempt abandoned、DATABASE_FAILURE→batch database operation failed、COMMAND_FAILURE→batch command failed、SAFETY_FAILURE→batch safety check failed、IO_FAILURE→batch file operation failed、TIMEOUT→batch step deadline reached、INTERRUPTED→batch step interruptedの既存固定文を完全保持する。enum名/順序/ordinal/public descriptor、Reason.code()及びallows(Status)の全body、外側recordのStatus/Reason NN・各計数非負/SUCCESS failure0/SKIPPED全0と17許容27拒否の44組合せ・固定秘匿診断を変更0。private constructorは閉じたenum初期化だけでnullableは既存NONEの契約を表し、任意入力/例外/SQL/path/body/credentialを診断へ取り込まない。switch式が生成するsummary default1分岐6命令の未実行BUG3085を除外/到達不能/反射/偽enumで埋めず、既定値を保持する責務表現へ是正する。元独立全4Testsource/fixture/全期待をbyte exact保持、新sourceのfreshMain1RootNullAway/全静的/同singleexec全4/current179physicalCRC-initXML/raw全三Codeclassで確認する。DB schema/値互換/transaction/原本/所有/権限/HTTP/UI/電文/DIF変更0、元8反射fixtureやRoot2Actual4/DB鍵/VM/native/aru/HOLDを実行・抽出・代替0。旧sourceのdefault四100/raw不足を新sourceへ加算0、正式/全WBS/451/終了依存は別受入を維持。

BUG3085/YKT2431、状態:設計確定・main反映前、PG/PT/全criteria・終了依存/正式未完。

## SSC-439 純例外policyの非instance namespace責務（2026-11-16）

MorningSqlFailuresとJdbcResourceFailuresは例外優先順位だけを扱う非instanceのpackage-private static namespaceとし、final class宣言とprivate空constructorだけをstatic-only package-private interfaceへ置き換える。全static method名・descriptor・注釈・bodyを逆展開byte exactで保持し、既知SQL/IO/catalog判定・null契約・primary/secondary優先・suppressed固定診断・Error cause/suppressed/SQLnextのidentity付き有限BFS順・閉じたredactionを変更0。新instance/abstract method/field/portを導入せず、型のpackage可視性は不変。型kindがclassからinterfaceになるため旧Methodref callerbinary混用は禁止、全十sourcecallerのpath/hash/owner/static呼出箇所を保存、将来releaseは全caller/fullmoduleをfresh再compileする。今回は実JDBC-DBやHOLD依存の全callerをcompile/実行せず、二純helperを呼ぶ元Morning12/JDBC8を全source byte exact保持し、新たな独立StorageReason固定3値のvalues/valueOf/ordinal/defensivearray/未知空大小文字/null/固定Storage診断契約1だけを加え、新source同一run21で四Main五Codeclassの全分岐・raw四counter100/RootNullAway/全静的/currentCRC-initXMLを検証する。StorageIoExceptionのproduction bodyは変更0、実DB接続/driver/transaction/credential/Root2Actual4/鍵/VM/native/aru/permit等のHOLDを代替せず、旧二sourceのraw不足や成功は歴史証拠で別保持する。BUG3087/YKT2559/YKT2431、SS332333354。private反射/空instance生成/除外/到達不能扱いで未網羅を埋めない。内部責務の詳細補足のみでRD/UI/QA/承認DIF変更不要、全caller/451/正式受入は未達条件が閉じるまで更新しない。

状態:設計確定・main反映前、PG/PT/全caller/正式未完。

## SSC-440 public純utilityの非instance責務と局所pattern（2026-11-16）

ResourceScope・InspectorRunEnvironment・InspectorStaticEnvironmentの非instance責務をpublic static-only interfaceで表す。publicfinal宣言/空privatectorを除去し、既static methodとResourceScopeの四nested functionalinterface、MAXIMUM_BYTES定数は既public descriptor/型注釈/可視性/値を保持、interfaceで暗黙publicになる冗長modifierだけを除く。ResourceScope/RunEnvironment全method bodyは逆展開formatted exact。StaticEnvironmentのprivate int二値・Pattern二式はrequireValidのmethodlocal finalへ移し、既regex文字列/判定/ループ/固定例外は識別子置換を逆展開して保持する。private Patternをpublicfieldへ公開せず新port/設定/権限/instanceを導入0、MAXIMUM_BYTES65848/最大names65536/TCP65535/ASCII sourcegrammar/version1-16/重複拒否/NN/UTF8規則を変更0。Patternは各呼出の既NN-サイズ検査前に元の順で構築し非共有、型初期化cacheから局所へ移るallocation差を記録、fatalErrorをcatch/正常化せず実heapOOMEやIT性能は未測定として後続へ残す。class→interfaceの旧Methodref binary混用は禁止、全Main参照sourceのpath/hash/owner/行を列挙し全caller/fullmodule fresh再compileを将来release条件にする。今回は元ResourceScope8/Factory18/RunEnv4/StaticEnv6の全36Test source/独立期待byte exactを保持し、既StorageIoException/Reasonの公開catalog・有限identity BFSを独立新2、BatchRun全NN・年1..9999・µs拒否/recordを新1で補い、新source同run全39/freshMain5Root/全静的/physical10中Code6と自然Code0四interface/CRC-initXML/raw必須四100で確認。無意味instance/私有反射/除外/到達不能扱いをしない。callbackの取得-返却-移管-一回解放/IO対unknown優先/固定suppression、runfile/静的fileのbytesと全診断を不変更。実FD/VM/DB/JMS/credential/鍵/Root2Actual4/aru/HOLDや全callerを代替0、旧Core5aの無関係Data59の確認再演やoldexec合算0。内部詳細の範囲でRD/UI/QA/DIF変更不要、BUG3090/YKT2562/YKT2431、SS333343354、全451/全caller/正式未受入を維持する。

状態:設計確定・main反映前、PG/PT/全caller/正式未完。

## SSC-441 Inbox閉Reasonの固定SQLstateとhash契約PT（2026-11-16）

BUG3100/YKT2572のInboxException.sqlState閉enum switchを、Reason五定数が既固定SQLstateをprivatefinal metadataで保持する表現へ置換する。MESSAGE_ID_REUSE/OPERATION_TOKEN_REUSE=23000、FINGERPRINT_KEY_UNAVAILABLE=55000、STATE_CORRUPT=XX000、TRANSACTION_REQUIRED=25000の順序・name/ordinal/values/valueOf/可視性を完全保持する。private enum constructorだけで五つのnonnull literalを一度代入し、package-private accessorをouter privatehelperから読む。privatehelperはObjects.requireNonNull(reason,reason)を元と同じmessageで先に行い、SQLException継承/constructor/message/SQLstate/errorCode/reason getter/throw identity・全caller public ABIを変えない。閉定数のprivate constructionへ到達しないnull guardや反射用経路を足さず、NullAwayとliteral閉包でfield invariantを確立する。生成MatchException defaultだけが表現から不要になるので、coverage除外/到達不能合格/別enum binary/私有反射/無意味instanceを使わない。BUG3101/YKT2573の新Request fixtureは独立期待retainedを保持し、単一entry Map.of.getから実HashMapへのput/getへ変えてhash-equalityを実操作で確認する。元21のTest ID・入力・期待・全assertとMain1の他bodyを逆展開formatted exactで確認する。SS範囲内の内部詳細でRD/UI/DIF/QA変更不要。先にSS324352354914だけをmainへ反映してからPGし、新Core同run全21/freshMain14Root/適用未分類0/current15physical15CRC-initXML/同singleexecraw必須四100を要求する。五SQLstateとNullableReason拒否のgoldenは元21を保持、元raw不足PG35714を残し旧exec合算0。全caller source/既public ABIの一致を確認するが、実DBcoordinatorや全module/全451/native/CHR/終了依存の受入にはしない。Actual4/Root2/鍵/VMDB/native/aru/HOLDを維持、古いRootや無関係PTを確認だけで反復しない。

状態:設計確定・main反映前、実装/全21再資格/全体品質は未完。

## SSC-442 N12非instance validatorと九識別子の値契約（2026-11-16）

BUG3104/YKT2576のN12共通IdValueをpackage-private static-only interfaceへ表現する。非instance責務のfinalclass宣言と空privateconstructorだけを外し、MAXIMUM=999999999999Lとvalidate(long)の全body/固定IllegalArgumentException文言を保持する。interfaceで冗長なfield staticfinalだけを省き暗黙publicstaticfinalとなるが、型自体のpackage-private境界は維持しpackage外へ新型を公開0、private状態やPatternを公開0。static validateもinterfaceで暗黙publicとなる内部flag差を記録し、全Main参照をsource/owner/行で列挙する。九record constructorのinvokestaticはInterfaceMethodrefへ変わるため全九callerを同じRoot/sourceでfreshcompile・実constructor実行し旧class型helperとのbinary混用禁止、全module/release JAR再構築は後続条件。publicProtocolIdと九recordの型/permits/component/constructor/getter/equality/hash/toStringの既ABI・意味を維持する。九IDだけの正値N12であり0許容のcount等generic数値fieldへ適用を広げない。独立new3通常PTは九factory×正常1/123/MAX・異常LongMIN/-1/0/MAX+1/LongMAX、固定診断、全record同値/異値/null/異型/独立signed32 Long hash/既literal表示、全81型対と実HashMap九key保持を確認する。期待MAXをproduction定数から生成0、private反射/空instance/除外/到達不能合格0。Main11/physical11(10Code・ProtocolId Code0自然N/A)/freshRoot/static/current10CRC-initXML/同run3/raw四100を要求する。元120/124やaccepted17全面再資格を行わず、元raw不足PG35880と旧JARは保全・合算0。RD/UI/DIF変更不要のSS内部詳細、SS322323354914をPG前にmainへ反映する。Actual4/Root2/VMDBkeys/native/aru/HOLD・全451/正式/wholeProtocolModule未受入を維持する。

状態:設計確定・main反映前、製造/通常PT3/全module/正式未完。

## SSC-443 PathSyntax非instance字句検査と二callerの現source契約（2026-11-16）

BUG3107/YKT2579のうちPathSyntax責務だけをpackage-private static-only interfaceへ整理し空privatectorを除去する。二私有Patternの正規表現文字列を完全保持し、各利用method内のlocal Patternへ移す。interface fieldの暗黙public化で私有cacheを外部公開することは禁止、型はpackage-privateのまま・三static methodの暗黙public内部flag差を記録する。旧静的cacheからmethod毎compileへallocation timingが変わる内部差を明記し、PG/PTで性能又はIT/STを承認しない。先頭slash/backslash/ASCII drive prefix・slash/backslash区切り親segment・ISO control判定の順序/short-circuit/診断/Unicode処理を保持し、Pattern変数名/宣言scopeと型/ctor以外の実bodyを逆展開で一致証明する。二実Main caller RelativePath/DisplayPathはstrictUTF16検査を含む現sourceを不変のままfreshcompileしInterfaceMethodrefと両factory実行を確認、旧helper binaryと新callerの混用禁止。二path公開ABI/正規化/length/segment/equals/hash/redactedtextは不変。独立new3通常PTで境界255/256segment・512/513 UTF8total・空/絶対/drive/root/末尾separator/空dotdotsegment/control・NFC/多byte・同値異値null異型/独立JavaString hash/実HashMapを確認、既PathUnicodeBoundaryTest全2をbyte不変で必要回帰する。三Main/三physicalCode/currentCRC-initXML/freshRoot/static/同run全5/raw四100が限定条件。ProtocolValidatorの別空ctorは未修正OPENとして残し、この範囲へ成功加算しない。元Protocol120/124/accepted17全面requal/旧exec合算0、privateReflection/無意味instance/除外禁止。SS323333354914を製造前にmainへ反映、RD/UI/DIF変更不要。Root2Actual4/DB鍵nativeVMaru等HOLDと全451/正式未受入を維持する。

状態:設計確定・main反映前、製造/通常PT5/全module/正式未完。

## SSC-444 ProtocolValidator非instance責務と現Protocol全module再組立（2026-11-16）

BUG3107/YKT2579残のProtocolValidatorをpublic static-only interfaceへ表現し空privatectorを除去する。既公開PERSISTENT_DELIVERY_MODE=2とvalidateTransport(CommonHeader,TransportMetadata,ExpectedRoute)引数戻り値/例外/null/全分岐順序/固定診断を保持、private PROTOCOL_VERSION文字列001はvalidateTransport内localへ移し新publicfield公開0。classからinterfaceへのpublic型kind差とstatic呼出InterfaceMethodref差を内部Java ABI変更として明記、旧binaryとの混用禁止。全Main参照検索で直接caller FixedWidthDecoderを特定、同source Protocol全165MainをRoot規則でfreshcompile・全physicalを証明し、新helper/旧callerまたは旧helper/新callerの混合を禁止する。IdValue/PathSyntaxの先行型整理も含むため、必要なmodule再組立と通常全140PTを当source一回だけ行う。原130は成功確認で再演するのでなく、三helper型変更の下流/64layout/JMS transport snapshot/QA054/Unicode/独立goldenを同source/moduleで回帰する依存検証。既原130と追加N12三/WireEnum四/Path三の全31source(一helper含む)・五独立TSVを無変更で使用し、元source期待値をproduction methodで置換0。公開record constructor/getterに対する既public反射は固定UI由来型表/nonnull negative契約の範囲だけでprivate反射/Root権限反射無し、元有限2workerの期限/cleanup保持。実物DB/JMS接続/FS/master/鍵/VM/native/aruは操作しない。memory byte streamとtest literalのみ、枠/空き/所有を確認して新job一回とし重複起動禁止。標準coverageはdefaultfilter由来値として保存し、同singleexec全physicalのrawCodeも独立測定、missがあれば全451/当Program受入を保留・修正前BUGへ起票する。Interface/Code0/branch0は自然N/A、除外/旧exec合算/成功算術加算禁止。元904.85/SV/群開始見積保持、477停滞是正として細かなutility追加から一つの実module/caller/source閉包へ作業順を変更するが工程scope/品質/モデル/HOLDは変更しない。SS322323354914をPG前にmain反映、RD/UI/DIF変更不要。正式1964/53・正本184/625・元17/190・工数nullのまま、module回帰成功だけで全PGPT/ITST完了にしない。

状態:設計確定・main反映前、製造/通常PT140/全module/正式未完。

## SSC-445 Payload型registryの状態所有とprivate binding責務（2026-11-16）

BUG3111/YKT2583のうちPayloadTypeCatalogとprivate補助Mapping/RecordMapping責務だけを整理する。公開finalclass/四static APIの型・引数戻り値・例外/diagnostic・全64layout key/69namedtype・decoder methodref/登録順と不変Map/読取順序を保持する。privateSTANDARD cacheはclass初期化時に一回生成する実cache owner INSTANCEのprivatefinal standardへ移す。privateconstructorはこの不変registry実状態を確立し全lookupが参照する責務を持つためのもので、試験から無意味なinstanceや反射で空ctorを呼ばない。JLS class初期化とfinalfield safe publicationを保持し新publicinstance/API/可変cache公開0、性能/heap量は未測定でITST承認しない。二private recordはvalue-equality対象ではないdecoder bindingなのでprivate static final field-only classとし、実使用dataType/dataDecoder/recordMapping・recordType/recordDecoderのprivategetterとconstructorだけを定義する。外部から利用不能でsource検索上未使用のrecord由来equals/hash/toStringとMapping.layoutId accessorは生成せず、registry keyと重複するlayoutId component/privatefactory引数を除く。64Map.entry keyは不変、各mapping引数先頭に重複していた同じkey literalだけを除き、逆展開時は当Map.entry keyから元重複literal/旧privatefactory二signature/元record表現へ復元して全body/表/diagnosticをformatted完全一致で証明する。対象削除はprivateに不要なvalue APIの責務整理でありcoverage除外や到達不能合格としない。private全constructionは固定class literal/methodref/Optional.empty-or-ofに閉じたnonnull入力をRoot静的解析で確認、任意入力/private反射を追加しない。全Main参照をsource/ownerで保存し公開API javap完全一致を確認、他164Mainと既32Test source/五TSVの期待を保持する。新通常1は独立named-types-ss323.tsv64行からexpected class名/record有無を作り、有限二reader/ready-start latch/future10sec/finally shutdownNow-await10secで全64lookupを同時検証、128観測を128Testへ増幅0。初回cold-initを実測したと断定せず公開同時readとJLS安全公開根拠を分ける。Main変更の下流として同source全165Main/176physicalをfresh組立・既144＋新1＝全145通常PTを一回実行、旧source成功/exec転用0。Code変化はparent＋private2 classだけが想定で他173classのbyte一致を確認、parent/private2全Code raw100・全module rawは実値と不足を保存し全451へ昇格0。SS322323354914をPG前にmain反映、RD/UI/DIF変更不要。モデル/枠/Root2Actual4/実DB鍵VMnativearu/QA051final等HOLDと正式1964/53・正本184/625・工数nullを維持する。

状態:設計確定・main反映前、製造/通常PT145/全module/正式未完。

## SSC-446 固定長field paddingの三値dispatch（2026-11-16）

BUG3111/YKT2583のFieldDefinition compact constructor内のpadding選択だけを詳細化する。wireTypeは先行Objects.requireNonNullでnonnullを確立、承認済みWireTypeはTEXT/NUMERIC/BOOLEANの三定数に閉じる。TEXTならSPACE_RIGHT、NUMERICならZERO_LEFT、それ以外の現三値中BOOLEANならNONEという対応を、final local expectedへのif/else-if/else代入で明示する。三入力の対応・不一致時の既存診断・全null/範囲/end検査・両publicconstructor/recordcomponent/全API・独立UI TSV/期待値を変更しない。新enum定数追加はこの既定処理を無審査で流用せずwire型/設計/codec/全対応試験の変更対象とする。javac enum switch由来の理論上のunknown default/補助mapを作る必要がない責務へ整理するもので、列挙値の不正注入や反射、coverage除外、未実行を到達不能PASSに変換しない。型kindはrecordのままで公開ABI javap完全一致、変化Mainはこの一sourceのみ。元switch全byteを逆展開formatted完全一致で証明、他164Main/既全Test/五TSV不変。全165Mainを当sourceでfresh組立、physicalは元176からFieldDefinition$1のみ非生成となる175、親以外174class byte不変を独立照合。新JUnit定義0、現集約4＋必要原14＝同18を当sourceで一回必要再実行し現七class raw全line/method/class/branch100と全physical不足を別保存する。四mapを除外せず三残mapをrawで測定、全module/451/native/正式受入へ昇格しない。RD/UI/DIF変更不要、SSC設計を先にmain反映後PG。全HOLD/枠停止条件/正式1964-53/正本184-625/工数null維持。

状態:設計確定・main反映前、製造/通常PT18/全module/正式未完。

### SSC446 Root compile適合補足（2026-11-16）

SSC446補足（BUG3123/YKT2595）。Root実ビルドがcompact constructorの未初期化final expectedへの分岐代入を拒否したため、三値のif/else-if/else判定はprivate pure static expectedPaddingFor(WireType)へ置き、constructorはfinal Padding expected = expectedPaddingFor(wireType)で初期化する。先行nonnull契約/三値対応/TEXT SPACE_RIGHT/NUMERIC ZERO_LEFT/BOOLEAN NONE・既診断・公開record API・独立全期待を保持する。JDK単体の欠陥とは未証明、Root flags/静的条件を緩和しない。新private関数一methodは三入力を通常PTで全branch確認し除外0、逆展開ではhelperを除き元switchへ完全復元する。元47da/36514のcompile失敗を成功へ混ぜず保全、別freshRoot165/175physical/同18必要再試験・ABI/他174byte/raw七class100で是正を確認する。元開始.25/.75/2.25 cap2.5は維持し今回の内訳を再試行原因として記録、追加Junit0/外部仕様差0/全HOLD維持。

## SSC-447 型変換・JST日時の不変cache所有（2026-11-16）

BUG3111/YKT2583のうちTypedFieldValues/JstWireTimestampのprivate empty constructorと不変cache所有だけを整理する。公開finalclass/全public static APIとWIRE_LENGTH=17は保持、private cacheを外部公開0。TypedFieldValuesはprivate final Pattern retainedOptionalIdを実状態として所有するprivate INSTANCEをclass初期化時に一回生成し、constructorで元OPTIONAL_IDと同じPattern.compile("[0-9]{1,12}")を初期化、元parseOptionalIdはINSTANCE.retainedOptionalIdを読む。LITERAL_VALUE定数や全semantic変換/例外/範囲診断は不変。JstWireTimestampは元JAPAN ZoneId/17桁Pattern/STRICT formatter三cacheをprivate final retainedJapanZone/retainedWireDigits/retainedWireFormatterとして実所有し、private INSTANCE constructorで元と同じ順序・引数で一回生成、format/parseはその不変stateを参照する。class初期化/finalfieldの安全公開、Pattern matcherは毎callで分離、非並行mutable formatterやnew publicinstanceは追加しない。constructorは通常static経路が必ず使用する実cache状態のinvariantを確立し、試験から無意味なinstanceやprivate反射で呼ばない。追加二owner objectのheap/性能は未測定でITST合格を断定0。全cache literal/初期化順/変換body/診断を逆展開formatted完全一致、他163Main/全Test/五TSV不変、公開ABI完全一致・親二class以外173physical byte不変を確認する。生成class数は175/Code162を維持。日時header・全named69変換に影響するため、新定義0で既全35Testsource（helper含む）152通常PTを当source一回必要回帰し、両親raw100と全175raw不足を別記録、Module/451/正式を推測昇格0。元public oracleの四Class.forName/閉32public scalar/元helper inverse SHA/全期待は不変、工具は既module33/145に新二fixtureを加えた35/152構成だけ認識するよう補足し14負境界等の自己検証を実施、private/任意/HOLD反射やSDK接続を許可しない。旧同145/18の確認再演や旧exec合成0。SS322323354914をPG前にmain反映、RD/UI/DIF変更不要、全HOLD/枠10以下停止/正式1964-53/184-625/工数null保持。

状態:設計確定・main反映前、製造/通常152PT/全module/正式未完。

## SSC-448 参照DAO純JDBCとraw必須分岐

同sourceのRRF-PURE-001..008はSS332SSC448を正とし、未filter全Codeの四counterを必須判定する。SQL全文/UTC独立literal・全nullable/transaction/interrupt・各呼出例外・row/statementのSQL/RTE/Error primary/secondary全組合せ・owned各一回close・borrowedConnection不変・有限32独立fixtureを照合。原実DB8件はHOLDのまま、実DBlock/visibility/全P00403/F02F03の終了依存は別。default filter/raw両値と未hitを保存し、default100でraw不足を隠さない。共有6classも全物理集合に残し、当DAO100を全closure100へ換算0。元8定義/期待不変、公開API/他6byteと全Root静的を確認する。


## SSC-449 PostgreSQL JDBC注釈の正規compile依存（2026-11-17）

BUG3129/YKT2600、RD/UI変更なし。pgjdbc42.7.13の公式POMはchecker-qual3.55.1をruntime依存にしているが、PostgresMigrationCopyPort及びQuestionSubmissionServiceのPGConnection/CopyManager等をjavac -Xlint:all -Werrorで型検査するとorg.postgresql package-infoのDefaultQualifier/TypeUseLocationがcompile classpathへ無く10警告→終了1になる。PG36830元Maven/36834診断/36836元flagsの直接javacで同じ失敗を保全。これは製品業務処理や原本/権限の失敗ではなく、SDK注釈の依存scope不足。

Bootstrap POMへorg.checkerframework:checker-qual:3.55.1を明示compile依存として追加する。版は既pgjdbc POMのruntime版と完全一致、既toolchain cacheから使用し新規version選定/更新をしない。Bootstrapをcompile依存とするAPI/Web/Batchへも型情報を正規推移し、既runtimeに存在する同一artifactを別版へ置換/増幅しない。Root flags、NullAway/JSpecify/Werror、PMD/CS/SB、既業務Main/Test/SQL/電文/既goldenは不変。注釈classをstub/削除したり-Xlint:-classfile/-nowarn/-Werror解除で回避しない。実SDKの注釈解決だけであり、秘密・鍵・許可・署名・native/DBの実操作を追加しない。

独立資格: 原失敗のwarnings10/exit1と新compileのwarnings0/exit0を同じRoot flags/版/業務Main byte/sourceで対照し、実効compile classpathへ3.55.1の同JARが入ること、六module依存境界/収束を照合する。生成Mainは旧sourceの公開APIと必要byteを比較し、失敗元の未生成classは旧成功と同一扱いしない。四module全477Mainの通常compile・該当静的を先行し、API/WebのQA056該当classfile操作は回答まで保留、全六/F02/F03/451を宣言しない。PTを暗黙に起動せず、実PT/coverage/CHRと分離する。同source通常PTが必要な変更なら対象triggerと独立oracleを先に確定する。

状態:設計確定・main反映前・POM未変更・是正後compile/静的未実施。関連元F02/F03・P01808/00403/00405終了依存。元F03/2-2残2.4ppとcap5は据置き、診断/手戻りを原成果とは分離記録し、追加予算消化/工数率へ変換しない。BUG3129/YKT2600は再試験と全横展開判定までOPEN。


## SSC-450 閉SQLの実行位置をliteral操作として保持（2026-11-17）

BUG3132/YKT2603、上位RD/UI変更なし、canonical主担当/費用WBS-P019-03、F03受領。AssetStagingTables、MigrationMasterColumnVerifier、MigrationMasterConstraintVerifier、MigrationMasterContentVerifier、MigrationMasterFinalizer、MigrationMasterReferenceVerifierのprivate閉SQL表現を補足する。全SQL文字列・固定表/列/順序・実行順・timeout/fetch/setval bind・借用transaction・null/一次例外/cleanup規則・public APIは変更しない。

private stateless関数型の実装をclass初期化時に固定Listへ登録し、各executeQuery/executeUpdate/executeLargeUpdate/prepareStatement呼出位置の引数をcompile-time constantのSQL式にする。callbackはStatement/Connectionを保持せず呼出引数として借用し、一SQLごとのcallback割当や可変registry/外部SQL選択口を作らない。Assetのprivate Tableはname/columns/order文字列からprepare/targetCount/stagedCount/insertの四操作を持つ閉じた計画へ変更する。Column/Constraint各六query、Content七query、Reference六count及び全inspectionは同順の固定query操作、Finalizerは五MAX/五setval prepare/六ANALYZEの固定操作へ変更する。setvalの五事前MAX検査→全setval→全ANALYZE・constraint phase、known zero/nonnull/wasNull/row数とmetadata期待を維持する。NoCode private interfaceも物理集合に含め、除外/架空到達/SQL難読化/新suppression/flag緩和をしない。

旧承認SQL全byteと順序を一対一で照合するSource equivalenceは補助証拠とする。PT期待はproductionを呼んで生成せず、既独立Testのliteral SQL/metadata/rows/固定hash/JDBC後条件と承認SS/DDLから保持する。元Asset32・Column26・Constraint22・Content29・Finalizer30・Reference21のwhole160 Test本文/独立期待値を不変とし、必要なwhole helperをscope確定してから新sourceで一exec、Root NullAway/Werror/全静的/物理CRC-init/XML/当六sourceの未filter四counter/公開API及び不変byteを確認する。private関数型の真のNoCodeを隠さず、共通DTO等の残coverageも全componentに残す。実DB/master/原本/鍵/Backup/Root/VM/native/QA056四型/QA051 finalの保留は解除しない。

既instanceのtoString/redactionと例外診断を維持する。literal化は所有開始後のString組立を除去するが、性能やheap OOME挙動の実測合格を主張しない。追加A .4/1.2/3.6pp cap4を一回だけ計上、元F03 C2.4/SV/原見積りを保持する。元P01903/全F03/正式/ITSTの受入は別。状態:設計確定・main反映前・製造/PT未実施。
