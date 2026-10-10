# 当fresh Backup・Log/session独立仕様/実行結果

Program=NK-OPS-001、対象=MorningBackupArtifacts/Morning session cleanup/Web Log Outbox/SessionCiphertext、工具1263～1270。RD FUN-008/MON-003/AUT-001、UI232/235、SS314/324/341/343/351/352。WBS-N01/P006-05、QA051最終比較は保留。

当ProductionD5/PG1068/schema028のみ、pre-Root57a588…と正規停止after7b48…/Root run9f651096/cutoff20:03:22.718197Zをjoinする。既Root/Backup/stop/nativeを再発行しない。証跡は [公開manifest](evidence/provisional/PG1264-1270-fresh-business/manifest.json)、raw journal/key/DB/dumpは私有保全のみ。環境・command/operator source/日時/exit/hashはmanifestでTestID別一意。

| Test ID | fixture/操作・独立期待値 | 実結果 |
|---|---|---|
| PT-OPS-PG1264-001 | Backup固定4file/NKBACKUP1 canonical、3archive size/SHA、完全DB二handle・SUCCESS/errornull/attempt/count/byte、SS343固定8host config byte/owner/gid/mode。signed effective profileはexact signature authority、YAML4は登録templateでhost実byteの署名ではない、env3は外部入力。通常Backup UIDでpg_restore --listのみ、restore禁止 | actual0、3archive16306893byte、configuration step61640byte、8member一致、signed effective1/登録template4/env3、dump-list0。all24/full32/187/原本/資源後条件維持 |
| PT-OPS-PG1270-001 | Current Web INV4236e5a9のREQUEST222と追加DB/outbox222をUUIDで一意join。SS2336byteのliteral offset/header/padding/NFC/byte・Python AESGCM/tag/keyversion/AAD、GET/login200/匿名actor/件数/日時/lease無し/SENT、DB/localdetails/elapsedを独立照合。生wire/鍵をexportしない | actual0、wire/DB/local222・SENT222、duplicate identity/nonce0、全24-full32-current署名187及び二読journal allfield/cursor/event順一致。外部fixture request総数unknownのため要求完全性/QA051 final比較は未受入 |
| PT-OPS-PG1270-002 | pre-Root expires<=元cutoffで削除対象を独立選択、その他旧rowは全field保持。新session AESGCM/AAD/NKENC1・formatVersion2/CSRF64hex/empty operationTokens/maxInactive28800・8h expiry・unique nonce。消去対象を現在DBから逆算しない | actual0、独立期限削除1018/旧保持224/新匿名暗号session222。oracle内部のsynthetic viewは保持不変検査だけで、実DBへ旧削除rowを復元しない |

正常/期限境界/未知name・不足登録/identity/mode/byte/hash/null/別source/旧SHA/余剰欄/旧row改変・recreate/duplicate/件数不一致/暗号tag/key/AAD/envelope/JSON欄/nonce/Ref途中例外・close順/全journalfield・cursor・event順の負例を工具独立fixtureで実実行。1270実生成namespaceも同じpure関数を実呼出した。Toolsの選択13+従来独立codec等16は工具PTでありProduction3563PTへ加算しない。source変更なし・不要な全回帰反復0、coverage四100は依然未達。

修正前失敗1260/1262/1266/1268/1269は各actual1のまま保全し、合格件数に算入しない。BUG1069～1072/YKT838～841は署名素材責務/実schema/sourceauthority/metadata Ref寿命/journal意味同値の原因scopeのみ新独立host及び実VMで閉鎖。restore/世代prune/credential復号内容/Log network outage・再送競合/外部request総数/QA051 finalL01/全coverage/正式451は別残件。IT/ST完了ではない。
