# BrokerParent334 原反例・実装・再試験

## 原127資格（2026-10-22）

元6710/session87154/source d48f8ebf8ed4047763c77fe487c44f7caa03e8f8、archive a90db3614599a6014bb8a5b4dfdb2b8f3474a5056ec85bfff0a62b5bb628bab1、UTC23:15:55.116557～23:19:02.918581、phase0,0,0/真正0、127PT/33suite/FESflaky0/六SpotBugs0/source固定。原6712/session49890も真正0、公開manifest SHA9c92e0bf1ed2ef22826e41d53f42cd6916e5e0bf07c6f472a6717dfa3908f961、private664df5bd4d1670dbca06be9c37ad102fbfb2503bdf61548ed064dde6525ae39a、findingsdc4d8a160fc5ba5f9a4b201111bc918502e6b6d0764afc324dad26a016aa45e0。全851/1667・六原Jar/XML・四outer＋nested二差/残1661同byte、PMD raw1404/processing0/CS0。現全体pending/native資格false/formalfalse。

追加nested ConsumerProfileとAsyncは元83/元127の原Jar class hashを各private physical mapへ照合、nested source完全tokenと`javap -p -c`が同一。javap output SHA各32a5886344fee9151a9c6f37a068e72f8a9fad30bbebfd93b890ff40c1f98a27・5487f779d8e0aaafb18560585cb1988bdaa1f58919654fd850abfe120118e044。単なるowner whitelistで同値を推定せずline/debug物理差と確認、機能差へ二重加点0。

四新対象のL/M/C/B missedはAPI broker11/6/0/3、provider1/2/0/1、親4/1/0/15、Web broker14/7/0/2。未測定補完0。API partialの正常close/null scratch等は既全体のApiBrokerFactoryRemainderTestが独立literal/全close順・raw primaryで確認するので、その旧Testも当source全体で実行する。old全4170を新sourceへ成功転用しない。

BUG1607/YKT1360のfixture scopeとBUG1608/YKT1361のlock finally scopeはcompile/127/原六static0の再試験で完了（修正00a1cff1a/d48f8ebf8）。BUG1604/1606・YKT1357/1359は残同source全体/品質・予防確認があるためOPEN、工程/正式/工数率は閉じない。

## green v2静的停止・必要是正（BUG1608/YKT1361）

元6702/session72103/source2d5cb53f8/archive11b6d324、UTC23:12:12.419478～23:14:25.564481はphase0,0,1真正1。実79PT/19suite/FES0、API SpotBugs一件UL_UNRELEASED_LOCK_EXCEPTION_PATHのため後続未実行・127合格ではない。原manifest/XML/static保持。915/916先行起票後、API closeのscratch clearをtry、stateLock.unlockを内finallyに限定是正。Test/期待値/残三Main不変更、抑制/除外/人工fill例外注入0。既openのcopy clearは既外finally unlock、Sync closeはmonitor、partial constructorはlockなしを横展開確認。新only green6710-v3/原6712-v3へ切替、旧6702/未着手6704は再実行しない。全体6706/原6708の前提も原6712へ更新、以下旧番号は履歴保持。

1469、PG-D499、SS321/354 SSC334、BUG1604/1606/1607・YKT1357/1359/1360。WBS-P005-03主、P005-04/P005-02共通参照追加費0。group1674の低.5/標準1.5/高4ppは固定・未較正、実N/T/専有費/工数率null。PT_DEFAULT・自己所有proxy/未接続factory/有限自己所有childだけ。実credential/DB/VM/Root/failed cohort/鍵/intent/permit/native操作0、拒否代替完了0。

## 元run・独立期待値（2026-10-22）

source4ce1521aa80d2a77920df68ee03889df6cbbdf3f、archive SHA a6c13b4e6d4eba7d48de469d68e9fb544048886e7e6c7e34dc00ebc8b9f179d8。API6698/session90779 UTC23:06:27.211805～23:09:44.820967、Web6700/session11249 UTC23:06:29.045576～23:10:13.131789。両phase0,0,1/真正1、API11PT/6suite F5・後続not-run6、Web13PT/6suite F3・後続not-run2。全八予定反例の専用assertionは元XML完全一致、失敗/未実行をPASSへ算入0。readerは再実行PT0/終了0。

公開原manifest:

- evidence/provisional/PG6698-broker-api-original-red-v2/manifest.json SHA e0615c853320c73f702c8061d448682319ce34b9700a8df8a504844611b14af5
- evidence/provisional/PG6700-broker-web-original-red-v2/manifest.json SHA 2fdac77b315f9c903c1d9a25db479e4fc9b0bdb1e7a7aa5174771c07bb454957

期待値は1469の事前固定Error identity・role/mode/setting/catalog literal・close順/回数・wipe表。provider diagnosticsからexpected生成0。新三Test SHA1f041abc/e450d657/5ab0f744と全旧Test byteを赤から固定。旧6690/6692のcompile停止は別source4ba/archive11cc・0PTで保全、当八反例へ加算0。

## PGと別パス点検

当d48fの別経路sourceレビュー（実行PT/拒否代替ではない）:

- RB334-01: API三slot/owner listと親三group/stateは取得前準備、partialの未返却providerはprovider自身のconfigureOwned責務、返却後はreverse owned closeへ記録する。最初の取得失敗を取得済みと扱わない。
- RB334-02: API/WebのstateLockはsupplier/createContext/stop/closeを直列化。scratchはprivateでclose lock内だけ使用、clear異常でも内finally unlock（1608）。context利用期間自体は外側がconsumer→broker順に止める既責務であり、新たなborrow期限/再取得権限を作らない。
- RB334-03: 親groupsはprivate、追加されるSync/WebLog/Questionは実final child。普通の非Error closeは新しい固定cause wrapper、Errorは直接という契約なので親final guardで全保持graphへ到達する。反射で到達不能NoSupp groupを作らず、直接Error優先表は従来どおり。他のgroup失敗でも全試行・成功phase再close0を維持する。
- RB334-04: 原startup primary/通知/非Error cleanup causeを別参照で持ち、全必要close後にだけ分類。native onUnconfirmedが非帰還ならそのままUNKNOWN、捕捉して正常returnへ変えない。openのguardがErrorをthrowしてもcopy取得済みなら既finally wipe・外finally unlock、未取得copyやcaller factoryを勝手に消去/closeしない。新catalog/公開JSON/logへprivate graphを追加しない。

四点はSS321/354と実class/取得・帰還順からの点検であり、実VM所有・native資格・新source全体PASS/global100の証拠ではない。後者は1471元終端/原資格/実counter待ち、ptAlternativeCompletedは0のまま。

四Main/PG-D499のみ。標準suppressionでprimary identityとreverse個別secondaryを維持するraw factory境界、fixed cause-less redaction前のfinal guardを区別。全closeより前にgraph accessorを呼ばない。直接Errorの既優先表→正常returnしたUNKNOWN callback→graph分類、scratch finally clear、createContext finally wipe、成功owner再close0をsource順から再点検。親groupは実公開childの固定cause carrierに限定し、届かないNoSupp groupを反射で作らない。実UNKNOWN非帰還を復旧済みとせず、実資源保留解除0。format32741終了0・Test差0。

次commandは同driver green（新only6702/宣言127PT33suite）→元真正0後qualify-green（6704）。全851source/1667physical・六Jar/XML・四counter・静的の実数を記録し、必要同source全体/横展開完了前に全閉鎖しない。現在green未実施/合格未認定。旧f16f全4170/903b83・各native/traceを新sourceへ転用0。
