# 保持inode reader試験のcompile・最終割込coverage

2026-09-12、PG-D-152。BUG148先行b3031f2c、BUG149先行5d2348b3。Productionの意味変更なし、試験code/故障注入の修正であり失敗runを合格へ変更しない。

| 実行 | 結果・独立根拠 |
|---|---|
| 探索1 21:15:11 JST | testCompile失敗で新8件未実行。generic Boolean戻り値のassertTrue overload競合。raw log SHA256=1ea471639670aa83f9e4a8ce9f33b5ae2842631fda6b6a6171816c717dbb0026 |
| 探索2 21:16:59 JST | 全129 PT成功後、最終interrupt line107のbranch1未網羅でverify失敗。read直後のinterruptは実FileChannel.sizeが先に検出していた。raw log SHA256=b273fe9efb204129a2cc23698cdf5dc305827525249d73b5c62a3ff7c0251ea4 |
| 探索3 21:19:01 JST | 129 PT/4coverage100%/静的解析PASS。boolean localで所有確認を維持、最終readonly観測後にも割込を追加 |
| 探索4 21:21:21 JST | raw IOException＋close時のraw診断を追加し129 PT/4coverage100%/静的解析PASS。新reader4class/21method/98line/92branch missed0 |

EFILE008は開始割込・実IO途中割込・最終metadata後割込を独立に確認し、全てflag維持/非成功/owned資源解放。EFILE001はborrowed rootが生存することを明示booleanでassert。単一新reader試験の注入/型付け修正で、他Productionへの同一原因修正はなし。collectorの新reader所属9class/OPS8group/全79PTは独立019 inventory・欠落/重複/未知/非PASSで検証する。

正式PT-WEB-20260912-02/source27698d4865da64a174c59e8c80acbe131c0df3d8（21:24:02～21:31:24 JST）で全1125件・6 moduleの4coverage100%・Production静的解析成功、017/019全17負canaryと12collector/35scope同run/source/hashを認定したためBUG148/149完了。探索logは環境pathを含むためGitへ全文を置かず、固定診断/日時/対象/hashで追跡する。Program/工程/実root配備完了は宣言しない。
