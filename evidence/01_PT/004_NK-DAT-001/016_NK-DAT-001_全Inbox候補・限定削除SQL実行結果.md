# NK-DAT-001 全Inbox候補・限定削除SQL実行結果

2026-09-20 最新確定: dev-foundation/source 0ca3aa9588fa480ccf4b3e4ff06561f627365e66、正式PT-WEB-20260919-02（09-19 23:58:54～09-20 00:14:59 JST）、全1455件（Protocol80/Storage74/API660/Web241/Batch359/CHR41）PASS、failed/error/skipped0。実装済み6 Java moduleのline/method/class/branch100%、Production5 moduleのNullAway/Enforcer/Spotless/SpotBugs未解決0。固定/etc・/run・/varの3 method限定静的レビューを維持しcoverage除外なし、CHR runnerのSpotBugsは未設定。15collector/38scopeの同run/source/branch/hashと46負canary成功。DB29部品266＋batch24部品273＋OPS15部品126＝68部分成果665 PT（全1455の内数）。PG175～177のroot manifest新規公開・directory公開・bundle耐久化/元inode照合を認定し、今回9月19日再開比+40 PT/+3部分成果。BUG199～204/YKT158～160/SSC064～066完了。BUG195/YKT154/SSC063のSQL等、実dump・tar・age/7世代・親実子制御/全cleanup接続/通常Question writer/replay/Logout RERUN001/QA045は残る。固定加重約4割（35～50%、456）を維持。実NK CHR/IT/ST完了とはしない。利用枠残91%で継続、元dev-web3file保全。PG178は仕様のみで未認定。以下は履歴。

最新正式判定: PT-WEB-20260909-25/source6dd862d0、2026-09-09 12:46:41 JST完了、全918件PASS、failed/error/skipped0、5 Java moduleの4種coverage100%、静的解析0。本仕様8 PTも全PASS。evidence/full-inbox-sql/manifest.jsonの現行SHA-256は `61622856868d28ab62bcfe5ad2a592034d63eb48678a7331ae19cb4d4d99b15f`。8collector/23scopeの全hashとtrace負canary、V001～013/Current baseline不変、秘密pattern scanを確認。本scopeのcoverage/SQL分岐対応は同manifestと以下の個別結果へ追跡。鍵file読取/main/oneshot・親process・Question/通知参照/親chunk走査は未完了、BUG-014/SSC-049継続。

以下は初回・探索・旧正式runの履歴。旧hashは証跡commit d98961c6等の該当履歴を参照し、現行manifestのhashと混同しない。未確定という旧記述は本段落の対象sliceに限って更新済み。

## 1. 現在の判定

V010/PG-D-124、015仕様PT-DB-INBOX-049～056。探索3で追加8件と関連68件=76件PASS、failed/error/skipped0。正式全reactorとsanitized証跡確定は未実施であり本slice完了とは扱わない。Java全候補検査削除接続/Question・通知参照/全run/oneshot/V006置換は未完了、BUG-014継続。SQLだけで暗号整合証明を提供しない。

## 2. SQL分岐・条件matrix

| SQL対象・条件 | 対応Test ID / 独立後条件 |
|---|---|
| helper NULL run/cutoff/±infinity | 053 / 22023。公開候補からhelperへ伝播、helper直接EXECUTEは049で42501 |
| helper advisory取得成功/競合 | 051/055 / 正常進行または観測した55P03、再試行は別transaction |
| helper backup集合なし/片側/状態/日付/run/ended_at | 055 / SUCCESS両側だけ通過。他4合法状態は55000、ERRORはDDL23514の別negative |
| helper locked snapshot途中追加 | 055 / 候補/削除それぞれでDB行lock待ちを観測後CONFIG追加、当該queryは55000、次transactionは両側lock後成功 |
| 候補FOUND/なし、cursor NULL/一致/後方、state/expiry/未知 | 050 / UUID1件順、期限同値/未来/PROCESSINGを除外。未知も返却し削除false、残5行不変 |
| 候補参照AUTH_SESSION/USER/SCENARIO_FILE/その他/不存在 | 051/054 / 対象3種の実在行はFOR SHARE、別connectionの対象更新55P03・非対象更新成功、終了後解除。不在は候補返却だけ |
| 削除引数NULL/非decimal長さ/hash31・32・33/非有限 | 053 / 不正22023、正当入力次段階へ。異なるMessage/hash/xactはfalse |
| 削除canonical/state/version/owner/token/ref | 051/053 / 24route×NONE含む6参照型、正当形態だけ可。7未実装応答/未知route保持。隔離admin rollback-onlyで制約を一時外しSQLのowner/token/NULL/参照数値範囲/state独立拒否も確認 |
| 削除日時/最短保持/cutoff | 052/053 / 全24routeで24hまたは168hの±1µs、未達/非有限/順序不正/同cutoff保持、正当期限削除1 |
| DELETE FOUND/再走/rollback/同run | 050/051/052/056 / 1削除true、既削除false、rollback1復元。User/script/session/backupを削除しない |
| 関数/列/owner/role境界 | 049 / 2公開functionだけ検査role EXECUTE、helper不可、User2列/Scenario2列だけSELECT。password/その他列/直接Inbox/Web/任意DML/DDL/SET ROLE/他role呼出し42501 |
| migration履歴 | 056/既存DB15/旧SQL16 / V001～010の承認10履歴・再適用0、V001～009の独立固定SHA9件不変、旧認証候補/削除と168h契約維持 |

SQLへ架空のJaCoCo coverage値を付けない。Java4種100%と静的解析は正式reactorで改めて確認する。

## 3. 障害と証跡予定

BUG-087/YKT-078: batch状態をERRORとしたfixtureを、DDLのRUNNING/SUCCESS/WARNING/FAILED/SKIPPED全5状態へ修正し、ERRORは意図的23514 canaryとして別検査。既存候補/削除fixtureのFAILEDは非該当。

BUG-088/YKT-079: 並行migration count2箇所の9/9L残存を、production SQLから生成しない承認version literal一覧MIGRATION_VERSIONSへ集約。通常/並行の実行件数・history、全version/resource inventory、旧SQL2と新SQL1の10履歴を全て再試験した。旧SQL9ファイルのhash oracleは変更しない。

実行日時/branch/source/command/exit/環境/各Test ID/期待根拠/actual/SQL matrix/BUG/SSCは正式run後のevidence/full-inbox-sql/manifest.json、results.xml、checksumsへ確定する。生ciphertext/credential/DB dumpは格納しない。IT/ST未実施。
