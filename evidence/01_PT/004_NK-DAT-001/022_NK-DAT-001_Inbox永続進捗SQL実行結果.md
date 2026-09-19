# NK-DAT-001 Inbox永続進捗SQL実行結果

2026-09-20 最新確定: 正式PT-WEB-20260920-15/source13e28a71b7024777f03569bfd06392ccdfc6ec3f、06:16:15～06:28:03 JST/Maven11:47/exit0、全1572PT（Protocol80/Storage82/API689/Web313/Batch367/CHR41）、failed/error/skipped0。6Java全line/method/class/branch100%、Production5 NullAway/Enforcer/Spotless/SpotBugs未解決0、固定path3method限定review継続・coverage除外追加なし、CHR SpotBugs未設定。18collector/41scope整合・63負canary成功。DB29/266＋Batch25/281＋OPS17/142＋QST2/16＋ASY1/5＋Web7/72＝81部分成果782PT（全1572の内数）、今回再開比+157PT/+16部分成果。PG198検索結果モデル8PTを限定認定、新規障害なし。PG199検索入力はSSC072/仕様のみ。BUG195/206/YKT154/162/SSC063、実archive/親/質問受付全体/残Web・本文controller-file/readiness/Logout/QA045/実NKgateは未完了。固定加重38.25～49.75%（中心44%、約38～50%）を維持。残量42%で継続、元dev-web3file保全、PGPT/IT/ST未完了。以下は履歴。

## 1. 判定

最新正式判定: PT-WEB-20260909-25/source6dd862d0、2026-09-09 12:46:41 JST完了、全918件PASS、failed/error/skipped0、5 Java moduleの4種coverage100%、静的解析0。本仕様8 PTも全PASS。evidence/inbox-progress-sql/manifest.jsonの現行SHA-256は `a7bf9cbff8ff87cb24370a48afb901893f9e96afa13788e2390d797ab723fd3c`。8collector/23scopeの全hashとtrace負canary、V001～013/Current baseline不変、秘密pattern scanを確認。本scopeのcoverage/SQL分岐対応は同manifestと以下の個別結果へ追跡。鍵file読取/main/oneshot・親process・Question/通知参照/親chunk走査は未完了、BUG-014/SSC-049継続。

以下は探索時の履歴。正式未確定/Java接続未完了という旧記述は、上記対象sliceに限り更新済み。process/親接続の残件は維持する。

探索3（2026-09-09 11:03:43 JST完了）: 新8＋旧SQL32＋DB15＋Outbox4＋Protocol5＋Storage16=80件PASS、failed/error/skipped0、静的解析0。追加のrecord全引数/未期限・PROCESSING拒否/空ENDも確認。正式root gate/証跡は未確定。V012・PG-D-127・QA-046/SSC-049、021/PT073～080に対応。Java検査との所有transaction接続、oneshot、親process、残る参照・全cleanup監査は未完了。BUG-014/YKT-012を閉じない。

## 2. SQL条件matrix

| 対象 | Test ID / 期待結果・根拠 |
|---|---|
| open初回/既存/完了、NULL/finite/cutoff変更 | 073/076/077、初回0/NULL/未完了、再読同値、別cutoff55000、NULL/±infinity22023、既完了不変 |
| record全NULL必須引数/負count/unknown outcome/xact形式・同一性 | 076、22023・異なるTX55000、case mismatch/空/未知を拒否。cursor NULLは初回だけ正当 |
| record progress不在/cutoff不一致/cursor不一致/count不一致/既完了 | 073/074/076、55000/0変更、savepointはSQL負値のfixture隔離にだけ使用し本番所有境界の証明にしない |
| DELETED/PROTECTED/END・Message NULL形態・UUID前進 | 073/074/076、D/Pは各count+1・合計維持、Message不在/存在・期限同値/未完了を区別、PG byte順の8000…を進める、stale/同値/逆行55000 |
| END残候補/候補なし/二重END | 073/074、残候補55000、後方に候補なしだけcompleted_at設定、二重記録55000・完了readは不変 |
| DELETEと記録のcommit/rollback・記録overflow | 075/076、同TX両方確定または両方復元、Long.MAX_VALUE＋1は22003、削除後のoverflowでも全rollback、再読で二重計上なし |
| 全4CK/NN | 076/080、非有限cutoff/completed、負・不一致count、0とcursor不一致は23514、必須NULL23502、正常0/上限許容 |
| backup/state/JST日付/終了/同run、advisory/row lock | 077、成功2行以外55000、同run/別run競合55P03、backup/progress NOWAIT55P03、終了後再取得可 |
| purge400日strict±1µs/未完了/同run/調査中/lock/limit | 078、100/107だけ先に2削除、106はlock解除後1、他6保持、rollback全復元/反復0、batch履歴4不変 |
| purge各NULL/finite/limit0/1/1000/1001/backup/lock | 078、不正22023、LOCK_BUSY/BACKUP_GATEいずれも0/0/0、正常OK件数一致 |
| role/owner/search_path/UTC/PUBLIC/default privilege | 079、検査2関数/batch清掃1、base tableはbackup SELECTだけ（app default明示REVOKE）、service DML/SET ROLE不可、PUBLIC0 |
| inventory/旧history/hash | 080/旧SQL/DB、12履歴・22table・CK149/PK22/FK23/UK30/trigger1、再適用0、旧V001～011独立固定SHA不変 |

全SQL条件matrixはSQL実行と後条件で検証し、架空のJaCoCo100%としない。Java4種100%は正式root gateへ追跡する。テスト中のSQL capabilityを暗号検査成功の証明と誤認しない。

## 3. 証跡

正式run後、evidence/inbox-progress-sql/manifest.json/results.xml/checksumsへsource/branch/日時/command/exit/tool/SQL source hash/Test ID/期待・実際/QA/SSC/BUGを確定する。fixtureのciphertext/生wire/credential/dumpは保存しない。全既存scopeの再試験・hash/trace・Current baselineと旧migration不変・秘密scan確認後に更新する。IT/ST未実施。
