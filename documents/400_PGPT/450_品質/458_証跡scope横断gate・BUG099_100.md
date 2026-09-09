# 証跡scope横断gate・BUG-099/100

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

調査・実装・再試験中。Production変更なし、RD/UI/SS変更なし。品質toolも対象sourceへcommitしてから正式gateを実行する。
