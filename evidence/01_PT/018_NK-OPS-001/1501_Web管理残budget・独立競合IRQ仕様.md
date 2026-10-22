# Web管理残budget・独立競合IRQ仕様

設計先行公開済：source0a714c09a/PR200→main1077f8cd5a9a6a33cd7f3d669b1cd62d132275ac、二SS/914だけを通常merge/fetch確認。PG/PT・実環境/正式の受入ではない。添付APIはcap100で一回失敗、再試行や既添付削除0。実declarationは新三methodを含む**42/15**、旧data束23と既Web16＋新競合三であり、全回帰ではない。

初回6850/session53283/sourcec223ef32860db77c400ef41146dc3e88c23e361cはarchive20b2854c8385e4bbde5f3d4e9cb7fc872a6b8e28f55bbc437eb5848556732940、UTC06:22:27.358792～06:23:16.917578、phase0,1/actual1・Production0/0。新Testのpromoteへboolean literalを返すlambdaを渡したcompile不備で、旧Main反例を再現したとは扱わない。BUG1628/YKT1381を修正前起票し、Web固有Runnableへvoid通知counterを渡す形へ是正。Testの独立期待値/旧Main/既oracleを変えず、新onlypg6856-web-deadline-red-v2で未実行だった実PTを行う。旧6850 namespace/失敗証跡を上書きせず、v2 Testをgreenまで固定する。

是正後local smokeはJAVA_HOME=toolchain/jdk-25.0.4、Maven3.9.12 `-q -o -Dmaven.repo.local=.../m2/repository -DskipTests -pl src/schubert-nk-web -am test-compile`、session38270 actual0（Production PT0、単なるcompile）。format/管理二/工具pyflakes0。旧6850の公開compile failure manifestへ元SHA7a853667/旧Test6373de8eを保存し、成功/反例へ正常化しない。新6856はまだ未発行。

履歴訂正：上記「Runnable」はvoid-SAMというjavac診断の説明誤称。既WebはServiceStartupAdmission.Ready.release（void/IOException）で、元Web試験はpromotion拒否をIOExceptionとする。6856-v2/source74e18a07ca069d2f09f9c09c1f3fd598397a903c/session93594はphase0,0,1・実29/9・新三失敗・batch13/6未実行、source固定/archive60a21965。第一/第二はsecond.get line122のTimeout、第三は新TestがIllegalStateを誤期待したcleanupのunexpected IOException（line136）で、BUG1629/YKT1382へ修正前起票する。Mainや旧oracleを変えず、新Testを既IOException/fixed message/通知0へ整合する。

反例v3は新onlypg6856-web-deadline-red-v3、六guard12/7＋新Web三/1=15/8へ限定し、無関係な旧domainの再演を省く（greenは全関連42/15）。期待値変更で旧MainをPASS化せず、旧Mainのまま三件の第一owner保持liveness違反を再確認し、そのTest bytesをgreenへ固定する。旧v1compile/旧v2oracle失敗は別に保全する。

BUG1627/YKT1380/SSC335/PG-D509、P018-06。群開始低.3/標準1/高3週次共有pp、fresh最後81/残19/reset1793082865、開始見積りを固定。K01必要全体費は別に開始前記録し二重計上しない。原/v4/実費N/Tnull/正式1964-53/17-190/工数nullを維持。

## PG契約と範囲

SS342のWeb graceful phase30秒・SS352既確認phaseと同deadline、UI251のWeb停止上限を内部managementへ接続する。現Mainの無期限lock待ちとjoin元Duration再使用を点検で発見、実VM障害とは区別。SS335を342/354へ先行補足し、design-only main反映後、旧Mainで有限反例→同Test固定のPG是正→旧domainを合わせた通常PTを行う。

**PT_DEFAULT**：新Testだけが所有するephemeral loopback HttpServerとそのexecutor、fixture latches、有限worker二つ。既許可LAN builderの新only namespaceで実行。通常get/info業務起動/VM/Root/回収/原本DBBackup/credential/permit/Unit/権限/実native操作は0。実provider停止ではなく、自己所有JDK serverを保持するfixtureがstop内を有限latchで一時待機するだけ。拒否を探る試験/代替ではない。

Input検証0..30秒・旧HTTP/例外/stop成功cache・未起動UNKNOWN・Web既IRQ表を固定。新同nano deadlineをlock/joinへ適用する。preIRQはlock待ちだけclearし、JDK stopより前に復元、旧awaitのIRQ不確定と全出口flag復元を保持する。APIとは異なるため、共通helperへ無理に統合しない。vendor stop自身の強制時間制限/強制killは追加せず、非帰還の残存リスク/既Unit・親budgetを保持する。

## 独立試験

| Test ID | fixture/input/操作 | 期待値と独立根拠 |
|---|---|---|
| PT-WEB-MGMT335001 | 正常start済みのowned server。第一closeをstop入口latchで保持、第二closeWithin(Duration.ZERO)を別workerで呼ぶ | 第一を解放する前に固定IOExceptionで帰還、cause/suppressedなし、stop呼出一回・ready false。0budgetはlockを無期限待ちにしない。最後は第一を解放し実stop/join・同port再bind確認 |
| PT-WEB-MGMT335002 | 第一を同様に保持、第二は正budgetで実lock待機に入り、その自己所有workerへinterrupt | 第一解放前に固定IOException、呼出workerのIRQflag true、stop追加0・closed成功化0。取得後IRQの旧表は既Testを維持 |
| PT-WEB-MGMT335003 | 第一workerの正常startをfixture内で保持しstopLockを所有、第二workerは入場前からinterrupt、零budgetで競合close | 元flagを保持した固定未確認帰還、stop未取得発行0。第一startを解放後もlate promotion拒否、最後に正規close/socket解放。停止要求をlock前へ置く根拠を別phaseでも確認 |

workerのliveness待ちは独立上限（数秒）とし、vendor latchには独立有限watchdogを置く。全finallyでfixture自身を解放して当Future/worker/executorを回収し、旧反例の失敗を資源漏れ成功へ読み替えない。private fieldやJDK内部reflectionによるstate偽装はしない。期待値はIOException型/固定literal/整数counter・IRQboolean・held latchと実socket再bindで作り、Productionのmethodで生成しない。

新三methodの予定は実declarationで確認する。既data新3/元23、既Web全suiteと六guardを束に含め、同じ入力を旧source反例と是正後へ使う。旧全oracle/他Main/gatesを変更しない。必要原XML/Jar/Main差・同source四counter・静的全raw分類・SQL/JVM・traceを別に確認し、前回Main同一のdata-only結果を新Web Main/global coverageへ移植しない。PG/PT未実施段階で合格/coverage/leafを増やさない。
