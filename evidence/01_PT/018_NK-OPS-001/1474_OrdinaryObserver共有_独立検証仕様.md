# OrdinaryObserver共有・独立検証仕様（実装前）

BUG1610/YKT1363、ArtemisConnectionFactoryProvider/WebBrokerContexts、NK-MSG-001/002、RD MQ001003006008/SYS004/UI231243253/SS321354・451。主WBS-P005-04、WebはP005-02共通参照追加費0。当原d48f/4184/13a7b5aeと原127/9c92e0bfを基点、普通close observerのbody重複だけを内部同値整理し、generated除外や未実行補完で100へ到達させない。PGは省略しない。

## PT_DEFAULT・範囲

OBS335は既JUnit TestID群への観点参照で、新しいJava実行件数を四件加算するものではない。展開同値はPG commit後にprivate新only proofを作り、同じcommitをgreen6722へ束縛する（proof作成でGitをdirtyにしない）。public proofは原資格後に保存する。methodの共通化でコード量は変わるが、既全127/必要全4184の独立動作oracleを変更しない。

全新旧Testのbyteを4ce赤から固定。既pg6690 driverの同127/33・compile-first・六static/全Main原資格を使う。新only green6722/original6724を割当（旧6710/6712は歴史保全・確認再演0）。VM/原本/鍵/実DB/サービス/Root/cohort/intent/permit/native資格操作0、既自己所有proxy・未接続factory・有限自己所有childだけ、126等へ欠落変更しない。

|Test ID|独立fixture/操作|期待値と根拠|
|---|---|---|
|PT-JMS-OBS335-001|API既ApiFactoryOwnershipTestの12設定各故障・直接primary/close表・same object、BrokerGraph334Testの四edge close graph|SS321十二literal/window、close1、正規raw primary/secondary又は元fatal identity、秘密/外部操作0。期待値は元既Test/1469固定で、共有policyからexpectedを作らない|
|PT-JMS-OBS335-002|Web既WebBrokerFactoryOwnershipTest/FACT334006～008の普通supplier/context/close/configure fault|元copy wipe・nk_web/mode0・固定cause-less診断・close1/成功phase再close0・元Errorの旧期待値を維持|
|PT-JMS-OBS335-003|既API/Web finite NativeRetention契約fixture|unknown true側のonUnconfirmed非帰還と外frame保持を維持、普通NoOpへ置き換えない。自己所有unconnected locator/finite childだけ、実native資格ではない|
|PT-JMS-OBS335-004|old d48 sourceと新二Mainのtoken展開同値確認|新private static final Consumer定義は各一・bodyは空/非captureだけ。Provider二/Web四の旧空lambda位置へ展開すると、コメント/空白以外の全token（literal含む）が元d48に完全一致。native選択、設定、close/通知順・他処理の変更は拒否。これは機械的source同値証拠でありPT動作expectedの生成ではない|

新PGは各moduleのprivate stateless ordinary observerを定義し、上記既定callsiteだけを参照へ変更する。関数body/呼出順は同値、Consumer identityはprivateで外へ渡されず、retained field又はconfigure cleanupへだけ使う。callback定義はclass初期化時、取得より前に準備。ordinary close failureはobserver return後に既契約で依然失敗し、正常成功に変換しない。native政策のnonreturn/capture/期限/実権限は変更0。分類5、上位仕様/oracle変更不要。

command: token同値工具→formatter/管理/pyflakes→source/Test保存pushclean→`pg6690_broker_parent_selected.py green`（新6722）→真正0後`qualify-green`（新6724）。旧testを削らず、必要な新source全体4184/643・原XML/Jar/四counter/静的/traceを当sourceで閉じる。新method countの削減自体を完成率にせず、実method miss0と同契約の全scope証拠で判断する。現在新PG/PTは未実施・未合格。
