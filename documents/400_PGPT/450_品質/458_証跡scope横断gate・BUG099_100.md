# 証跡scope横断gate・BUG-099/100

## 2026-11-23 新規収集と再照合

新規収集は `python3 -B tools/quality/018_collect_verified_evidence_set.py <新規run ID>`。標準出力先は作業ツリーの隣の `pgpt-formal-candidates/<run ID>`。既存の候補先は使用せず、別の未使用パスを指定する場合は `--candidate-root` を渡す。保存候補の再照合は同run IDと `--validate-only --candidate-root <既存候補パス>` で行う。終了値、出力先、53領域、出力の由来を確認してから正式公開を別途判断する。

既存正式証跡は作業ツリー上の既公開成果として保持する。PG42746で、旧正式公開commitに保存された53領域を読み戻した。対象は旧runの保全確認。

## 履歴

2026-09-20 最新確定: 正式PT-WEB-20260920-27/source3b980d71f5573342b7c787ad6eed53db6d8c2940、10:14:36～10:27:24 JST/Maven12:47/exit0、全1719PT（Protocol80/Storage82/API689/Web460/Batch367/CHR41）、failed/error/skipped0。6Java全line/method/class/branch100%、Production5 NullAway/Enforcer/Spotless/SpotBugs未解決0、固定path3method限定review継続・coverage除外追加なし、CHR SpotBugs未設定。JS1file全line/function/branch100%、18collector/41scope整合・81負canary成功。DB29/266＋Batch25/281＋OPS17/142＋QST2/16＋ASY1/5＋Web25/219＝99部分成果929PT（全1719の内数）、今回再開比+304PT/+34部分成果。PG215 Log画面状態8PT・PG216実template8PTを限定認定、BUG226/YKT182完了。LogのBrowser入力検査/ADMIN HTTPは未実装。BUG195/206/YKT154/162/SSC063、実archive/親/質問受付全体/残Web・本文controller-file/readiness/Logout/QA045/実NKgateは未完了。固定加重40.85～52.35%（中心46.6%≒47%、約41～52%）を維持。残量9%で利用者指定の停止、元dev-web3file保全、PGPT/IT/ST未完了。以下は履歴。

## 1. 正式26の非合格記録（修正前）

PT-WEB-20260909-26/source5b4d1d52は2026-09-09 12:58:59～13:05:13 JST、build exit0、930件成功・4種coverage100%・静的解析0。
しかし009 Media collectorが新api.fileの鍵reader12件をMediaへ混入しexit1。他collectorの更新後にMedia25と残り26が混在した。
個別hashだけではrun混在を検出しないことを確認。全体証跡確定・PG/PT完了の合格には算入しない。
最後の全収集確定は正式25/source6dd862d0/918件。26の部分証跡を消去せず、BUG-099/100・YKT-089として修正し新sourceで正式27を再実行する。

## 2. 修正前の独立期待値

PT-QA-TRACE-002: 共用api.file packageはMediaのAssetChecksumManifestTest/AssetManifestLoaderTest/HeldMediaFileInspectorTestの3classと、NK-DATのInspectorCredentialLoaderTestの1class。Mediaは61件を維持し、DB12件を含めない。未知class・Media内の未知method・欠落methodは拒否。
PT-QA-TRACE-003: 必須24scopeがすべて指定run/source/branch/exit0を持つ。1scopeでも欠落、別run/source、hash破損、collector非zeroなら全体の証跡完了を拒否する。個別合格と工程全体完了を分離する。
既存PT-QA-TRACE-001（017）はネスト相対参照/hashの負canaryであり全scope同時点性は保証していなかった。

## 3. 横展開・再現・結果

Production変更なし、RD/UI/SS変更なし。品質toolも対象sourceへcommitしてから正式gateを実行する。

