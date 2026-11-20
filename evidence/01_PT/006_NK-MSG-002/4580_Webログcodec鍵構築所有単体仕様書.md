# Webログcodec 鍵構築所有の単体仕様

NK-MSG-002、WBS-P018-10.03、UI235／242、SS352、SSC420関連、BUG-3483／YKT-2779。対象はWebLogPayloadCodec constructor。従来の受理・拒否順と暗号形式を維持する。

| Test ID | 入力と観点 | 独立した期待値 |
| --- | --- | --- |
| PT-WEB-WEBLOG-OWN002 | 合成32byte caller鍵、現在鍵長31、previous片方欠落、同version、random欠落を組み合わせる | current鍵長→previous組→同version→randomの順で最初の既固定診断。callerの二配列は独立連番fixtureのまま |
| PT-WEB-WEBLOG-OWN002-STATIC | 旧・新classのJDK javapの構築codeを比較 | 旧は最初のcloneが全設定前。新は全通常拒否分岐の後に最初のcloneを行い、二つめのclone範囲のErrorは取得済みcurrent copyを0で埋めて同じErrorを伝播 |
| PT-IDEM-012／015、WEBLOG-OWN001 | 元codec全10の境界、固定JCA golden、並行、過去鍵、復号、secret診断 | 元独立oracleと同一。別sessionや別sourceの結果を合算しない |

構築拒否のダミー鍵は公開合成。実OOMを発生させず、例外handlerのbytecode確認と動的coverageの未到達を分ける。実資格・DB・Artemis・実サービスおよび正式451は別条件。
