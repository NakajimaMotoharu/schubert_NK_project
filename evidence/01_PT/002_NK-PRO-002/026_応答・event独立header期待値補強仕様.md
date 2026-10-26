# 応答・eventの独立header期待値補強仕様

2026-10-26、BUG1806/YKT1557、G03_HEADER_PROFILE_WIRE_ORACLE_V1/開始.5/2/5 cap10、G03.01主・原担当費P00203関連追加0。NK-PRO-002/MessageCodecTest.responseAndEventHeadersRoundTripWithoutLeakingContext、既PT-PRO-002-H01。RD MQ014～038/MSG001～011、origin/main UI232§3/SS322/451。Main/上位設計/Current baseline変更0、新Test ID0。

UI232の全17fieldを独立literalで256byteへ組み立てる。byte位置は1開始：magic1/8、version9/3、layout12/8、layoutversion20/3、区分23/1＋24/1、message25/36、correlation61/36、JST97/17、context114/64、header長178/4、data182/6、record188/6、count194/6、total200/9、result209/4、reserved213/44。

応答はGAMRSP01/SS、UUID123e4567-e89b-12d3-a456-426614174000／223e4567-e89b-12d3-a456-426614174000、JST20260902123456789、公開合成a×64、0256/000009/000272/000001/000000537/0000、予約space44。eventはWLGEVT01/EI、同UUID/JST、context space64、0256/002080/000000/000000/000002336、result space4/予約space44。算術256+9+272=537／256+2080=2336を仕様から確定し、Production methodでexpected生成しない。

各golden長256、encode全byte一致、独立wireをpeekして固定入力CommonHeader全属性一致を検査。旧QSのgolden/全negative/roundtrip/全元assertionを保持。今回一既存methodに二vectorを追加するので二新PTと数えない。実HTTP/JMS通信・実context認証・秘密値・DB/VM/Root/FFM/保持file/鍵closeに依存しない純Protocol input-only通常PT、他HOLDは解除しない。

先行Test-only static/当file GJF→source固定/正常六compile0/PT0/NullAway→当一method閉catalog/JUnit一回→原XML/一session/全CRC/完全HeaderCodec source-unit四counter/他Test method probe0/全Main1843不変/旧Test token保持/static適用性/traceへ。全coverage100を予測せず、測定不足/生成非適用/残WBSは明示する。正常/境界/異常/null/並行/再送の元試験は削除せず、本二正常profileだけの結果を全Programへ転用しない。command/OS/JDK/source/exit/coverage/hashは027と共有manifestへ保存。
