# 1552 監視完成単位 全体compile・物理差分結果

2026-10-23、1551/同group1805の品質substep。Production sourceは元48PTと同じc285c38ac4fcc3f16bfd3d2051ec76c352227f74、operator HEADとは別に固定した。

| 原job | 真正結果 | manifest SHA-256 |
|---|---|---|
|PG7030-monitoring-six-compile-v1|六moduleのMain/Test compile・package0/六Jar生成、PT実行0/全UNRUN、元XML生成0|e795a9ca9ff3133f3e8aa0a32e615243847708486765073cd1a74a47101abe97|
|PG7032-monitoring-six-artifact-post-v1|六Jar全1684class、旧1669class byte完全一致・追加15だけ、当48PTの14実行＋metadata1全class hash一致。ArchUnit全1684/六module/五rule違反0|29419ec5a11421d466b9b5a960bc62210bfdc2f17a49d9e7037a06e485889963|

pathは各 `evidence/provisional/<原job>/manifest.json`。元archive/開始/所有process/子終了/log/Jar/classは `work/pgpt-runs/PG379/pg7030-monitoring-six-compile-v1`、独立static子のbegin/exit/stdout/stderrは `pg7032-monitoring-six-artifact-post-v1`。固定POM七件/plugin preflight・実command/環境/hashを元manifestへ保存。copy/migration/Unit/Root/noargs/実VM/DB/Broker/Caddy/鍵/intent/permit操作0。

旧e7/PG6930原資格728682a9の1669classは全てfresh Jarでbyte同一、debug差も黙認0。src差分は監視packageのMain8file（実装7＋package-info1）/Test6file/独立TSV1の追加15fileだけ、既存Main/Test/全POM/設定/DDLは変更0。追加physical15は全てBatch、主所有P018-09/C07共有費0、対応は7032 newSourceDelta/newPhysicalClasses。これで当c285の実48PT/CRC対象classが実Production Jarへ同byteで入ることを確認した。新class名の漏れ/未所属/旧byte差0。

ArchUnit1.4.2/SLF4J2.0.18と既五rule/tool sourceを原6960のhashへ結合し、fresh六Jarを静的importした。旧11canary成功確認の再演0、対象classのload/init/execute0、型依存の境界0。F03 Root11の意味reviewをしたとは主張しない。

重要：compile-onlyのskipはPT成功ではない。元4222/660を新sourceへ再認定0、全六/全scopeのcoverage union0。当14実行classの四100は1550/7028、旧全体の未達counterは未閉鎖のまま。新sourceの全体451/CHR/native/正式/485 current更新はまだ未受入。源泉別前回新7・歴史17・正式1964/53・工数null/QA051final/PTALT0/F03/actualHOLDを維持する。

本再開の具体成果はC07要求六群の対応確定と、純粋mode/metric26/alert72key/12threshold/単一pipelineの製造5段階、独立通常48PT/14実行classの資格と当source全六compile・実Jar接続。工程成果を元190受入5件・工数率や見積削減へ換算しない。以降は独立して着手可能なC02の未対応四設定の仕様/原source/Test不足を限定確認し、実Unit合成/起動/権限に触れない通常の設定PTへ進む。
