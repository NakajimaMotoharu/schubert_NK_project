# Web例外finally補足の独立PT仕様

EXEC325002/WebRuntimePendingFailureRetentionTest、SS313342354/SSC325、PG-D479/BUG1578/YKT1320、1381。javacはfinallyを正常帰還/保留例外伝播の二経路へ複製する。当一Mainは既25/6400で資格済みだが、正常startup後UNKNOWN九入力だけで後者の全実行を認定しない。これは同じ仕様の内部PT詳細補足で、業務/設計oracleを変更しない。原red/green Test d0767c10も変更しない。

## 独立入力・期待値

自己所有最小childのdummy callbackだけで次の三vectorを実行する。1=start LifecycleException＋close IOException＋診断Error、2=await Error＋close RTE＋診断RTE、3=start IOException＋close Error＋診断通常。期待はstart/stop/close/固定診断各一回、awaitはvector2だけ一回/他0、再close0・escaped0・外側finally0、保持thread生存を1200ms後/割込後1200msで確認する。入力の例外型・callback順序/回数は明示constantから作り、expectedをProductionの戻りから生成しない。既通常/null/原例外identityは関連既二Testで維持する。

空env/TempDir出力・同run JaCoCo agent引継ぎ、child20秒wait/超過時はそのProcess handleだけ終了。daemonは不活性dummyのみでDB/JMS/Web/VM/Root/鍵/Unit/intent/permit操作0、子の終了は実native解放証明ではない。PT_DEFAULT、拒否境界探索でも旧保留操作の再試行でもない。

## 実行・閉鎖条件

Production Mainはd319と全byte同一。新Test一件のみ追加・正規format元5756終了0、actual宣言26/12（元25を算術PASS加算せず、新sourceの全関連XMLを実行する）。元25/6400/原JVM classhashを前提に、保存pushclean後 `python3 -B tools/quality/pg6412_web_frame_pending_selected.py` 新only一回→元真正0後6414原全8511667/六Jar/全XML/actual raw counter/静的を照合する。source/run/command/時刻/OS/JDK/exit/input/expected/actual/coverage/BUG/hashを原begin/manifestへ保持。現在未実行、準備二工具＋raw availability四工具0はProduction加点0。

共通selected報告はBUG1580修正により欠落counterを追加せず、BRANCH欠落を100%としない。原JVMの全method（private空constructorを含む四）に条件/switchが無ければclasshash/sourceとbranch適用性を明示し、二finallyの各五fence/診断/close catch/元callback保持と、この補足を含む実例外PTを独立にjoinする。sourceDataや除外設定/期待値の緩和は禁止。必要全体は二新@Test/二Testclassを一campaignにまとめ、現時点の予定4054/610/1667を実宣言で再確認してから発行する。中間4053全体は未発行であり反復しない。

元25/source d319、旧4052/sourcec341、次26/次全体はそれぞれsource/runで分離し、旧native/coverageを合成しない。元6396失敗、BUG1580追記訂正と歴史tool横展開OPENを保持。正式1964/53・17/190・工数null/QA051final/PTALT不明代替0・実環境HOLD/全保全は不変更。群開始.5/1.5/4pp/原-v4不変、補足PT/工具是正/再認証を分けて専有費/N-T不明はnull、通常小群/commitで停止しない。
