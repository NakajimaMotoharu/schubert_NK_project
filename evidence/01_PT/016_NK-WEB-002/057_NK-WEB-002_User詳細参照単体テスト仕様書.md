# User詳細参照単体テスト仕様書

2026-10-03、NK-WEB-002/SCR017/PG-D346、RD FUN009/AUT002、UI222/225 §5/236 §5、SS313/314/323/332。UserAdminController.detail/UserDetailViewModelと明示view/template、UserAdminControllerTestの追加8JUnit。更新form/成功POST/完成token履歴QA049は別未完了。

| Test ID | 入力・操作/fixture | 独立期待値・観点 |
|---|---|---|
| PT-USER-DETAIL001 | ADMIN/UDT target42・0000/0200 | UI236 UDTREQ12 numericID/UDTRSP320の全byteを手作成、requested ID=returned ID、username/role/state/日時/actor/active count/versionの明示表示値 |
| PT-USER-DETAIL002 | real MVC/Thymeleaf GET HEAD/特殊username・actor | User詳細title/common Menu/通知/Logout CSRF、全field escaped・password/token/contextなし、unknown numeric route404。PG452/SSC177の同class業務POST追加後、旧2引数partial MVCはfull token依存なしで503/API0。旧read-only時点405結果は058へ歴史保全し本sourceへ流用しない。full構成の業務POSTは081/BIZを正とする |
| PT-USER-DETAIL003 | USER/欠落・誤principal/ID0・13桁・非ASCII | USER403/ADMIN不存在404、API未送信、null境界拒否 |
| PT-USER-DETAIL004 | 全result code/JMS/timeout/correlation・context・reserved異常 | WebResultMapper固定HTTP、0102既存session terminal、wire invalid503/元buffer0/pending0、予期しないErrorを正常扱いしない |
| PT-USER-DETAIL005 | 応答target不一致/count3/欠落日時 | 正規payloadでも表示invariant違反503、wire mandatory破損503、要求値へ修復しない。version0を異常とした旧誤記はBUG639/YKT452によりSS331/N9正常へ是正し009で確認、過去結果は改変しない |
| PT-USER-DETAIL006 | LOCKED/ACTIVE/DISABLED/Optionalありなし/session count0..2/self・他人 | UI225全表示/固定Login失敗lock理由・他空、日時JST millisecond、immutable display-only Map・role/ID/version/context非混線 |
| PT-USER-DETAIL007 | 8thread100 current context/UUID/target固定 | request毎API照会/100別Message ID/actor表示一致/全buffer消去/pending0、sessionへresponse body保存なし |
| PT-USER-DETAIL008 | real encrypted session/Tomcat 11.0.25 ADMIN USER/匿名/API0102 | 独立HTTP200/403/302・GET HEAD/no-store、API失効後Cookie/DB終端、対象4coverage/static6/strict null |
| PT-USER-DETAIL009 | fresh UDT320 version0/999999999 literal | admin/user-detail/200、受信versionそのまま表示。SS331 default0/N9の独立期待値、BUG639の誤positive拒否を正規oracleへ戻す。081/082へ新source再試験を追跡 |

期待値はProduction codec/ViewModelを呼んで生成しない。実行Source/環境/command/日時/FES/coverage/BUG/YKT/証跡hashは016058/manifestに実測後記入、選択結果を正式全scope/native100へ算入しない。
