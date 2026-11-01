# SessionPrincipal 表示snapshot境界 独立PT仕様

PG17910、source6b53efeec87f3ec36a840dd8e7759656cb4aee5c/未配備、HEADbec06882d4cdba94a6dbf556a8b4f6ae9913bf3e/branch dev-foundation、固定1/3/6pp cap10。主F03/関連P015-02追加費0、NK-WEB-001/NK-AUT-001/FUN001/AUT001～004/UI226/SS314§7.2.1・SSC014の表示64byte/key96byte補足/SSC038/PG-D094/PT-WEB009～015、既3001/3002/3004を継承。Main42/AuthenticationContext45/UserRole18を全読、NFC/64byte表示と96byte比較keyを混同せず、実API/session/JSONcodecとは分離する。

新quality Test五件はSource value constructorの独立境界で、保留SessionSecurityContext等の元method/fixtureを抽出しない。Production Main/Test変更0。固定公開a×64のtyped AuthenticationContextと固定Instant/USERADMIN値だけ、実context発行/login/session/Cookie/DB/JMS/HTTP/SecurityContext/crypto/鍵/Root/native0。

|Test ID|入力・操作|独立期待値|
|---|---|---|
|PRINCIPAL-BOUNDARY001|e＋U+0301、ADMIN、公開typed context、固定UTC|手書éへNFC、username/getName一致・残三component identity保持|
|PRINCIPAL-BOUNDARY002|a1/a64/é32/emoji16/İ32、分解e＋U+0301を32組|表示NFC後1～64 UTF8byteを保持、lowercase比較keyへ変換しない。分解列のraw96byteでもNFC後64byteなので受入|
|同002 overflow|空/a65/é33/emoji17/分解33組|固定IllegalArgumentException/session principal is invalid/cause null/suppressed0|
|PRINCIPAL-BOUNDARY003|孤立high/low surrogate、mixed不正Unicode、C0/C1(0,9,10,13,31,127,159)、末尾ASCIIspace|同固定拒否、不正UTF8置換で受入しない|
|PRINCIPAL-BOUNDARY004|username/role/context/loginAt各null|API invariantとしてNPE拒否・publication無し、catch通常成功化0|
|PRINCIPAL-BOUNDARY005|USER/ADMIN・Display_Userと固定context/time|表示caseとcomponentを保持、toString固定SessionPrincipal[REDACTED]、権限を認定する動作なし|

é2byte/emoji4byte/İ2byteというUnicode literalから境界を独立算定。Production Normalizer/constructor/戻り値でexpectedを生成しない。ctor NFC許可の試験であり閉JSON decoderがnoncanonical表現をどう拒否するかは別契約。認証4field all-or-none/最新role再検証/expiryはcodec/API/外側責務で本値objectだけから実認証成立を推定しない。並行/実再送は不変snapshotの当経路外で未実施、独自Thread/executor/task/UUID/乱数0。

全一Source一Code・15L3M1C10Bを新単一execで実測。recordのcompiler生成accessor/equals/hashCodeは公式JaCoCo0.8.15既定filterのまま、custom ctor/getName/toStringは全counter対象、任意除外/無意味なgenerated memberへのcoverage目的assert0。component値assertはsnapshot契約のため行う。未達は未達、実証100時だけ元15759-a11c2bc0 partialを履歴保存し置換、旧exec union0。

command：python3 -B tools/quality/pg11123_checked_python_entry.py tools/quality/pg17910_session_principal_boundary_five_pt.py。normal14216/Spot14224/report runtimeを同byte再用、新qualityTestは元srcの入力へ偽装せずSHA4364589f803a56246baf9c90bc232b96a2c7f2a27e6d04d301e561ea3f65d3fcを固定。OS/JDK/branch/HEAD/command/time/exit/XML/exec/input/class/hashは3441予定と各manifest。普通5786/quality件数を分け、正式1964/53・歴史17/190・新WBS受入0/工数null/QA051final/451/全HOLD維持。
