# 2083 REQ006 Context境界補完 単体テスト仕様

NK-WEB-001、既WebRequestTraceTestのREQ006二method、source主責/費用主責WBS-P006-03を保持。G03.01参照0追加費、開始1/3/7pp cap10。BUG1843/YKT1594。RD FUN001/AUT004/MON004、UI222226252、SS313314342351352/SS312 §11。Mainの振舞い変更なし。

前source36/10542十PT/独立10544ではContextに三分岐・五行・二methodの不足が実測された。この変更による関連十methodの再実行は必要検証で、成功の確認再演ではない。2081/2082のMock-only全依存レビューを継承し、追加はMock requestの属性操作と例外/固定UUID/診断のassertだけ。新しい外部fixture、DB/socket/Root/key/VM/サービス操作や認証・権限変更はない。

|既method|追加入力/操作|独立期待/根拠|
|req006ServerIdentityIsStableAndDoesNotGrantTransport|正常Mock filter後の既ContextのtoString|固定WebRequestContext[REDACTED]、identity/addressを表示しない|
|同|Mock requestの内部requestId属性だけをremoveし、identifyのsupplierは呼ばれたらAssertionError|同じ入力request UUID(0,3)を戻し、属性を再設定。Production getterをexpected生成へ使わない|
|req006AllNullAndMistypedMetadataAreRejected|Contextのない新Mock requestへrequire|固定IllegalStateException、欠落は正常contextへ置換しない|
|同|require(null)|NullPointerExceptionの明示境界、catchして正常扱いしない|
|同|別Mock requestにContext属性として固定String not-contextを置きexisting|固定IllegalStateException/安全message/cause無し/suppressed0、不正型や値を漏らさない|

元一fallback固定式、三同値定数、既十methodの全元assertion/fixtureを保持し、二追加blockの除去で元source tokenと一致することをmetadataで確認する。誤UUID/誤message/旧getterへの置換/追加block欠落/他assertion改変を拒否する。所定format/static/正常六module compile、同source固定十method JUnit、XML/CRC/session/全Main1843・非対象Test byteの独立後検証、五完全Main countersを測定する。四counterは適用分母ごとに扱い、0/0をnumeric100へ補完しない。未網羅は未完として残す。

結果/source/run/command/環境/exit/coverage/関連障害/hashは後続2084と公開manifestへ。正式1964/53、個別17/190、工数null、QA051final/全安全HOLD不変。旧36/旧661/歴史sourceのexecを新sourceへ合算しない。

追加発見BUG1844/YKT1595：Mock内部suffix .requestIdが四参照となったためTest-local同値定数へ分離する。二block＋同値suffix一/四参照だけの全token逆展開を最終plan10554で確認する。中間sourceceの10552正常compile/PT0と元static10550六行は保持、最終sourceへ転用せず当sourceのstatic/normal/PTを別runで照合する。開始見積/品質は不変更。
