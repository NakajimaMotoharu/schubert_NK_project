# NK-OPS-001 / PG469 親完了・Log相関・通信断結果（暫定）

2026-10-06 02:22 JST。仕様346、same Production/full/frozen/signed/current=D3 `d3bba6db6eb9fec13e4847a10541cf337f575731`。管理/工具変更だけで全回帰を重複発行しない。既存fresh3301PT/489suite/F/E/S0/static6zeroを同sourceに対応付け、正式run24/1964PT/53scope・48.3%は更新しない。

| Test ID | 実結果・終了code・根拠 |
|---|---|
| PT-OPS-P469DONE001 | PASS（限定）。01:34:20.952開始、01:55:12.310761 PID1同boot/INV aabcc2c3…/job162935正常done、元30分内。observer actual0。Morning GCの零値ではなく4recordの真正journal（SHA87ab58c7672874831262e51e8c4be076311487d183c763653fb77b5198429eb6）＋単一native実行を確認。独立374/Werror0 |
| PT-OPS-P469DONE002 | PASS（限定）。readback actual0、351全14保持/361総数、既存same run成功に対する10step再開SKIPPED/count0、原本新activation DONE SUCCESS、全Backup20entry保持、45namespace/旧40byteとmetadata保持/intent0、19business table不変。app_users/version1・auth3・退役秘密保持。M/A/DB全新scope通常返却後だけ成功認定。旧timeout/UNKNOWNを成功化しない |
| PT-OPS-P469DONE003 | PASS（正常帰還部分のみ）。exec SHA07d738dc29cc2c7108d30130755d6bd41a8bc2663eb71c050edb493e17ef6062、単一session1791218061085～1791219312293、same frozen6 NoMatch0、正常540/542到達。47/543partial・全未網羅は残す。RootAPIの旧exec/別source/ordinaryWeb agent不存在を全native100へ変換しない |
| PT-OPS-P469CHR001 | PASS / actual0。01:48:01～03、DIF001/QA045のみ、artifact `program/characterization/reports/nk/PG469-native-a01-v1/artifacts/CHR-A01.json`。全CHR gateには加算しない |
| PT-OPS-P469LOG001 | OBSERVED_NOT_ACCEPTED / actual0。02:07:48～02:08:01、新source/shared Current Login→検索→ACTION Log。LOGIN_SUCCEEDED1、SCENARIO_SEARCHED1、HTTP_REQUEST_COMPLETED11。DB：同検索message IDのInbox COMPLETED/SRCREQ01/同correlation/owner、API/ACTION/INFO/閉じた2detailsとunique各1。DOM row/detail各2、page100/日時desc,id desc。QA051比較方式/名称/表示差分は未承認、baseline変更0。VIEWED/menu/log_search/outage全CHRの合格を推定しない |
| PT-OPS-P469LOG002 | PASS（通常投影）。02:09:34 actual0、同Web2006107/88e5…・同D3 INFO5、16:47Z～17:09:24Zの337local event IDs＝DB source_message_id、全投影field一致・欠落/重複0。独立17negative。生journal/DBrowはprivate600、safe集計/hashのみ公開 |
| PT-OPS-P469LOG003 | PASS（Web/Broker通信断、process停止とは別）。02:16:24 actual0、102独立assert後にuid997→127.0.0.1:61616だけ拒否。実packet counter>0、HTTP200×5/local event×5、拒否中ERROR/attempt≥1×5/DB0、finallyで当nft table削除・元空ruleset復元。通常scheduleによる復旧SENT5/DB各1、同API/Web/Caddy/Broker peer維持。broker/API process stopは未実行、CHR-L01全体未受入 |

安全manifest `evidence/provisional/PG469-parent-log-native-v1/manifest.json` SHA **0c184c9cd6aa1e3e3cda0670fb5980f277ccfd8f466b2cd5dfc5eaadeb5133c0**。actual command/source/時刻/終了code/tools hash/private artifact hash/正式・暫定区分を収録。WorkPG379の当observer/readback/native/L01/log readback/outage、Root `pg469-completed-journal-v1`・`pg469-log-network-outage-v1`等を保全。元原本/Backup/旧exec/privatecredential/Current/stash7を破棄しない。

初回SQL draftは未存在jsonb関数でexit3、Collector draftはProgram008誤pathでexit1（成果出力前）だった。どちらも合格へ算入せず、固定SQLのclosed-key検査、実Program008_NK-SCN-001への対応を是正し、新collector actual0を独立に確認。Production/SS/oracle変更はなく、新未実装の採取draftの失敗を既存機能障害とは扱わない。

BUG750/YKT527追加はnormal oneshot/Caddy terminal deadのhost独立136＋stop221まで。Root-v2のimmutable旧helperをこのhost新hashで置き換えず、新契約の全native受入は未完。source full回帰/native100/NPE/全scope正式gate・QA051/残PGPT・IT/STは不完了のまま。
