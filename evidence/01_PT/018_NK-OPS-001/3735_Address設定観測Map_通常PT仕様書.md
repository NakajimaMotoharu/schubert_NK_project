# Address設定観測Map・通常PT仕様書

Program NK-OPS-001 / ArtemisAddressSettingsReadinessClient.inspect/verify/constructor。RD MQ001002009010/UI231251253/SS321§5/10/13、QA042/UIC002/SSC130。原282未登録sourceのUNKNOWNを未実装と見なさず、公開PG22234では当Mainの対応受領不明だったものを実codeと元ArtemisAddressSettingsReadinessClientTest/ArtemisUnknownBoundaryTestの本文で確認。旧Testsは実broker期待値からverifyし、inspectの返却Map26field・六address完全一致/独立不変/未知field非公開の明示assertionは無し。既broker成功結果を再実行せず、既設Reader契約に限定した通常独立PTを追加する。UNKNOWNを未実装/旧試験失敗とはしない。

PT_DEFAULT: current normal Main22084の未変更batch/protocol/storage/bootstrap依存、既Readerへliteral JSONを返すだけ。ClientSessionは全method呼出を拒否するinterface proxyで開設/通信/closeなし。default constructorは組立だけ、既設Reader付きinstanceからinspect/verifyを呼ぶ。実Artemis/VM/DB/Root/native/process/filesystem/四heldclass初期化/実approval/permitや拒否操作へ到達しない。旧Test/helper/fixtureをcompile/runしない。Main抽出/改変や既期待値の緩和はしない。

OPS-ASET-001=六address各26の返却値をSS321独立固定literalで照合、余分fieldは返却せず、borrowed Session呼出0、入力と返却を分離。
002=outer/inner Map変更拒否、次inspect失敗でも既snapshot不変・再利用instanceの独立結果。
003=実数/boolean/文字列型をSS固定literalから変えたdrift、途中readでfail closedし後続read/再送0、最初の二成功結果を正常結果として返さない。
004=null/非String/JSON非object/missing field拒否、reader独自Runtime/Errorは同一identityで即時伝播、Session操作0。
005=verifyの六回投影とno-context default組立、入力未変更・返却Map別identity、所有を移さない。

期待値=SS321§5.3のmemory/page byteを独立整数33554432/234881024等でliteral化、SS5.1/5.4に従う共通22。Production methodでexpected生成しない。旧field-null/drift検証と重なる補助assertionを新unique case数へ分解加算しない。新五methodを一群、全成功/FESabort0を原Unitとして測定。Main physical全Code/nocode/normalCRC/実init/一session一exec・四counter確認、未測定は補完せず、global451/Formal/leaf非受入。

原見積1/3/7pp cap9、通常PT追加（元計画不足の補完、全体工数率null）。PGとMain本体は変更なし、独立expected→Test source→format/compile/PMD/CS→source固定commit→Unit/coverage→独立post→帳票。source/run/command/SDK/input/hash/exit/coverage/未測定をmanifestへ。
