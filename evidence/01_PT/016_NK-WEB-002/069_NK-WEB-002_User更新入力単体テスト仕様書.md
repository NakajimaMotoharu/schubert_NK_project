# User更新入力単体テスト仕様書

2026-10-03、NK-WEB-002/NK-AUT-001/SCR017、RD FUN009/AUT002003、UI225 §5/236 §6、SS313314323332、PG-D353。UserStatusForm/UserRoleForm/PasswordResetForm/UserUnlockFormのbind/isValid/getIssues/displayValues/toRequestとpassword close、package内四操作閉binding。

| Test ID | fixture・入力・操作 | 独立期待値・根拠 |
|---|---|---|
| PT-USER-CHANGE001 | STATUS true/false、ID1/N12最大、version0/N9最大 | 手書きUST60: ID0/12、flag12/1、version13/9、UUID22/36、Reserved58/2。全byte比較 |
| PT-USER-CHANGE002 | ROLE USER/ADMIN、同境界 | URL68: ID0/12、role12/5、version17/9、UUID26/36、Reserved62/6 |
| PT-USER-CHANGE003 | UNLOCK、同境界 | ULK60: ID0/12、version12/9、UUID21/36、Reserved57/3 |
| PT-USER-CHANGE004 | PASSWORD、trusted target username、NFC | UPW324: ID0/12、password12/256、version268/9、UUID277/36、Reserved313/11。確認はwireへ送らず手書きgolden |
| PT-USER-CHANGE005 | 各操作欠落/未知/他操作/重複、未知owner/username/role入力 | closed exact field/operation、HTTPでtarget/role/context権限を上書きせず無効toRequest拒否 |
| PT-USER-CHANGE006 | path ID0/負/N12超過、hidden id不一致/欠落/非ASCII/plus/overflow | path invariant/field errorを分け、positive N12一致のみ、APIは別の本人/ADMIN/current認可 |
| PT-USER-CHANGE007 | version0/999999999/負/超過/plus/指数/非ASCII/空 | ASCII N9、0はformatとして受入・optimistic conflictはAPI、切捨て0 |
| PT-USER-CHANGE008 | confirm欠落/false/on/TRUE/重複、token形式境界 | 確認trueだけ、canonical UUID小文字36のみ、nil形式だけではsession用途権限にならない |
| PT-USER-CHANGE009 | enabled/role欠落/空/不明/重複 | 固定truefalse/USERADMINだけ、Role/String回復や未知default受入なし |
| PT-USER-CHANGE010 | password codepoint12/128、UTF8256、NFC確認 | UI225同policy、末尾ASCII space/control/不正Unicode禁止、HTTP usernameをtrusted値として使用0 |
| PT-USER-CHANGE011 | password11/129、257byte、trusted username同一大小文字、確認不一致 | field error/password再表示0/invalid request0、秘密診断0 |
| PT-USER-CHANGE012 | map/key/list/要素null、各必須欠落/空list | null fail-fast/static併用、欠落は閉error、NPE catch正常化0 |
| PT-USER-CHANGE013 | mutable入力/不変issue/display snapshot、redaction | 後変更でrequest/表示不変、map変更拒否、password/token/CSRFを通常表示/exceptionへ出さない |
| PT-USER-CHANGE014 | password close/二重close・別所有DTO | owned char[] terminal、close後toRequest不可、他DTO/他form所有を壊さず完全String消去主張0 |
| PT-USER-CHANGE015 | 8thread100別target/操作/UUID | 全byte/target/version/操作対応・混線0・個別close、Production expected算出0 |
| PT-USER-CHANGE016 | 既存wire4capability/API UserCommand/Mutation SQL・null/異常 | 各入力が既存固定requestへ渡る、self/last ADMIN/競合/全session失効はAPI正本を維持、formだけで認可/成功保証しない |

Java25/strict null compile/static0・全対象4counter100、immutable constructor/factory、独立normal control/negative。実command/OS/tool/source/exit/counter/BUG/manifestは070へ実測保存、PG440全source採取/freeze後だけ実装。QA049更新token完成方式は未承認、POST/controller/template/全ordinaryWeb/Caddy/CHR/native100/正式品質は別未実行。期待wireはUI236 offsetから独立作成、SQL後条件は既存API実DBの関連suite、未実行やfailed/skipped/flakyを合格に算入しない。

2026-11-26 JST、BUG-3859／YKT-2997。PG45390は対象008と変更015の各並行試験を明示的に選択。元の8 worker、100入力、各Future期限、合成値と固定の期待値は継承。終了はViewFixtureWorkersへ委譲し、同時に失敗した場合の一次例外と抑制例外を保持する。実業務・認証・DBの証跡には加算しない。
