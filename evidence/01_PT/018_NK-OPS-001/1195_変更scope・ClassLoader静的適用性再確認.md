# PG5760 変更scope・ClassLoader静的適用性

- Source: `9463db1ac23437043facf95b87f64b9fc7e758bd`、WBS-F03、PG5760-changed-context-v1。PG追加変更なし。
- RD-NFR品質、SS311/343/351/352、PG-D435/439、1194の個別適用性分類を継承。拒否PTの代替ではなく、静的警告の適用前提の審査。PT実行加点0。
- 入力はPG5690の元380個別理由、PG5758の371再束縛、PG5750の全849source/1664class、installed PMD7.28の一次rule。全1582診断のID・順序・警告を保持する。

| ID | 対象・独立した判定根拠 | 実際 |
|---|---|---|
| F03-CTX-5760-01 | BackupUnitStartClientのthread5、InspectorUnitSnapshotのmap1、SystemManagerObservationのthread4/null1。宣言済みnested enum private名以外sourceが完全一致し、各outer class全byteも同じこと | 11件一致。mapはmethod-local builder→Map.copyOf、pending=nullはclosed確認後だけ。threadはJ2EE管理前提が対象外、並行安全や実停止の証明は別 |
| F03-CTX-5760-02 | RootStartupContext$NativeIoのthread1。完全source tailの一致、行移動量、元qualified/current actualclassのhash、CP番号と隣接paddingのみ正規化したjavap opcode | 1件一致。外側Rootの挙動変更やdebug差を無視せず、それらの実経路成功は主張しない |
| F03-CTX-5760-03 | WebHttpServer.startWithOwnerのparent loader。installed UseProperClassLoaderはJ2EE premise。SS311/343の自己JVM・own-release classpath・embedded Tomcatとの適用性 | 新規1件CONTEXT_NOT_APPLICABLE。WAR/EAR/foreign TCCL/plugin互換性は非主張、rule抑制0 |

実行: `PYTHONPATH=tools/quality:tools/quality/vm/050_s1:/home/mini/codex/project1/work/toolchain/pyflakes-3.4.0/runtime python3 -B tools/quality/pg5760_changed_context_review.py` 終了0。
工具unit3件成功・pyflakes0。negativeはenum外挙動変更、NativeIo末尾変更/重複宣言、opcode literal/branch変更を拒否する。Production PTへ加算しない。

公開manifest: `evidence/provisional/PG5760-changed-context-v1/manifest.json` SHA256 `12669fc9fb3f225310894b08c430f38c07dd6ffd9f76a029c0a752cd967f6737`。
全診断: 同`findings.json` SHA256 `d993f89240539ebcd1116000a1115ad3bb8a6ee63c360c58ac3658702fd5775e`。

再確認12、新規判断1、source再束縛候補384/未review1198。**当3932全体の元XMLへの接続は未完、F03/451/正式受入は未完**。旧PTやnativeを輸入せず、静的判断を実測coverage/PASS/所有・資源後条件へ代用しない。原v3/v4・開始0.25/0.75/2pp固定、消費専有費N/T/工数率null。VM/実DB/failed-cohort/intent/permit操作0。
