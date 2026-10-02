# SCR015 User一覧HTTP単体テスト仕様書

2026-10-03、PG-D344、NK-WEB-002。関連RD FUN009/AUT002、UI221/222/225 §3/232/236 §3、SS313/314/323/332。対象UserSearchForm、UserListViewModel、UserAdminController.list、UserMvcConfiguration、admin/user-list.html。実装・実行前仕様。全User管理/全Web readyの完了を表さない。

| Test ID | 目的・fixture/入力・操作 | 独立期待値 |
|---|---|---|
| PT-USER-HTTP001 | ADMIN/0000・0200、0/1/50件、正規filter、GET | USRREQ01 data96のoffset0 prefix64/64 role5/69 state8/77 page6/83 size3/86 reserved10からliteral vectorを作成。全header/認証context/UUIDを個別照合、responseはUI236のPAGED48/record168を手作成。HTTP200、template一覧50、秘密なし |
| PT-USER-HTTP002 | form既定/正常NFC・trim/ASCII page 0・負値/999999、closed enum | page<1は1、size50、空filter Optional.empty、byte制約・不変copy、toString redacted |
| PT-USER-HTTP003 | 未知・複数・空collection/null key/value/element、control/surrogate、prefix64/65byte、bad role/state、overflow/非ASCII page | 欠落は既定、複数/未知400、契約null拒否、禁止文字400、wire0。期待値はUI222/225とASCII整数のliteralから計算 |
| PT-USER-HTTP004 | USER/wrong/null principal/constructor・method null | USER403/送信0、他契約拒否。ADMIN専用fixtureをUSER成功へ流用しない |
| PT-USER-HTTP005 | all API error result/timeout/JMS/header・correlation/context/filler不正 | 明示WebResultMapper status、0102のみ既存terminal invalidation、技術失敗503、画面業務row0、buffer zeroing |
| PT-USER-HTTP006 | record数/重複ID/order/同名ID/PAGED値・page補正/不正typedデータ | 期待外は503または投影契約拒否。UTF8 C順のBMP/補助文字反例を独立literalで検証、並べ替え/修復しない |
| PT-USER-HTTP007 | MVC/Thymeleaf実描画、空・page1/2/末尾補正、filter escape・unsafe username | GET/HEAD200/HEAD body0、POST405、50件size、リンク保持、HTML escape、hidden Logout CSRF、password/hash/context/secret出力0 |
| PT-USER-HTTP008 | real encrypted session/security filter、USER/ADMIN/匿名、API0102 | 真正security拒否/本人row失効/Cookie終端、API role再認証。無権限・invalid formは送信0 |
| PT-USER-HTTP009 | 8thread/100要求、distinct actor/context/filter | 各HTTP result・snapshotと各送信byteが対応し、context/query混線0、fresh UUID、pending0・元buffer全0 |
| PT-USER-HTTP010 | 独立型/集合/投影invariant・getter/URI/constructor negative | all対象class/method/line/branchへ意味あるassertion、期待値のproduction計算0、null/空/unknown/境界を固定 |

開発中は影響Web/既存wire/session/template/媒体PTと依存moduleを選択実行し、厳格compile/NullAway/Spotless/SpotBugs/JaCoCo4counterを採取。User画面変更群を固定した同Sourceで451全回帰。実command/環境/source/exit/coverage/FES/BUG/YKT/日時/hashは054・safe manifestへ採取後のみ記入。既存PG434を新Sourceへ合算しない。生成XML properties/stdout/stderrを除去、秘密情報・実session/password/token・dumpは保存しない。native/CHR/全scope100%未実行は不合格算入0。
