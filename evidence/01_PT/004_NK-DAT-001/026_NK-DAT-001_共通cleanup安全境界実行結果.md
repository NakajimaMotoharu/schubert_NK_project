# NK-DAT-001 共通cleanup安全境界実行結果

2026-09-20 最新確定: 正式PT-WEB-20260920-16/source0039a6ef78df48432cebbc32d7ba86ea07f24234、06:32:13～06:43:57 JST/Maven11:42/exit0、全1580PT（Protocol80/Storage82/API689/Web321/Batch367/CHR41）、failed/error/skipped0。6Java全line/method/class/branch100%、Production5 NullAway/Enforcer/Spotless/SpotBugs未解決0、固定path3method限定review継続・coverage除外追加なし、CHR SpotBugs未設定。18collector/41scope整合・64負canary成功。DB29/266＋Batch25/281＋OPS17/142＋QST2/16＋ASY1/5＋Web8/80＝82部分成果790PT（全1580の内数）、今回再開比+165PT/+17部分成果。PG199検索入力8PTを限定認定・SSC072入力境界完了、新規障害なし。PG200検索画面状態は仕様のみ。BUG195/206/YKT154/162/SSC063、実archive/親/質問受付全体/残Web・本文controller-file/readiness/Logout/QA045/実NKgateは未完了。固定加重38.25～49.75%（中心44%、約38～50%）を維持。残量40%で継続、元dev-web3file保全、PGPT/IT/ST未完了。以下は履歴。

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
