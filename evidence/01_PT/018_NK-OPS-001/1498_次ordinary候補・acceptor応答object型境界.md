# 次ordinary候補・acceptor応答object型境界

事前訂正（BUG1624/YKT1377）：下記初期予定14/7・23/10は未実行の誤予定。共通guardは六moduleだが**12method/七suite**であり、実declarationを読み直した正規初回範囲は **23/11**（guard12/7＋既関連8/2＋新3/2）。旧23/10はinventory ValueError/exit1でremote job/PT未起動、成功へ加点0。工具を正規23/11へ修正し、実declaration一致・旧23/10変異拒否の管理二を追加する。予定値訂正で予算やProduction oracleを変更しない。

API元6828実行中の独立仕様準備。現在Main/Test/gatesを変更せず、当source4203の原品質・trace完了後に着手する。以下は予定で、試験実施・合格・coverage・leaf受入に加点しない。

## 対象と事前分類

`batch.mq.ArtemisAcceptorReadinessClient.inspect/verifyResponse`のdata-only応答検査。WBS主担当は485のP017-10（Artemis開始・ACL・圧力・readiness）、全業務起動の認定ではない。RD MQ001/002/009/010・SYS004、UI231/251/253、SS321 §2/10/13・SS342 §2/4、既PT-OPS-MQ013..015へ関連付ける。

通常PT_DEFAULT。固定JSONを既package Reader portから返し、ClientSessionは全methodをAssertionErrorとする未使用proxyのみ。ネットワーク、broker起動、管理接続、credential、DB、VM、Root、cohort、permit、実native、権限変更は一切不要。既ReadinessClientTestの実broker試験をこの新Testへ移植しない。拒否操作を探る検証でも、その再試行でもない。

## PG点検と独立期待値

SS321は唯一のloopback CORE acceptorと所定設定を要求する。既固定応答はname=core、NettyAcceptorFactory、paramsのscheme=tcp/host=127.0.0.1/port=61616/protocols=CORE、extraPropsは空object。Productionの`verifyResponse`はextraProps/paramsのobject型を別に検査し、異なる型は固定ArtemisManagementReadinessExceptionとする。新TestはProduction methodをexpected生成に使わない。

既opsMq014はextraProps非空、名前/port/各値/鍵集合/配列個数等を検証するが、extraProps/paramsそのものの非object型の明示入力がない。新二Test予定：

| Test ID | 入力・操作 | 独立期待値・後条件 |
|---|---|---|
| PT-OPS-MQ-OBJ001 | 全他項目が固定正常のJSONでextraPropsだけnull/array/string/number/booleanへ変更しinspect | 全て固定例外、cause=null・suppressed空・固定redacted message。started Reader未呼出、session操作0 |
| PT-OPS-MQ-OBJ002 | 全他項目が固定正常のJSONでparamsだけnull/array/string/number/booleanへ変更しinspect | 同上。params objectの前提を満たさないのでstarted照会へ進まない |

最初に完全正常JSON→明示固定Mapとstarted Reader一回を確認し、例外fixtureが常に失敗するだけでないことを担保する。各vectorの型はJSON literalとして独立列挙し、正常schemaの他fieldを失わない。借用sessionの状態を変えず、再送・並行・資源解放はこの純粋検査に非該当（既live管理/owner契約は別scope）。NullPointerExceptionをcatchして成功化しない。

Production実装が上記期待と異なれば、修正前に915/916を採番して起票する。現時点は未検証観点でありProduction障害と断定しない。PGレビューで必要な変更がなければその根拠を残し、coverageだけのためMainを変更しない。

## 実行予定

現API品質固定解除後、群開始予算.2/.5/1.5pp・fresh80/残20/reset1793082864・Main全851同byteを確認し、新Test二methodだけを追加。既全oracle固定。初期14/7は単独新Testの予定であり未発行。最初の実行前に1499のschema一Testと、対象class全counterの比較に必要な旧関連二suite（未変更Acceptor三・GateEvidence五）を同束へ選び、実declaration **23/10** を確定する。六guard12＋旧関連8＋新3。新Test自体はdata-only、旧Acceptor suiteだけは既自己所有の有限loopback broker fixtureを通常通り実行し、実環境管理接続とは区別する。Root/VM/既DB/権限/原本操作0。

format/compile-null/Werror/六SpotBugs/元XML/原Jar/対象四counter/全Main物理byteを照合する。全Main/全旧Test/gates固定のTest-only束であり、新全体の必要性は変更と原結果から別判定し、確認だけの旧4203再演をしない。未実行を成功算入しない。新selectedの全module coverageを旧fullへspliceせず、current全体4c034/4203と分離する。

正式1964/53・個別17/190・工数null・原/v4見積り・QA051final・全実環境HOLD・PTALT代替0を維持する。
