# API consumer終端・部分close PT結果（PG474、限定）

仕様366、PG-D379、RD MQ003006008010/MON005/UI212213231251/SS312321342343/451。base HEAD7e1a10d60400e2c041f283a811bc52fa0b97ca6f上のdirty変更群。Production五classの内部同値整理/固定factory部分所有と独立新3testを同群で検証した。正式run24/1964PT53scope/48.3%は不変更、全体/実native/ITST合格ではない。

|版・command末尾|実結果|扱い|
|---|---|---|
|pg474_api_consumers_selected_v1.sh|actual1、JUnit conditional generic型推論compile拒否/API NOT_RUN|新規試験初稿のTDD compile失敗。production障害/合格加算0。|
|同v2.sh|actual0、81PT13suite/FES0/static4zero|公開経路のみ初期確認、XMLはv3前freeze未保存。私有log/hash・実終了0を保持しv3/v5成功へ流用しない。|
|同v3.sh|actual0、85PT14suite/FES0/static4zero|Question1B/1L・Sync1L不足、完了0。safe manifestを保全。|
|同v4.sh|actual1、新規normal testが存在しないQuestion.terminalFailureObservedを参照/API NOT_RUN|新test初稿、公開APIを追加せず既ready/commit後条件へ是正、失敗log保全。|
|同v5.sh|actual0、86PT14suite/FES0/static4zero/formatNullAwayWerror PASS|五class LINE/METHOD/CLASS/BRANCHすべてmiss0。開発累積execによる限定確認のみ、fresh全6/同source nativeは未受入。|

v3 manifest実SHA：`54a7bc6450a5e750ed5e9352c681ce6541451c7f33d0054fa3775ffba4573fc0`、v5実SHA：`47d76386404f87f251183ee6dc0882cabda2f9b9b2a301dc30d65f8bb41a83a1`。対象は`evidence/provisional/PG474-api-consumers-selected-{v3,v5}/manifest.json`。

PT-OPS-API-REM001→ApiConsumerRemainderTest.factoryFailureSignalsBeforeClosingAllEarlierOwnersWithFatalPriority（runtime/fatal×通知4×cleanup4）、REM002→completeProfileClosesInReverseGroupOrderAndPreservesDistinctFatalIdentity、REM003→partialConsumerCleanupFatalAndSameIdentityAreNeverNormalSuccess/syncDrainPromotesLaterErrorButAttemptsAllFourContexts＋既CORE004/007/008、REM004→ApiConsumerTerminalRemainderTest全3method、FACT001→ApiBrokerFactoryRemainderTest全2method。期待は手書きprofile・close順・例外object identity・固定wrapper・broker SQL相当queue後条件・独立offsetgolden。Production methodでexpected生成0。

実brokerの正常Questionは一件処理/commit1/queue0/ready維持。複数group fatalは業務各1・ACK0・rollback試行・不確定でも外停止1/後段業務0。protocol既終端ではprovider作成wrong-type objectを拒否fixtureとして2回処理、これはtransport受信実証へ算入0。valid業務だけ実brokerを経由し、既終端後のfatalでACK増加0/通知重複0、Question一回retryは同原電文のreal rollback/redeliveryで確認する。私有raw provider文字列の通常診断/秘密出力0。

v3/v5のfreshJUnit14suiteの署名・全case/FES・実時間・source/diff/hashはsafe manifest、元XML/coverageは私有`work/pgpt-runs/PG379/pg474-consumers-selected-{v3,v5}-frozen`700/600に保持。v1/v2/v3/v4/v5 log/exit/started/completedは同PG379各stem private、raw XML properties/log/execをGitへ出さない。

次trigger=同consumer/factory所有・例外・terminal契約の機能受入。source/test/toolsをcommit固定後`bash tools/quality/vm/050_s1/pg474_full_v1.sh <新HEAD40桁>`で451fresh全6を一回完走→同source六byte/現VM19exec実byte・原本Backup/391postL01全値/57startup保持の新generation正常code-only→実外部親/Root普通/API保持Web/Caddy/DONE/readback/ownedTERM/nativeへ継続。QA051比較のみ保留、旧a5 full/native成功を新sourceへ加算0。未解決BUG544原因・global100/正式/R4残PGPTは維持。
