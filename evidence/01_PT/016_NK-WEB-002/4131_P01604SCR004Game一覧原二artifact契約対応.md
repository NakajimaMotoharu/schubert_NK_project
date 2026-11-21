# P01604 SCR004 Game一覧・固定順・0件200

NK-WEB-002。対象source/hash、承認設計commit/hash、独立期待値/TestIDは [PG27650](../018_NK-OPS-001/evidence/PG27650-game-screen-two-contract-v1/manifest.json)。

- P01604-PG01 / GameListViewModel.from/Card / PT-WEB-182..193: AlreadyverifiedGAMRSP01 only, nonnullprincipal/list/elements constructorinvariant, 0/1/10allowed11rejectfixedinvalidgame size. Immutablecopysnapshot, preserveAPIrecordorder(display_order), no manualN1/N2sort orduplicateelimination. CardclosedGameCode/wirevalue/title only andfixed/scenarios/NUKITASHI[12] URL; toStringredacted/display-onlyTopbar, nevercacheauthorizations orcontext.

- P01604-PG02 / scenarios.html/ScenarioHierarchyController sharedP008 / PT-SCR-001..016,SCENARIO-HIERARCHY-DOM: GET/scenarios/GAM facadeoneverifiedcallthroughsharedP008, USER/ADMINprotectedbychain; 0102 invalidhandler thenimmediatereturn/no secondrender. SCR0040games successful200 empty該当するデータはありません; childrenSCR005006empty404 aredistinct. FixedScenarioGames heading/currentpage-specifictitle/brandspan schubertNK/escapedgamecode-title/no thutext, fixedsearchlink+sharedpostlogout/CSRF; exactCurrenttitle/actualHTTP/CHR-U02 remainendingproof notinferredfrommarkup.

- P01604-PG03 / sharedTopBar/layout/security/wire boundaries / PT-WEB-142..147,PT-SCR-001..016: P01507Topbar/layout andP01502session/role/CSRF, P008 typedGAM/layout/stringbyte checks eachownedonce. ModelconstructordoesnotauthorizeorqueryDB orrepairrecordordering. Filter/session/verifiedwire/actualHTTP/actualDB/CHR/451 same-source end dependencies remainunaccepted; nofeesfor redoing sharedexistingpassedordinaryproofs.

SCR004 ownedGameVM/scenarios.html全文と現SS313321/UI221223234を対応、0/1/10record許容11拒否/nonnull集合要素・immutable/preserveAPIorder/typedGameCode固定URL・displayonlyを明示。Game0件は200空文、Route/File0件404とは区別、GAM単一要求/0102即終端/escape/共通brandLogoutCSRFは各共有責務を参照し費用重複0。旧PG24370全64/24452全resourceDOM入力hash不変を照合して旧source限定参照・再実行0/旧成功新source合算0、exactCurrentpageTitle/実HTTP/DB/CHR/451終了は未受入。原/1だけ完了、障害追加/Code変更0。

実行: `python3 -B evidence/01_PT/018_NK-OPS-001/input/1736_game_screen_contract_audit.py` metadata終了0。新規製品PT/coverageなし。原/1の準備だけ、原/2・451・元190未受入。独立期待値は公開設計の固定境界・順序・後条件に基づき、production methodで生成しない。正式1964PT/53scope・工数null。


## 現行Game一覧テンプレートの独立資源PT

PG41642の既存階層表示試験と別に、PG24452に含まれない `scenarios.html` とlayoutを独立したメモリfixtureで描画する。根拠はFUN-004、UI223/234、SS313。

| Test ID | method | 入力と独立期待値 |
|---|---|---|
| PT-WEB-SCR004-RSRC-001 | displaysGameCardsAndSearchInApprovedOrder | NUKITASHI1／NUKITASHI2をこの順に供給。固定タイトル・検索リンク、コードと表示文、各作品へのhref。山括弧とアンパサンドを含むタイトルが文字列で表示される |
| PT-WEB-SCR004-RSRC-002 | rendersTheEmptyMessageWithoutInventingCards | 空fixtureで固定の該当なし文言と検索リンク、作品カード0 |

実際のHTTP、ownerとDBは別条件。実行source、JDK、SDK、資源hash・結果はPG41694に記録する。
