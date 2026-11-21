# SCR015 User一覧原三artifact契約・独立期待値

NK-WEB-002。対象source/hash、承認設計commit/hash、独立期待値/TestIDは [PG27842](../018_NK-OPS-001/evidence/PG27842-user-list-three-contract-v1/manifest.json)。

- P01615-PG01 / UserSearchForm.bind/invalidCharacter/toRequest / PT-USER-HTTP001..010,USER-DISPLAY001..005: Four keys username/role/state/page only; unknown key/list0-or-multiple fixed binding error, map/list/element null rejected at constructor boundary. Controls and isolatedUTF16 reject before NFC+trim, username<=64UTF8bytes, closedoptional role USERADMIN/state ACTIVE DISABLED LOCKED. Empty/missingpage1; signedASCIIint<=0 floor1, positive<=999999, overflow/plus/decimal/unicode digits rejected. Immutable copies/redacted tostring. InvalidtoRequest fails; validwire pageSize50/optionalempty and no owner authority inferred. Pure string NumberFormatException boundary no provider callback.

- P01615-PG02 / UserListViewModel.success/invalid/link/Row / USER-DISPLAY001..005,PT-USER-HTTP006..010: Local ADMINdisplay guard; actualsecuritychain/API auth separate. Successrequiresvalidform, PageViewModel50 exactcount/effective=min(request,totalPages), exactrecordcount/uniqueID/usernameUTF8unsigned C-byte ascending thenIDstrictascending, no repair/resort. Emptyvalidpage/prevnext borders; copiedrows+stablefilterlinks all3conditions percent-encoded. Invalidform has no results/count/navigation. Rowusername/role/state/lock/lastlogin/createdupdated fixed+09millisecond display, optionalmissingempty, logical positiveID detailhref; no password/session/foreignobjects. Caller mutation cannot change immutable exposed list/beans.

- P01615-PG03 / admin/user-list.html / PT-USER-HTTP007..010,PT-RESOURCE-USER-LIST: Exact Users title/User追加/detail nav and field/columnorder fromUI225. GET searchfields retained/closedrole-state options, errorsescapedtext, no hidden session/token/password. Count/prevnext only whenPagepresent, empty message or escapedrow table, logicaldetailhref, sharedlogoutCSRF remains separate. No utext/inlineJS/rawDTO exposure; actualHTTP/auth/DB/page SQL/original190 ending not accepted by source/template checks.

- P01615-PG04 / Historical UserDisplayContractTest whole8 and later shared current qualification / USER-DISPLAY001..008: 3472/3473 and PG18210/12/14/25 retain original eight/source/run. AlltwoVM/helper source hashes and wholeTest byte checked only against original begin metadata; no replay or transfer of oldsource8/coverage. CurrentProto176 dependency changed, therefore after P01616/17 wholefixture source/closure review price exactly one shared current8, not newTest definitions or P01615+17 double fee. Originalcontroller/Bean DB/actual4 fixtures remain HOLD/unextracted; no privateResult or substitute permission seam.

SCR015原三source全文とUI225236/SS313332を対応。四入力/NFC64byte/50page/closedenum・signedASCII補正/immutable/ADMIN表示guard、UTF8 C-byte名順-id昇順/exactrowcount/JST9h/optional/全条件pagination・実templateescaped列順を独立期待へ固定。旧UserDisplay全8/六helper/wholeTest hash一致を元sourceだけ参照・再演0、現Proto依存の資格へ輸入0。P01617読取後に必要currentwhole8を一回共有価格、controllerDB/Beanactual4HOLD/新grantfixtureなし。原/1準備だけ、/2actualHTTP認可/DB/CHR/451未受入。

実行: `python3 -B evidence/01_PT/018_NK-OPS-001/input/1841_user_list_contract.py` metadata終了0。新規製品PT/coverageなし。原/1の準備だけ、原/2・451・元190未受入。独立期待値は公開設計の固定境界・順序・後条件に基づき、production methodで生成しない。正式1964PT/53scope・工数null。

## 製品テンプレートの表示検証

NK-WEB-002／WBS-P016-15/2／FUN-009、AUT-002、UI225・236、SS313・332。製品の `admin/user-list.html` と共通layoutを使い、独立した表示用mapをレンダーする。

| Test ID | 入力・独立期待値 |
| --- | --- |
| PT-WEB-SCR015-RSRC-001 | 検索済みの2ページ目を想定した表示値。Users見出しと追加リンク、Username・Role・状態のGET検索入力の順、固定のRole・状態の選択肢、八列の順、件数と前後リンク、および行順と文字列エスケープを確認。 |
| PT-WEB-SCR015-RSRC-002 | 成功0件。固定の0件行と空案内。明細表と前後リンクは非表示。 |
| PT-WEB-SCR015-RSRC-003 | 入力異常と未検索の表示用値。エラーをエスケープして既入力を保持し、件数、結果表、空結果案内、ページリンクは非表示。 |

期待値はUI225・236、SS313の表示規約と固定fixtureに基づく。Javaの表示集計やHTTP認可、検索実行、DBはこの資源PTの対象外。実行はPG41706のmanifestに環境、入力SHA-256、Junit結果、終了コードを結ぶ。製品Javaをロードしない資源試験のため Java coverage は適用外。
