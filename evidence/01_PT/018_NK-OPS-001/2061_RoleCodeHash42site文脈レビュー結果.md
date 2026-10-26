# Role/Code/Hash42site文脈レビュー結果

G03.01、群2379・開始0.5/2/6pp/上限10、source3d9f1d9fd395e8cb9456b0a540e1f29bcb87876e。PG10252の非共有role.wireValue/code.wireValue/hashを含む42syntax候補/21sourceを点検。変更済みsourceの元line番号を現lineとして使わず、現SHA/実selector位置を再照合した。製品/fixture/実環境操作なし。

|候補|syntax site|判定|
|---|---:|---|
|Web role.wireValue|17|12sourceの表示/監査role期待がSUT mapping共有。BUG1825/YKT1576。追加検索でAPI UserCommand.assertUserも一、実修正対象18/13source。入力enum identityと期待literalを独立させる。|
|API code.wireValue|12|五sourceで同SUTの結果文字列を期待wireへ使用。BUG1826/YKT1577。負例fixture二とQuestionMutation共通wire一を含む実対象15/六sourceへ横展開。元12というsyntax件数を実全使用数とはしない。|
|Scenario hash|1|固定4800byte Test行の独立JDK SHA-256、golden65で既確認。新成果へ重複算入しない。|
|SuccessProgressSeal hash|6|Test固定JSONと明示更新後JSONのUTF-8/JDK SHA-256。Production seal/hash methodでexpectedを生成しない。DBの動的後条件再認定ではない。|
|ReleasePayloadVerification hash|4|Test synthetic byte payloadのJDK SHA-256、Production verifier経由でexpectedを作らない。実署名/鍵/配備の資格へ換算しない。|
|JdbcWebSessionStore hash|2|Test IDの`%064x`整形で作る合成識別子。実session/tokenではなく、本番hash methodの検証でもない。|

新指摘二は上記mapping共有であり、製品の誤動作は観測していない。hash13siteの独立性確認を実DB/native等の実行免除にしない。QA/設計変更不要、元17/190・1964/53・工数null・QA051final/全安全HOLD不変。

PG10390は当42syntax行/21source SHAと元line有効性、横展開で見つかった実18role/15codeのpath/count/hashを保存する。自動独立性判定ではなく、本表の人手レビューを束縛する。次はrole18から別群見積りを凍結し、ソースを最小是正、純画面部品Testの依存確認後だけ通常PTへ。code15はその後に一経路ずつ行う。
