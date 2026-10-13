# BUG1221/YKT987 — PT-OPS-2256-001 / PG2260

NK-OPS-001/451/SS342343354/SSC234、Main3b7f不変更。旧準備2256（Git4403d8698）はInspector同session terminal/closing二点を10streamとしてunionするため、451に反し未受入。実native合算は未発行・counter影響0、修正前起票。

修正後は10pointをそれぞれ固定bytes/CRC/session/実世代時刻で検証し、Inspectorの同session-id/start・terminal<=closing・全early class id/name/probe長一致・既true probeがclosingでもtrueの部分集合を独立JaCoCo公開readerで検査する。terminalをcoverageに追加せず9stream/latestclosingだけを全counter/XMLへ同一採用。terminalのtail/実Main終端は独立port/ownedpostの別条件で、この選択によって合格化しない。

独立Java literal10vector=同一/true増分正常2、null/空/late欠落/classID違い/classname違い/probe長違い/true先頭rollback/true末尾rollback拒否8。expectedは固定boolean array、Production method0。NativePointDominance.java SHA49cccb1b449b44bfbc9386b7bebfd41bcf87733468f3bd98872967d85b03ec37、Test.java SHA49fce9bcda08f735d2af7c4b4be19a5f12ff2d50d86d73331d552c575a4ea661。

PG2260 actualjavac25.0.4/Xlint-all/Werror0→Java独立10vector0（exits[0,0]）、JaCoCo0.8.15、14:53:11.628429Z→14:53:12.270647Z。command=`python3 -B tools/quality/pg2260_native_point_dominance_host.py`、詳細command/hash/時刻/sourceはW/PG379/pg2260-native-point-dominance-host-v1/manifest.safe.json。最新選択Python test/全transport-server namespace/static0、sourceinput helper2も凍結archiveへ追加。

旧2198/2104二点は歴史診断のまま、2106既latest-onlyは別0fdSourceで新実績に合算0。2254は十pointのeligibilityのみ、2256の実monotonic/nativeCRC/九streamcounter/XML資格は今後の当bootRoot/DONE/ownedstop/post後に検証。したがってBUG/YKTはhost是正済・実再試験待ち、未完である。正式1964/53/全leaf0不変更。
