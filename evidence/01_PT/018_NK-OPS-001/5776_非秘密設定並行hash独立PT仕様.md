# 非秘密設定の並行hashを固定fixtureから照合

NK-OPS-001、SS352、WBS-P018-01/2、BUG-3669／YKT-2885。PT-OPS-APICFG005／WEBCFG005。各fixtureの承認済みGOLDENのUTF-8 byteをJDK SHA-256で変換した一値を期待とする。元001／006（基本値・公開雛形）とAPI007の独立算出も同一fixture内で再利用。32個ずつの並行hashを比較し、異常null、未知key、5秒の各待機と10秒の所有終了を保持。

当候補BootstrapのApiNonSecretConfig、WebNonSecretConfig、JdbcFailureGraphと補助Storage二classを入出力に固定し、固定の公開三雛形のみ専用領域へ複製する。原14件を一回選択し、同一source/runで終了・当該二Mainの生counter・静的結果を記録する。実設定・秘密・認証・DB・JMSは参照しない。

### 2026-11-23 JST 実行結果

PG43118-v1/v2 は検査例外の宣言不足で compile 1、JUnit 未起動。v3 の対象14件は F/E/S 0。生 L241/M25/C2/B150 全数。Checkstyle/SpotBugs 0、試験内有限workerのPMD生10を保持。[動的試験manifest](evidence/PG43118-nonsecret-config-independent-concurrent-oracles-v3/manifest.json)。PG43120 は同製品Coreの対象Main5入力に現親POMのJSpecify/NullAwayを適用し、終了0・物理6一致。試験は再実行0。[型付きmanifest](evidence/PG43120-f03-config-main-typed-current-v1/manifest.json)。実設定および全451は別結果を必要とする。

### 公開診断の原因・抑制確認（BUG-3670）

SS343／351、API/Webの003・004・007を既存の合成入力で選択実行する。固定メッセージ、原因null、抑制0を独立観測し、実ログ・実credentialには接触しない。実行 `python3 -B evidence/01_PT/018_NK-OPS-001/input/5776_p01801_nonsecret_oracles_current.py --version diagnostics`。PG43122で6成功、F/E/S各0、同runの部分counterを保存。[manifest](evidence/PG43122-config-diagnostics-no-nested-cause-v1/manifest.json)。
