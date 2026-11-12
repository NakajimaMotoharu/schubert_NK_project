# Web認証value四件・現全166：実行結果

仕様は [4071](4071_Web認証value四件_単体テスト仕様書.md)。2026-11-12、branch dev-foundation、source840982bb38d1fe4ebb09fc492a4bef62a3656532、Production Main62960fc3b5d4a67cf7bd9df887b668169d10f87f（不変更）。PT-WEB-CLOSEDVAL001～004全件成功。元162＋新4＝166 found/started/success、failure/error/skipped/abort0。

実command: `PYTHONPATH=tools/quality python3 -B evidence/01_PT/018_NK-OPS-001/input/1345_web_auth_helper_qualifier.py run 840982bb38d1fe4ebb09fc492a4bef62a3656532`、終了0。独立: `python3 -B evidence/01_PT/018_NK-OPS-001/input/1348_web_auth_helper_independent_post.py 840982bb38d1fe4ebb09fc492a4bef62a3656532`、終了0。新source/Toolchain/command/実環境/各hashは [PG26818 manifest](../018_NK-OPS-001/evidence/PG26818-web-auth-helper-independent-v1/manifest.json)、branch/tool versions補足は [PG26826](../018_NK-OPS-001/evidence/PG26826-web-auth-helper-run-context-v1/manifest.json)。PG26818 SHA 3b50e6b5148e3de1c79b5c9c3103201e3c8b0e6a03e32062322a070e1a8d8d5c。

全197physical/CI187/code176/180positiveCRC、一session、旧exec合成/手動除外0。line3854/method810/class176/branch1180、instruction19066/complexity1427すべてmiss0。直前162のhelper4不足line32/method4/class2/branch35を新4の独立NFC/上下孤立surrogate/64byte/closedtoken matrix/例外constructor/原因graph identityで解消。自然Code0の17（package10＋abstract/interface7）と標準switchmap4は全入力保持、除外追加なし。branch0の固定exception constructorは自然N/Aでline/method/classを測定する。

Test freshcompile→PMD/CS/format。BUG2677の初回raw16（適用literal1）と旧compileは保全し、定数化後26808compile0/26810raw15全行文脈非該当・適用0/未分類0/処理error0/CS0/format0→26812PF0。Main197はsame-source/byte/旧NullAway/Mainstyle/SpotBugsを厳密照合し再buildなし。新4はthreadなし、immutable/stateless・呼出毎のgraph/queueをfixture所有とし、共有状態/外部競合は非該当。元8の100並行と二有限ownerは同166で再確認。実認証/credential/session/DB/key/HTTP/JMSbroker/Root/VM/actual四classは非接触。

[PG26820](../018_NK-OPS-001/evidence/PG26820-web-principal-global-owner-supplement-v1/manifest.json)でSessionPrincipal既guard/site33だけglobalYKT2328へ対応、当原因未完26→25。BUG2678の初回未公開caller guardはPG26822に保持し、[PG26824](../018_NK-OPS-001/evidence/PG26824-utf16-cause-taxonomy-independent-v1/manifest.json)正3/負3metadataで全35分類を独立確認。局所是正3/原因非該当3の別枠6と全owner closure flagsを区別し、他25/globalは閉じない。

前run162成功/未網羅報告はそのまま保持し、合成せず新166の単一runだけで判定。新定義4・新実行166を区別、metadataチェックを製品PTへ加えない。原P00706/2・実HTTP/DB/終了依存・451/元190は未受入。正式1964PT/53scope・工数率null。追加費事前.1/.3/.6のみ完了、P015共通実装へ二重計上しない。
