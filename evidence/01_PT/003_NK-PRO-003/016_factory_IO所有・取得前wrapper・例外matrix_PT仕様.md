# NK-PRO-003 / SSC308 IO所有単体仕様（製造前仕様と限定実行追補）

2026-10-18追補：「製造前」は初版時点。現source6d7a54a01、factory001～012はPT-IOFACT-001～012に一対一、dirfactory001～003はPT-DIRFACT-001～003、RootEntryRejectionTest.guard004はPT-ROOTGUARD-004。DIR001は実kernel root inode/一度close、002はnull/取得失敗同一例外/未所有close0、003はclose失敗時FD消費と設定 '/'拒否。Root004はprimitive319/負値/取得例外/nullの所有境界を独立固定期待で確認。実222件と実bytecode/全storage四counterの結果・全失敗履歴・hash・commandは017を参照。新source全体/native/横展開の合格は主張しない。

主担当WBS-P003-08（ResourceScope）/P003-04（OwnedTransferDirectory）、Root/N15参照費0。RD FIL001009/OPS009・UI237251、SS333/343/354・SSC063/304/308、BUG1414/YKT1178。起点sourcee8ecの親全体/独立資格を先に回収し、凍結src/Testを変更しない。設計only9762b2da5→origin/main **b92c887e399b4b0e9ae8552045c0a5b1a425ae87/PR156**（四文書のみ、通常merge/remote確認）。群1180開始費.8/3/8共有pp固定、元/v3/v4/歴史受入を上書きせず、専有費/N-T/消化率null。

製造対象：ResourceScopeの新factory所有入口（全port構築検証→取得→即保護域）、OwnedTransferDirectoryの取得前wrapper/EntryHandle確保・同FD openRoot・保護下transfer、RootServiceExecutableAdmission/RootStartupPendingの同一取得経路。既ResourceScope.use、取得失敗のchecked型・identity、取得後IO/unknown/複合例外の既優先順位を維持。設定path '/'拒否・NOFOLLOW・名前・mode・非上書き・sync・exec前正常close・caller権限/期限は不変更。

期待値は以下SS333規則をliteralの呼出列・同一object・固定messageで直接assertし、旧use/新acquireをexpected生成に呼ばない。fixtureはresource identity一つ・open/live/close計数と公開markerのみ。例外は各組合せで新規objectにし前caseのsuppressedを持ち越さない。

|Test ID候補|観点/入力|独立期待値|
|---|---|---|
|PT-IOFACT-001|正常・nullable body結果|construct全port→open→body(same R)→close(same R)各一回、戻り値identity/null保持、live0|
|002|Acquire/Release/OwnedActionの各null|NPE、open/body/close全0。NPEをcatchして正常化0|
|003|factory戻りnull|NPE、body/close0。資源なしを正常結果にしない|
|004|factory checkedIO・StorageIO全Reason・Runtime/NPE/Error|同一object/型を伝播、body/close0、checked Eの狭い型もcompileする|
|005|各portの構築fault（明示Error注入）|helper入場/acquire前の故障、open/body/close0。実heap OOMEを発生した証拠と呼ばない|
|006|body IO/各StorageReason、close正常|StorageIO固定transfer storage operation failed/cause無し、元storage reasonはsuppressed無しだけ保持、close1/live0|
|007|body IO＋close IO/各StorageReason|UNAVAILABLE固定、raw secondaryを出さず、close1/live0|
|008|body IO＋close Runtime/NPE/Error|secondary同一objectを優先、追加close0・一度close/live0|
|009|body Runtime/NPE/Error＋close正常|primary同一object、close1/live0、suppressed増加0|
|010|body Runtime/NPE/Error＋close IO/unknown/同一object|primary同一object、secondaryは固定StorageIOの秘匿suppressed一つ、self-suppression禁止/既suppressed順保持|
|011|body正常＋close IO/各StorageReason/unknown|IO正規化は既rule、unknown同一object、close1、成功に算入0|
|012|nested scopes/並行独立resources|内→外の順一度close、各identity/例外優先順位独立、global mutable hook無し/資源live0|
|PT-DIRFACT-001..|新openRoot/null/factory失敗・既directory全機能|同FD一度消費、未openのclose0・再試行0、既path '/'拒否/NOFOLLOW/segment/CREATE_NEW/sync/transferと全失敗後live0。個別method/TestIDは実fixture確認後追補し、未定を完了0|

Java25 actualbytecode条件：全callback portのinvokedynamic/newはfactory open前、acquireの返却直後はnonnull確認とslot格納から保護域へ入り追加new/invokedynamic/boxing無し。OwnedDirectoryのstateLock含むwrapperはopen前、EntryHandleはprimitive取得前に確保してconstructor内部はfield格納だけ。生FD取得→box生成のgapを作らない。Root全同path/順序/metadata/pin/borrowed context・明示exec前closeは旧sourceから照合する。

実施：PG5128/5130回収後→Test先行/製造→六format→新固定選択PT/実Directory FD・旧ResourceScope/Root各case/static/coverage/bytecode→必要な新source全体/当source実経路/native。既sourceの50や旧nativeを新source合格へ算術合算0。新helper全四counter・境界/例外を測定、除外/意味ないassert/安易な抑制0。実command/環境/日時/source/run/exit/XML/TestID/hash/input/expected/actual/coverage/BUGを新manifestと結果へ保存する。

横展開：固定e8ec候補68file237siteの元source/行hash/主担当は`evidence/provisional/PG5134-scope-candidate-inventory-v1/manifest.json`（SHA9f9c80a5968d5f9a6010e98fa74854c17777c99076eb98d11e3f4e4129870344）。全siteは未判定を明示し、所管外側owner/保護域/transfer/borrowの各修正又は非該当理由・実再試験を記録するまでYKT全体closeしない。Root/共通directoryの限定是正だけで残候補を完了扱いしない。

本仕様時点では新Main/新PT未実装・未実行。工数率null/正式1964PT53scope/歴史17・190は不変で、新sourceの個別criteriaは再認証が必要。既受入の旧source記録を成功転用せず、BUG1414是正前のsourcee8ecは署名/配備しない。
