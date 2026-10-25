# 生成switch-map適用性・静的レビュー結果

2026-10-26、仕様020/群2240/WBS-G01。レビューsourceは8ba82083ec65abc6373b8454576dcbaee7d3e621、元の実行sourceはfd3d04df5710ca28f0e34f919cbc103e569a607b。新しい製品PT実行は0。判定は**全4class/未到達16probeの原因対応を静的・独立照合済み、生成codeの適用性承認・当sourceの動的資格・G01全体は未完**。

## 確認結果

|完全class（protocol配下）|CRC64|原probe hit/miss|未到達probe ID|対応するenum field|
|---|---|---|---|---|
|codec/PayloadCodec$1|160a2b21eaf8e770|5/3|2,4,6|WireType TEXT/NUMERIC/BOOLEAN|
|file/MediaDescriptorValidator$1|48e566e90c75eeb8|5/3|2,4,6|MediaType AUDIO/VIDEO/MUSIC|
|layout/FieldDefinition$1|208ba71a9840eb7c|5/3|2,4,6|WireType TEXT/NUMERIC/BOOLEAN|
|layout/LayoutFieldCatalog$1|11245607473ab8f5|10/7|2,4,6,8,11,13,15|Presence MANDATORY/CONDITIONAL/OPTIONAL/FIXED、WireType TEXT/NUMERIC/BOOLEAN|

全16はcompiler生成のNoSuchFieldError空catch（例外をASTOREで破棄して合流）に対応する。三enum/重複を除く10fieldは固定された当Jar内に実在する。全4classはCodeを持つsynthetic switch helperであり、Codeなし13classとは違う。JaCoCo0.8.15のSyntheticClassFilterはACC_SYNTHETICのmethod範囲を除外するため報告counterは0/0だが、未到達が存在しない意味ではない。

一次照合はASM命令一覧とメモリ内のprobe配置を使用し、独立postはPythonによる元execのbit復号とJDK javapの原bytecode/例外表を使用した。ASM命令indexとJDK byte offsetは別単位として保存した。元25hit/16missは変更なし。16probeを16branchと数えず、既102PT/22suite・実測159class/L3480-M743-C159-B1014各100を生成Code4の全命令資格へ読み替えない。旧1222の「17非実行class」はCodeなし13と非計測生成Code4へ明確に区別して参照する。

対象Jar/元exec/当normal/sourceをhash束縛し、Protocol全176classと三enumの当byteを確認した。reader JVMの実行classpathに製品Jarを含めず、対象classのdefine/load/init/invoke、変換byteの書戻し、agentの新規起動、enumの欠落を意図した不整合classpath fixtureを行っていない。実環境のBOM/classloader/世代の照合は未実施であり、これを固定artifactのfield存在から推定しない。

## 再現・原証拠

実行環境はLinux amd64/JDK25.0.4/JaCoCo0.8.15/ASM9.10.1。以下は当Programのevidence/provisional配下。各manifestに実command/開始終了時刻/工具hash/対象hash/実exitを保持。

- PG9842-protocol-switchmap-review-v2/manifest.json：4159dc3dda26a447e147b3c689de36e2052662fada0d9a87374a5fec4b208bed。`python3 -B tools/quality/pg9842_protocol_switchmap_review_v2.py`、exit0、reader Werror compile0、全16対応。handler-probe-map.jsonが一次表。
- PG9843-switchmap-compile-stop-v1/manifest.json：fec42a4eaa7c46f6c0d52c480153f60231ad42e75ff9b9aaf51298679151ee2a。元V1のjavac exit1を回収した失敗証跡。回収工具exit0を元compile成功へ転記しない。
- PG9844-protocol-switchmap-review-post-v1/manifest.json：a381c95d3636e10540f18d5f87fd3e7838ad136bbff8fc2858948e0bd5486980。`python3 -B tools/quality/pg9844_protocol_switchmap_review_post.py`、exit0。independent-probes.json、independent-handler-byte-offsets.json、independent-jdk-bytecode.txtを保存。独立exec parserの12固定vectorと8件の誤った対応/昇格拒否vectorは工具検証であり製品PTへ加算しない。
- 元PG9726-protocol-generated-shape-post-v1/manifest.json：c5e2b600dfadfca7c1a8a889fec5d605e775b7e75e36955bc4a70cf5298290b5。元exec sha6599384e9d11ee208180c1e762d8a07ca381ded3a54e2dfe4d1381f3a5e4530aを保持・書換え/再実行0。

BUG1767/YKT1518は元V1のLabelNode開始forにvarを用いたcompile時の型推論不備。reader実行前の失敗を保持し、別V2でAbstractInsnNodeへ明示した。他のgetNext開始走査は共通型で非該当、Werror compile・全四class/16対応・独立postまで工具scope確認済み、保存commitを台帳へ追記する。未使用Arrays import除去の編集はformatterが既に削除しており初回patchは変更前に不一致、実差分を確認して継続した通常編集手戻り。platform拒否ではない。

## 未完条件・非昇格

生成codeについて451/SS354が要求する独立した適用性承認は与えていない。新除外設定0、到達不能扱い0、原raw miss変更0。当sourceの実runtime/BOM/classloaderと同source全scope/全counter/native/CHR/451は別の残条件。Graph9動的HOLD、全actual/HOLD、G07残4493、QA051final、正式1964PT/53scope、個別受入17/190、工数率nullは不変。今回完了は16/16の静的な原因対応と未証明条件の具体化であり、正式受入や原計画のleaf完了は増やさない。
