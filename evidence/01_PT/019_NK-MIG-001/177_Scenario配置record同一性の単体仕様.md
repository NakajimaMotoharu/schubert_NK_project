# Scenario配置recordの同一性 単体仕様

NK-MIG-001、WBS-P019-03.03/2、SS343。対象は `ScenarioEntryPlacementMap.Placement` と `PlacedEntry` の等価性とhash契約。PT-MIG-PLACE013は二つの合成入力を使う。

- 同じgame、file、entry、indexを持つ配置を二回追加しても集合の要素は一つ。indexが一つ違う配置は別要素。
- 全値が同じ二つの配置結果も一つ。出力file IDが違う結果は別要素。
- 期待する各追加可否と要素数2は固定入力の並びから独立決定。実移行、DB、実asset/fileは使わない。
- PG44118の既存12件と、この新規1件を一つのexecで検証する。既存12 Test IDは再計上しない。対象三物理の四指標とscope外の未確認を記録する。
