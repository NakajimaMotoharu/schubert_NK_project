# 管理metric供給口 PG/HTTP借用write PT仕様

RD171/MON010～013/UI252/SS311342351、NK-OPS-001/PG-D619/group2049/主P018-09/C07追加費0。開始fresh43残57/reset1793382075、凍結見積2/5/9pp・cap10。
既Api/WebManagementServerにcontextを借用するbind三引数/五引数を追加し、既bindはOptional.emptyで従来通りとする。callerはcontextを先に保持/initし、manager終了確認後にcontextをcloseする責任を残す。managerはSDK/contextを取得/init/closeせず、handlerをfactory.create前にcapturedする。既respondのtry(exchange)内で固定metrics rawpathだけhandler.writeへ委譲、健康/公開info/旧ready/defaultport/stop契約は変更しない。

handler.handleはexchange所有、writeは借用。両経路で全render後headers/body、write単独は成功/失敗ともexchangeを閉じない。managerのtryが一回だけcloseし、二重close/partial成功/SDK破棄を避ける。modifier/public write追加はrole内HTTP境界責務に限定する。

|対象|判定/実行|証拠と合格の範囲|
|---|---|---|
|Api/WebMetricHttpHandler ctor/handle/write|通常PT、memory exchange/new2 each＋変更後必要既16 each=actual36/2|APIMHTTP/WEBMHTTP017成功借用writeとnull/018失敗借用write、新4のみ追加成果。旧001～016の32は変更のため必要互換回帰・新規算入0。当二Main四100/static/CRC-session|
|Api/WebManagementServer新bind/constructor/respond|PG実装とpublic source強化レビュー・許可済みcompile/metadata/static|defaultserver/start/stop/実socketを含む動的経路は既HOLDに依存しUNRUN。source読取/compileをPT PASSへしない。拒否TestID未特定を偽って免除完了にせず、coverage未測定を100にしない|
|ApiProcessMain/WebNativeRuntime|不変更・未接続|Root consumer/source供給・実owner/起動/native・観測鮮度は後続依存、現manager portだけをactual受入しない|

017fixture: STD context/GET/手書きready1/UTF8独立byte/header、write後closed=false/calls0・caller close後calls1/context render継続、write(null)拒否。018fixture: ready Runtime原identity/headers0/partialbody0/closed=false・caller close1/context保持。既001～016のexpectedは1817と同一。new16 fixtureの順序やregistry/family/tagは不変更、独立oracle・元例外identityを保持。

source固定後8774正常six PT0→8776 actual36(新4/必要32)→8778当handler2四counter100/静的/CRC-session/negative→8780全1832/変更4parent physical/旧1828・原1667不変/現221owner/五edge・manager source/metadata ownershipレビュー→1820/result/scan/push。manager PT/全source451/native/CHRは未受入、必要なqualityを免除せず保留として追跡する。新ソケット/VM/DB/keys/permission/job操作0/Root変更0/拒否探索0、元4222確認再演0。正式1964/53・原190新受入0・工数null・QA051final/PTALT0/全actualHOLD、原本/stash/元見積/v4/v5保持。開始時actual36 UNRUN。
