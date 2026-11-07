# WebAccess失敗handler全単体仕様

NK-WEB-001/WBS-P015-02、FUN001/AUT001..004/UI221226252/SS313314351352/PG-D112、対象whole WebAccessFailureHandler constructor/commence/handle/isNavigation/static matcher。Main7aed不変更、同constructor owner/cache/heap Mock Servlet/Loggerと明示空ThreadLocalでpublic contractを確認する。元DB/fullchain Testの部分抽出ではなく独立した全六method。null/保存前提/全media分類/監査順/例外identityを手書literalで確認、実認証・role付与を認定しない。

|Test ID|入力と独立期待|
|---|---|
|PT-WEB-ACCESSPORT001|constructor依存nullと両API全3null引数→NPE、request/session/audit/response callback0|
|PT-WEB-ACCESSPORT002|GET/scenarios?page=2→status403→相対String一save→AUTHORIZATION_DENIED/UNAUTHENTICATED監査→Location/login→302。savedGET一回、JSON actorなし|
|PT-WEB-ACCESSPORT003|POST/HEAD/AJAX大小無視、audio/animation-media/music-media/music-download全四prefix→403/audit/send403、session/Location0|
|PT-WEB-ACCESSPORT004|空owned contextのAccessDeniedはmethod別でもstatus403/audit ROLE/send403一回、session取得/actor/Locationなし。実user role認定ではない|
|PT-WEB-ACCESSPORT005|内部context欠落/異型は全callback前拒否、cache owner欠落はstatus403後に固定失敗、save/audit/redirectなし|
|PT-WEB-ACCESSPORT006|普通のaudit runtime失敗とsendError IOException/header runtimeは同一identityで一回伝播、後続の成功redirect/再試行0。部分savedString/audit保持も期待どおり観測|

Testは固定UTC時計/公開TestNet IP/固定UUID/heap session公開labelのみ。cache既9/22250の受入を繰り返さず本runのsupport範囲だけ測る。request内部contextは同package constructorをMockへ設定し、実Caddy/Root信頼の証明にはしない。実sessionID/Cookie/認証/DB/crypto/JMS/HTTPserver/Root/native/VM/held四を実行しない。cause graph walk/旧失敗cohortを再現しない。SOURCE全CodeでL/M/C/B未達0、自然零のみN/A、同normal classbyte/CRC/一session/exec/全実method/初期化許可境界を独立postで照合する。正常/境界/null/単純異常・応答失敗を六methodで網羅、business再送/並行DBは非該当、stateless handlerの共有ThreadLocalはchild JVM内で前後clearする。source固定後一Unit、F/E/S/abortは合格外。開始.5/2/4cap5/原予算/正式1964-53/工数null/全HOLD維持。
