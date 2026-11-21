# P01605 SCR005 Route一覧・prefix・0件404

NK-WEB-002。対象source/hash、承認設計commit/hash、独立期待値/TestIDは [PG27654](../018_NK-OPS-001/evidence/PG27654-route-screen-two-contract-v1/manifest.json)。

- P01605-PG01 / RouteListViewModel.from/Card / PT-WEB-182..193: CallerbindsnonnullclosedGameCode, verifiedRTERSP01 only; nonnullactor/list/elements/max50 and51rejectfixedinvalidroutesize. Immutablecopies/preservebackendPrefixascendingorder/routeName/fileCount asreturned, Webdoesnotsort/rebuildCurrentRouteName map. Prefix typed0..99→exacttwoASCII viaLocaleROOT02d, title prefix: routeName, href/scenarios/NUKITASHI[12]/NN, fixedup/scenarios, no untrustedURLorcontext/authobject. 0records legaldisplayvalue only; controllerownsHTTP404.

- P01605-PG02 / scenario-routes.html/sharedScenarioHierarchyController / PT-SCR-001..016,SCENARIO-HIERARCHY-DOM: GET/scenarios/{game:NUKITASHI[12]} separatednumericdetailroute; unknown/nonASCII/pathmismatch404beforebusinesshandler. RTE facadeone requestwithboundgame/currentactor, verifiedresult0102terminalimmediatereturn, zero routesCurrentcompatible404 notempty200. FixedgameRoutespage-specifictitle/closedgameheading/subtitle/brand, escapedtitle/game/filecount+files, gameup/searchnav/sharedlogoutCSRF. ActualHTTP/routebinding/404/role/CHR proof unacceptedhere; model+markupaloneinsufficient.

- P01605-PG03 / sharedGAM/RTE/page/Topbar/security / PT-WEB-142..147,PT-WEB-182..193,PT-SCR-001..016: SharedP008query/wire validation andP01502auth/API0102/P01507layout feeonce. APIownsrequestedgame/responseassociation/DBCurrentprefixname andrecordordering; WebownsclosedURL/readonlydisplay/empty404controllerboundary. NooldPTsuccessconfirmationrerun/newOriginal12count/currentSourceunion oractualDB/nativefile/Root/VM operations.

SCR005 ownedRouteVM/scenario-routes.html全文/UI221223234SS313321対応、nonnull/cap50・51拒否/immutable/元順序・routeName/fileCount維持、typedprefix0..99をLocaleROOT2ASCII/固定href/back/search/titleとescapeを個別期待値へ記録。View0件valueとcontrollerRTE0件404を区別、閉game正規route/numericID非衝突/単一要求/0102即終端は共有責務・実HTTP未受入。旧Hierarchy12含むPG24370全64とPG24452resourceDOM入力不変の原scopeだけ参照、再実行0/共有費重複0。原/1のみ、原/2のactualAuth/wire/DB/HTTP/CHR/451終了未受入、障害追加/Code変更0。

実行: `python3 -B evidence/01_PT/018_NK-OPS-001/input/1740_route_screen_contract_audit.py` metadata終了0。新規製品PT/coverageなし。原/1の準備だけ、原/2・451・元190未受入。独立期待値は公開設計の固定境界・順序・後条件に基づき、production methodで生成しない。正式1964PT/53scope・工数null。


## 現行Route一覧テンプレートの独立資源PT

PG41642の既存表示モデル試験と、PG24452の資源範囲を確認した。PG41690が欠けている現行 `scenario-routes.html` の資源実行を記録。UI223/234、SS313、FUN-004に基づき、当テンプレートとlayoutに固定のメモリfixtureを与える。

| Test ID | method | 入力と独立期待値 |
|---|---|---|
| PT-WEB-SCR005-RSRC-001 | rendersApprovedHeadingRoutesAndFileCounts | game=NUKITASHI1、03と09の二ルート。固定title・見出し・副題・ナビ、2桁href・順序、文字列としての山括弧・アンパサンド、`3 files` と `5 files` |
| PT-WEB-SCR005-RSRC-002 | rendersEmptyAndFiftyRoutesWithoutExtraNavigation | 0件でカード0、00〜49の50件を元順序で描画。両端hrefを固定文字列で検証し、ページ送りを表示しない |

実HTTPの0件404、owner、JMSとDBの後条件は原仕様の別範囲。実行source・JDK・SDK・resource・結果hashはPG41692に記録する。
