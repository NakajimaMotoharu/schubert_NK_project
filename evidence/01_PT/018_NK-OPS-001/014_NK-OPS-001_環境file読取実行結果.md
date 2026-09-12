# NK-OPS-001 保持inode環境file読取実行結果

正式確定: PT-WEB-20260912-02/source27698d4865da64a174c59e8c80acbe131c0df3d8、2026-09-12 21:24:02～21:31:24 JST、全1125件成功。新reader8件・4class/21method/98line/92branch全missed0、6 moduleの4coverage100%・Production5 module静的解析成功。017/019全17負canary・12collector/35scopeの同時点性/hash成功、BUG148/149完了。環境/command/結果/Test ID・独立oracle/source/hashはevidence/manifest.json。本部品は借用rootのreadonly検査までで、private公開PG153は仕様のみ。以下は探索履歴。

013/PT-OPS-EFILE-001～008、PG-D-152。探索4（2026-09-12 21:21:21 JST）でStorage50/Batch79計129件、4coverage100%・静的解析成功。新readerは4class/21method/98line/92branch全missed0、実inode/readonly channel・合成root/GID/localFS・全IO位置/複合raw IOExceptionと初期/途中/最終割込・64並行を確認。BUG148（先行b3031f2c）・BUG149（先行5d2348b3）の修正後探索成功、017/019と正式PT-WEB-20260912-02の全体回帰・35scope認定待ち。正式01へ新8件を遡及算入しない。原子publish・固定namespaceの親結線・backup/SSC055は未完了。
