# API consumer終端・部分close PT結果（PG474、限定）

追記（2026-10-06 10:39、BUG762/YKT542）：sourceabdb6f35a008f7e92f189ba7488856cf7c0ddc57のfull-v1/session50225はactual0/3365PT505suite/FES0/static6zeroで17:22min完走。しかしfresh Sync callback normal rollback line80/83が2line未網羅でcollector54024 actual1、五class全100/機能受入へ算入しない。初回六targetは私有pg474-hostへfreezeして保持し、safe PG474-full-v1-coverage-refused SHAdc7b67c0b3b026c0b871998c995557881583cc85300a2e72222d6f3752b14e06。v5の「全miss0」は開発累積限定という原記録のまま、fresh gate拒否を上書き0。

修正前BUG762/YKT542起票→normal-fatal/uncertain-fatal/protocol-first三独立brokerをREM004へ保持。v6/session9256 actual0/86PT14suite/FES0/static4zero/五class四counter0、safe SHA231af8d36074f66da440a7d1004e0147f7d1d9ed4b88c058b7a58ae7954427d5。Production main変更0、型/例外/ACK/再送契約変更0。v6も累積限定のためBUG/YKTの完了は新source fresh全6-v2で全対象四counter0と全実XML/static/byte/sourceを確認した後だけ。次command=`bash tools/quality/vm/050_s1/pg474_full_v2.sh <修正保存HEAD40桁>`→`python3 -B tools/quality/vm/050_s1/pg474_collect_full_v1.py v2`。原fullv1のfrozen/失敗collectorと新v2のsource/frozenを分け、新candidateはv2 source/byteだけを使用する。

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

次trigger=同consumer/factory所有・例外・terminal契約の機能受入。source/test/toolsをcommit固定後`bash tools/quality/vm/050_s1/pg474_full_v1.sh <新HEAD40桁>`で451fresh全6を一回完走→同source六byte/現VM17exec＋2私有診断heapの実byte・原本Backup/391postL01全値/57startup保持の新generation正常code-only→実外部親/Root普通/API保持Web/Caddy/DONE/readback/ownedTERM/nativeへ継続。19は全file数（10:17実観測で分類確定）でありheapをcoverage入力へ算入しない。QA051比較のみ保留、旧a5 full/native成功を新sourceへ加算0。未解決BUG544原因・global100/正式/R4残PGPTは維持。
