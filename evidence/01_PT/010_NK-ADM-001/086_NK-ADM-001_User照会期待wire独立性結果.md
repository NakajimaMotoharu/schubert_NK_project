# 利用者照会expected独立性・限定結果

2026-10-26 14:37 JST、source8788668513552ce50862797cb700d2b7a4162ac1、Production Main21d7c304不変。085仕様/BUG1814～16・YKT1565～67/PG-D679、群2353→2354/G03.01/原P01001関連0、開始1/4/9 cap10。Java25.0.4/Maven3.9.12/PMD7.28.0/Checkstyle14.3.0/GJF1.36.1、環境詳細とcommand/stage終了/hashは各manifest。

公開pathは `evidence/01_PT/018_NK-OPS-001/evidence/provisional/` 下。

|path|真正結果|SHA-256|
|---|---|---|
|PG10308-expected-helper-context-v1/manifest.json|非共有expected70site/五source、15新gap/14既是正/41当文脈欠陥認定なし、製品PT0|07dba3164cb081544a34d190ae4b0f4a133d64c5a20b9b1eeb168e790d6a71e8|
|PG10310-user-query-oracle-static-v1/manifest.json|raw19/CS0/processing0/exit1、原保持|c3ac86a0dff588ebb0339e2e8e27aa2579fccaede3a2caf3a48ce2e6d7a9d2a7|
|PG10313-user-query-literal-plan-v2/manifest.json|五literal定数化・逆展開全token一致、元plain class保持|5a4797dd4e394e2dd0d4e9b2be72b58fb1e8112fc12b11ff65033f0654db4d92|
|PG10314-user-query-oracle-static-v2/manifest.json|duplicate五解消/raw14/CS0/processing0/exit1保持、新helper指摘0|58b872c710117d6d22c4fbca689f933af8c6657cba8a0b34d4c287ccf34111ba|
|PG10316-user-query-oracle-metadata-v1/manifest.json|27whole-wire vector/未知形式三/配列独立、exit0、Production classpathなし|d45fd41a41e7daa58149c568dba1a7411f114e7b4d84a1b309ad0f1e1d32c7bf|
|PG10318-user-query-oracle-six-compile-v1/manifest.json|当source六jar正常compile/NullAway、exit0/PT0|04ac980e0ed4a2b18e83dd41521bfe9adda035251b7ce8ca6f3a90b9fae89942|
|PG10320-user-query-oracle-post-v1/manifest.json|14caller/七fixture条件/元assertionとbyte配置保持、全Main1843/他Test1940同byte、当二outer変更＋新helper一|3d06dba306747ab6039845c106e185e103102fd4d441ac257f684eb66cdb0d36|

元PG10312 plan/emitはfinal class固定markerのため各exit1/OUT生成前停止、source変更なし。BUG1816修正前起票・原工具保持、V2はclass名部分だけ一意照合して既plain modifierを保持し、元token逆展開を維持した。製品再試験なし。誤ったsession73096参照はUnknown process idで操作なし、実static31091/metadata65711は元セッションから真正終端1/0を回収した。

raw14はf.sqlFault=null五（optional Test fault解除）、checked Exception→AssertionError callback一、try-withで所有するStandalone Test executor六、borrowed JMSContext Proxy一（実receiverは外側try-with owner）、Standalone interface loader一。当sourceの実line/text/hash付き個別文脈を10320 pmd-applicability.jsonへ保存、contextual applicable0/抑制0/rule変更0。raw exit1を0へ書き換えず、全F03/他sourceへ合格を拡張しない。

元Testの実PTはNOT_EXECUTED_HOLD、coverage未測定、メタ27/三を製品PASSや新TestIDへ加算0。原Query19定数化source4cの結果も別sourceとして保持する。当User二変更＋新helper、先行Query二SHAの計五pathは次batch traceまでpending。正式1964-53/既17-190/工数null/QA051final/全HOLD不変。
