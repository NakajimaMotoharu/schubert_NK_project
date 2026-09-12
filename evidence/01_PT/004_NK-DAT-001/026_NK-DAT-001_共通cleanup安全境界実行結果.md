# NK-DAT-001 共通cleanup安全境界実行結果

2026-09-12 最新確定: dev-foundation/source 194667c104b091e2f303805b1a908602bbe52319、正式PT-WEB-20260912-03（21:44:36～21:52:02 JST）、全1133件（Protocol80/Storage58/API634/Web241/Batch79/CHR41）PASS、failed/error/skipped0。実装済み6 Java moduleのline/method/class/branch100%、Production5 moduleのNullAway/Enforcer/Spotless/SpotBugs未解決0。固定/runの限定静的レビュー1件は維持しcoverage除外なし、CHR runnerのSpotBugsは未設定。12collector/35scopeの同run/source/branch/hashと17負canary成功。DB26部品240＋batch3部品37＋OPS9部品66＝38部分成果343 PT（全1133の内数）、今回private0600/非上書き公開の低位能力8件を追加しBUG150/YKT116再試験完了。PG154/run環境publisher12件は仕様のみで未合格。親制御/backup artifact/設定publish/SSC055原本・全cleanup caller・通常Question writer/replay・Logout RERUN001・QA045は残る。固定加重約4割（35～50%、456）を維持、残件は460。実NK CHR/IT/ST完了とはしない。利用枠残94%でPG/PT継続中、元dev-web3file保全。以下は履歴。

最新正式判定: PT-WEB-20260909-25/source6dd862d0、2026-09-09 12:46:41 JST完了、全918件PASS、failed/error/skipped0、5 Java moduleの4種coverage100%、静的解析0。本仕様8 PTも全PASS。evidence/cleanup-safety/manifest.jsonの現行SHA-256は `3c30e77bee724bb00472eda911646c5552202ac65ff473be9feb1cc716475ff7`。8collector/23scopeの全hashとtrace負canary、V001～013/Current baseline不変、秘密pattern scanを確認。本scopeのcoverage/SQL分岐対応は同manifestと以下の個別結果へ追跡。鍵file読取/main/oneshot・親process・Question/通知参照/親chunk走査は未完了、BUG-014/SSC-049継続。

以下は探索時の履歴。正式未確定という記述は本sliceに限り上記で更新済み。

025/PT-DB-INBOX-089～096、PG-D-129、SSC-050、BUG-092～095・YKT-083～086に対応する。最新正式run21/878件はこの新sliceを含まない。正式root gate/19scope収集が揃うまで完了へ算入しない。

## 1. 探索履歴

探索1 /tmp/pgpt-cleanup-safety-explore-1.log: 84件中82成功・新2error（BUG-094不存在API role、BUG-095禁止tableをbatchへ読ませたtest）。SQL gate/保持と旧V006反例の新6件・旧40SQL/DB15/依存21は成功だが非合格。5df29fcaで修正前起票しroleをschubert_appへ一致、実pg_roles存在・42501・admin観測を追加。権限を増やしてtestに合わせていない。

## 2. SQL条件と独立後条件

探索2 /tmp/pgpt-cleanup-safety-explore-2.log、2026-09-09 11:38:11 JST完了、52.232秒、exit0。新8/旧SQL40/DB15/Protocol5/Storage16=84件PASS、failed/error/skipped0、NullAway/Spotless PASS、SpotBugs0。正式root未確定のためslice完了は保留。

| Test ID | 実行する条件・後条件 |
|---|---|
| 089 | 全7関数×backup2 step×9変異（4非SUCCESS/前日/翌日/終了NULL/別run/欠落）=126拒否、batch row前後hash不変。旧V0065関数は前日・終了NULLでもOKを返す反例をrollback隔離で再現、現行全7はBACKUP_GATE |
| 090 | 全7で他connection advisoryはLOCK_BUSY、成功chunk中backup2row NOWAIT55P03、終了後2row lock可。各関数でsnapshot取得後に不足CONFIGを追加しても当該呼出しはBACKUP_GATE、次はOK |
| 091 | 全7×NULL/run/cutoff/limit/±infinity/0/max+1/int端は22023、3 session timezoneとUTC±offset同時刻はOK、JST日境界の前日はBACKUP_GATE、1/max範囲成功 |
| 092 | 実在5 forbidden roleから実呼出し42501、batch EXECUTEだけ、owner/definer/path/UTC exact、PUBLICなし。UTC改変/余分設定negative、13履歴・再適用0、V012固定SHA（旧V001～011は前5SQL PT固定hash） |
| 093 | log1 lock中に2だけcandidate削除1、batch直接SELECT42501、全rollback後1/2両方保持。limit1もrollback、P0001 triggerは伝播し全行保持、除去後2削除commit/再実行0 |
| 094 | Notification物理状態ACCEPTED/PROCESSING/COMPLETED/ERROR/CANCELLED×5日時。期待候補7だけ削除、残18/関連question18・job18保持、削除flagなし/同値/未来保持。API/IP/Web各期限±1μsと2→3→1共有chunk後各1有効保持。revoke/locked_until±1μs、古いlockでも有効windowなら保持 |
| 095 | log90日strict±1μs/同値/未来、hold NULL/期限前/同値/後。4target/3delete/1skip、残2/3/4/7。再実行保護1skip、rollback7復元。時刻順limit2は5/6だけ削除。旧SQLは最近2/3と保護7まで削除する6/6/0反例 |
| 096 | ended_at400日strict±1μs、開始古いが終了最近/終了NULL/現在run/同runRUNNING・FAILED調査を保護。limit2は110/111、次101、残102～109/112。旧SQLは開始/任意閾値で9件誤削除する反例 |

## 3. 正式証跡・未完了範囲

正式runの日時/対象commit/branch/OS/JDK/tool/command/exit/各Test ID/input・expected・actual/SQL source/hash・Java全coverage/BUG/SSCはevidence/cleanup-safety/manifest.json/results.xml/checksumsへ確定する。全8collector/19scopeのhash・相対trace・負canary、Current baseline/旧V001～012不変、秘密scanを確認する。sanitized resultのみGitへ格納し、秘密/本文/ciphertext/dumpは保存しない。

SQLは上表の条件matrixでありJaCoCo100%と偽称しない。親の実backup/OS lock、oneshot、log保護行を含む全chunk cursor、pending revoke/全domainは別未完了。BUG-014/YKT-012の全件完了や実NK CHR/IT/ST合格を意味しない。