| 対象 | 所属・非該当根拠と追加確認 |
|---|---|
| 009 Media | api.fileの3 Media class、1 DB classを明示分類。未知class拒否、Media全methodの完全一致を維持。61件から変更しない |
| 003 Auth | 全moduleの全試験/coverageを再照合し、api.securityの共通認証回帰を収集する。Program独占件数ではなく重複を含む回帰範囲。今回は新readerを収集対象としない |
| 006 Scenario | 全module試験のroot証明を持ち、共用storage全classを回帰として収集。native8件も共用能力回帰に含むがScenario独占成果や全体件数への加算には使わない |
| 007/008 | 明示classと固定method件数/Test IDの回帰、package所属の仮定なし。全体証明のhashとsourceを照合 |
| 010/015 | 明示class一覧とTest ID全method完全一致。共用packageを一括でProgram扱いしない |
| 016 | switchでProgramのsubject/class/Test IDを選択、root manifest相対path/hashを017で負検証。今回は035の12件を専用scopeへ格納 |
| 全24scope | 018が必須scope固定一覧で欠落/旧run/別source/別branch/非zero/hash不正/参照不正を拒否。収集の各exitをcheck=Trueで検査し失敗時に後続へ進まない |

探索確認: `python3 -B tools/quality/019_test_evidence_set.py` は3/3成功（独立4class分類、未知class/欠落・未知・重複method、24scope×4異常binding、ファイル欠落/破損/重複/参照/脱出、24各段のcollector失敗停止）。017の既存1件も成功。
実際の正式25/26混在treeは018のvalidate_allで「mixed or failed evidence run/source/branch」として拒否し、誤った全体証明を発行しないことを確認。
Python品質canaryはJava930件に加算せず、Java JaCoCo coverage100%をPythonのcoverageとして流用しない。
正式再試験27/source4bbb32deは2026-09-09 13:27:18～13:33:40 JST、exit0、930件全成功・5 Java module全4種coverage100%・静的解析0。018収集は全24scopeで同一run/source/branch・全hash/参照PASS、Media61/reader12を分離し期待値不変。017 1件/019 3件負canaryも全成功、BUG-098～100/YKT-089再試験完了。Current baseline/V001～013不変、秘密pattern scan0hit。個別manifestのslice成功表示も本set合格も工程全体完了を意味しない。

## 4. 再現command

最新正式32/sourcefa0d53b4: 987件/6 Java module、9collector/28scopeの同時点性/hash/参照までPASS。新question-queryは8 Test IDとshared9class coverage、SQL V015hashを収集。019の6件（28段各失敗/112bindingと8query ID負canary）＋017の1件＝7 Python PT。BUG-115の旧最終flagはquestion-queryへ修正し全段再試験。SQLは新4照会を含む28routeでありJava SQL coverageと混同しない。

最新正式31/source7efedb19は979件/6 Java module、9collector/27scopeの同一run/source/branch/全hash/参照までPASS。batchはrepository17＋Log全件service12の2class/29 Test IDを020で必須化。019は5 PT（新12 IDと2class集合の欠落/重複/別class等の負canary追加）、017は1 PT、計6 Python PTをJava979へ加算しない。正式30は967件/27scopeで成功済み。

追補: 正式28は25scope/942件、正式29は26scope/950件を全収集確認済み。PG-D-137のbatch追加では9collector/27scope・6 Java moduleへ拡張し、019は4 PT（batchの17 Test ID負canary追加）となる。正式30で初回全体確認する。過去24/25/26scopeの履歴を27へ改記しない。

PG-D-135追加時はinspector-processを必須scopeへ加え25scopeに拡張する。019独立inventory/全25失敗段/100異常bindingも同時に追加し、初回正式検証は28で実施予定。既存27の24scope完了記録を後から25scopeへ読み替えない。

source commitを確定しclean reactor build終了後、次を順に実行する。collector中もsrc/pom/characterization/toolsは変更しない。

```sh
python3 -B tools/quality/017_test_inbox_evidence_trace.py
python3 -B tools/quality/019_test_evidence_set.py
python3 -B tools/quality/018_collect_verified_evidence_set.py PT-WEB-20260909-27
python3 -B tools/quality/018_collect_verified_evidence_set.py PT-WEB-20260909-27 --validate-only
```

最後の表示PASS_EVIDENCE_SET_ONLYもPG/PT完了や実NK CHRの合格ではない。秘密scan/上位変更/障害/trace/PR等は451・456の残るgateで判定する。
