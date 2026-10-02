# 通知一覧HTTP単体テスト仕様書

2026-10-03、NK-WEB-002/SCR020/PG-D347、RD FUN010/NTF001～012/AUT、UI222/224 §4/236 §8、SS313/314/323/332。NotificationSearchForm/NotificationListViewModel/NotificationController.list/NotificationMvcConfiguration/notifications/listと独立NotificationControllerTest。実装はPG436 source22b95全回帰採取後に開始し、旧Source結果を流用しない。

| Test ID | 入力・操作/fixture | 独立期待値/観点 |
|---|---|---|
| PT-NTF-HTTP001 | USER/ADMIN/0000・0200/count0・1・50 | NTSREQ64のtype0..11/from12..28/to29..45/page46..51/size52..54/reserved55..63、PAGED48/record624をUI236から手作成、全wire byte/50固定・現在actorのみ |
| PT-NTF-HTTP002 | default/type・page0/負/999999、immutable inputs | 空は未指定、closed type、page1補正、入力変異非影響/Map返却変更拒否、安全snapshot/固定redacted |
| PT-NTF-HTTP003 | 日付0001/9999/閏日、同日・366日・367日/逆順・片側/空 | 明示JST開始・終了時刻/UTC独立literal、strict実在date/年0・日付不正・datetime/suffix/offset拒否。UI366日は包含日数、To日は23:59:59.999まで |
| PT-NTF-HTTP004 | owner/username/role/context/未知/複数/空list/null key/list/element/control/Unicode page/overflow | 400相当/API未送信、roleやownerをparameterから採らない、null契約、固定issueのみ |
| PT-NTF-HTTP005 | 全result error/JMS/timeout/不正header・correlation/context/record filler | 固定HTTP分類/API0102 session Cookie終端、不正wire503/pending0/元buffer0、Error握り潰しなし |
| PT-NTF-HTTP006 | PAGED48不整合/件数/ID重複/updatedAt逆順・同時ID逆順/type-state・summary削除矛盾 | wire個別成立でも表示不整合503/要求へ修復なし、public factory各negativeも独立確認、未網羅を層の手前拒否で隠さない |
| PT-NTF-HTTP007 | 全5内部state/全3type/質問概要100 codepoint・Unicode補助/削除済み/日付JST秒 | UI224の受付通知・処理済通知・エラー通知、PROCESSINGも受付、削除済みcaption、固定明細linkだけ/手動削除0。body・response・contextをsessionへ保持しない |
| PT-NTF-HTTP008 | MVC/Thymeleaf GET HEAD/空結果・50件・末尾page補正/特殊summary | title/共通nav/Logout CSRF、escape/ownerinputなし、date/type filter保持・前後link/count・empty表示、POST未実装405/unknown owner400/API0 |
| PT-NTF-HTTP009 | 実Jetty/encrypted session両role・匿名/API0102 | 両role200/current context/GET HEAD body0/no-store、匿名302・0102後Cookie/DB終端、ADMIN他owner指定400/API0 |
| PT-NTF-HTTP010 | 8thread100独立context/UUID/filter、null/全例外/境界 | 混線0/100別MessageID/全buffer0/pending0、line/method/class/branch100%・静的6zero・strict compile/NullAway/秘密/trace。正式native/fullScopeは別未受入 |

Productionでexpectedを生成しない。scope/実行Source/日時/OS/JDK/Maven/command/終了code/FES/counter/BUG/YKT・証跡path/hashは016060/manifestへ実測後記録。質問受付第4table QA048・完成token履歴QA049/取消・native fullReadyは本参照仕様の合格へ算入しない。
