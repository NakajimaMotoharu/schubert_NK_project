# F03共通資源GenericCatch二十のsourceレビュー仕様

Program NK-OPS-001 / WBS-F03 / Main 28af318d0198fe7432ca6fcd234d3fabbfd10173。起点c2a260d、893の原見積0.5/1.5/4pp、上限5pp、ordinary。RDの品質・資源管理、UI237/251、SS333:17/27/29/33/35・SS343:785/787/789に追跡する。PG19830の型分岐38件とは規則・元ordinalを分け、再計上しない。

Test ID PT-OPS-GC20-001: ResourceScope acquire/use、各body/cleanupのRuntimeException/Error、計8観測。factory取得前null契約、取得後同じ資源の解放一度、正常return前close、既知IOと未知例外優先順位・固定secondaryを全method原文から確認する。

PT-OPS-GC20-002: ProcessResourceScope acquire/useの同8観測。IO/Interrupted/StopGate対unknown cleanup、interrupt復元、同一Throwableでself-suppressionせず固定secondary、factory未取得時のrelease無しを照合する。

PT-OPS-GC20-003: ConfigurationGroupResolver.scopeの同4観測。checked IO契約、unknown body identity、checked primary対unknown cleanup優先・割込flagと、呼出側のstdio逆順・TERM-before-join/buffer消去の責務を照合する。実NSS・process・reader終端は実行せず未証明。

PT-OPS-GC20-004: 独立metadata post。原PG19744 raw1491のordinalと全raw内容を固定し、先行307/今回20/残1164の非重複完全分割を別パスで再構成する。unique1439/duplicate52組を保持し、catchのRuntimeとErrorを同一行だからと併合しない。各Main SHA/全文method範囲/原文行/理由/未実施動的後条件を記録する。上位設計はorigin/main blobとworking file SHA一致・実行原文行で照合する。期待値は承認設計と原rawであり、production methodを呼ばない。

操作: env PYTHONPATH=tools/quality python3 -B evidence/01_PT/018_NK-OPS-001/input/022_owned_resource_generic_catch_context.py run、続いて同post。新unused PG19840へ一度保存。Python metadata処理のみ。Javaロード/fixture/実close/process/DB/HMAC/Root/native/VM・新JUnit/analyzer再実行なし。Main/POM/normal19740/SB19742/JARの不変は既存read_inputsの読取で検証する。

独立動的PTは各review行のrequiredDynamicPostconditionsに明記し、このレビューで免除・PASSとしない。coverage未測定、全F03/451未受入、適用違反総数null、正式1964/53・技術46・原80結合16・原282交差28・新leaf0・工数nullを維持する。不十分な理由があれば未分類を維持する。証跡: evidence/PG19840-resource-generic-catch-context-v1/{review.json,manifest.json}。実日時/環境/HEAD/hash/終了は元manifestと結果3530を参照。現HOLDとheldファイルにはアクセスしない。
