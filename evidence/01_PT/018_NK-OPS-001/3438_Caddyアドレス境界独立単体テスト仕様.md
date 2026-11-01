# Caddy numeric peer・header境界 独立PT仕様

PG17880、source6b53efeec87f3ec36a840dd8e7759656cb4aee5c/未配備、HEADa4635c7822f7b56045a1013fd10b8b2a127c347a/branch dev-foundation、固定1/3/6pp cap10。主F03/関連P015-02追加費0、NK-WEB-001/FUN001/AUT001004、UI226/234、SS314§3/5・342§3.1/352・BUG066/PG-D105/PT-WEB082～089/既3013/14。群開始のMain49/Address28/Exception14という行数記述は実40/26/13計79へ訂正、開始event/予算は不変更。

新tools/quality/architecture/CaddyAddressBoundaryContractTest六件は上位header契約から独立作成したmemory Servlet入力のみ。保留ErrorMvc/WebRequestSecurity等のTest method/fixtureを抽出しない。Production Main/Test変更0、実Caddy/HTTP/socket/Server/filter/audit/session/DB/JMS/Root/native/permit/getent/credential操作0。ofLiteral数字解析は既3013許可済み・DNS lookup呼出し無し、JDK内部初期化の総効果はnullで外部資源成功を推定しない。

|Test ID|入力・操作|独立期待値|
|---|---|---|
|PROXY-BOUNDARY001|peer127.0.0.1/::1と一つのhttps、一つの203.0.113.27/2001:db8::9|forwarded numeric textをそのままvalue返却、Host/originや実利用者認証を認定しない|
|PROXY-BOUNDARY002|peer null/空/非数字/非loopback、Forwarded enumeration null/存在|固定CaddyRequestRejectedException、request proxy is invalid/cause null/suppressed0|
|PROXY-BOUNDARY003|proto enumeration null/空/null要素、http/大文字/余白/重複|同固定拒否、単一の小文字https以外を許可しない|
|PROXY-BOUNDARY004|for enumeration null/空/null要素、空/hostname/カンマ連結/重複|同固定拒否、DNS解決へ代替せず数字一件のみ|
|PROXY-BOUNDARY005|Servlet rawPeerがISE、getHeadersがIAE、nextElementがNSEE|同固定拒否、先に作るPUBLIC_UNTRUSTED_RAW文言/causeを保持しない|
|PROXY-BOUNDARY006|null request|ObjectsのAPI nonnull契約としてNPE拒否、catchして通常成功扱いしない|

同じProduction methodからexpectedを生成せず、独立literal peer/header/type/messageと例外属性だけをoracleとする。正常/IPv4IPv6/欠落/null/空/未知/重複/例外の全boolean経路を対象。並行/実再送/session発行は当parser契約外で未実施、Thread/executor/task/UUID/crypto0。Main全一Source一Code＝20L3M1C18Bの全分母を新単一execで実測、未達を実測まで100としない。既helper LoginClientAddress/RejectedExceptionの資格と旧Sourceをunion0、四100実証時だけ旧partial d6011b2cを履歴保存して置換。

command：python3 -B tools/quality/pg11123_checked_python_entry.py tools/quality/pg17880_caddy_address_boundary_six_pt.py。normal14216/Spot14224/共有reporter byteを再利用、qualityTestは既src入力へ偽装せず別SHAf0612ddb3090a317163f1793408c724796c1ab818fde23b0942192283178c6c0で固定。raw/post/独立XML/CRC/元OS-JDK/command/time/exit/全input/hashは3439予定とmanifestへ保存。品質fixture件数と普通declaration5786を分離、正式1964/53・歴史17/190・新WBS受入0/工数null/QA051final/451/全HOLD維持。
