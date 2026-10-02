# User追加入力単体テスト仕様書

2026-10-03、PG-D345/NK-WEB-002/SCR016。RD FUN009/AUT002、UI222/225 §4/236 §4、SS313/314/323。対象UserCreateFormのcreation password契約、後続POST UserAdminController.createの入力前提。初版は実装前、実績は016056を参照しWeb成功POST/完成token処理を認定しない。

| Test ID | 入力/操作・fixture | 独立期待値/観点 |
|---|---|---|
| PT-USER-CREATE001 | validASCII username/USER ADMIN/true false/password12..128 codepoints/UTF8 byte<=256/canonical UUID | named UCRREQ01の372byte dataをUI236 offset0 username64/64 password256/320 role5/325 enabled1/326 token36/362 reserved10から手作成。Productionでexpectedを生成しない |
| PT-USER-CREATE002 | NFC/trim/account case、password NFC確認、補助Unicode、12・128文字/256byte境界 | usernameのみtrim、passwordの空白は切捨てない。codepointとUTF16長を区別、独立literal Unicode/byte golden。role/enabled既定はGETだけ、POST欠落拒否 |
| PT-USER-CREATE003 | 未知/複数/空collection/null parameter/key/list/element、_csrf1/複数 | binding400相当・request生成0、null契約拒否。_csrf値の保存/保持0、フォーム検証をsecurity CSRF代替にしない |
| PT-USER-CREATE004 | username0/65byte・全禁止ASCII/Unicode、control/unpaired surrogate、password11/129文字・257byte・末尾space/usernameと同じ | field固定errorのみ、例外/log/getter/toString/再表示に秘密0、API未送信 |
| PT-USER-CREATE005 | password確認不一致・NFC一致/unknown role/enabled/UUID大文字/短縮/壊れ/欠落 | 完全canonical UUIDだけ形式成立、用途/session bindingは後続呼出しが必須。unknown値をdefaultへ修復しない |
| PT-USER-CREATE006 | immutable params/close/invalid toRequest/normal例外・二重close | caller入力変異非影響、char[]寿命を意味ある再生成拒否で検証、closedはfixed exception、zeroingをgetter/private reflectionで覗いてcoverageを作らない |
| PT-USER-CREATE007 | 100並行異なるusername/password/UUID、HTTP model相当safe projection | command混線0、入力password/確認/CSRFはsafe model 0、全各値の独立wire一致、結果・モデルをsessionへ保持しない |
| PT-USER-CREATE008 | constructor/factory invariant、全null/空/未知・全例外/境界 | JSpecify/NullAway・strict compile・Spotless/SpotBugs0、対象line/method/class/branch100%・意味あるassertion。API完成/token履歴・実HTTPPOST/nativeは未認定 |

実行環境/command/Source/日時/exit/FES/coverage/BUG/YKT/証跡hashは実測後016056・safe manifestへ記入する。QA049/UIC008/SSC170の承認前に完成token JSON/history/退役・oracleを変えない。source固定中PG435成功をこのformへ流用しない。
