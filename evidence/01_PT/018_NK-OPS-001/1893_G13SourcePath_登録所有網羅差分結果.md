# G13.07・現source path登録網羅差分結果

保存時追記：終了event2125後の公開delta初回commandはPYTHONPATHからpyflakes runtimeを落としたため、import段階ModuleNotFoundError/exit1・OUT未作成で終了した（製品試験/scan判定は未実行）。既tool不変更で所定runtimeを戻したcommandだけ再実行する。文書追記patchの短縮context不一致一回はwrite前の原子的失敗で、corrected patch以外の変更なし。元ENDを上書きせず後続checkpointへ環境/構築再試行を追記する。BUG対象の実装済み製品仕様違反は確認されていない。

2026-10-25 11:33 JST、source64446a9f8901084a4ad7eba1f66ae975eb2bbdea不変更、WBS-G13.07/G13_CURRENT_JAVA_REGISTERED_OWNER_GAP_V1。1892の事前見積 .25/.5/1pp・cap1を維持。元941論理dataset ac5dee93/歴史943 dataset38247ee2/PG9288の256限定rowは不変更。

|source set|現Java path総数|明示登録あり|未登録|
|---|---:|---:|---:|
|main|965|961|4|
|test|824|120|704|
|合計|1789|1081|708|

明示登録1081は元485論理参照847＋current256のうち追加候補234。限定256はconfig/pom等も含む別分母であり、1789へ単純加算しない。製造Main物理1843もJava pathとは別単位。登録率約60.4%は本表の登録状況だけで、PGPT完成率・PT実行率・正式trace達成率へ転用禁止。UNKNOWNは元論理又はcurrent256明示rowに無いという意味であり、既resolver規則へ一致し得ないことを示すものではない。

未登録の内訳はprotocol main2/test21、bootstrap main2/test56、storage test29、API test210、batch test221、Web test167。各path・当source hashとmodule/sourceSet・owner/costは9304 sourceRowsにあり、UNKNOWNのowner/costはnullのまま。pathから推測割当・費用付替え・試験不実行との同一視0。次の具体的な独立工程はmain不足4pathの既承認RD/UI/SSとProgram責任の照合（登録根拠のある範囲だけ）、その後test704をProgram/TestID単位で対応させる。当群は所有割当や全method多対多joinを実装/受入していない。

原計測PG9304-g13-registered-owner-gap-v1/manifest.json SHA256 **bf0371f1eb4a85462ee8db6b265814fe933038b9084243aba933ada81ba162f0**、CLI0。normal9246入力のcurrent/snapshot hashを1789pathで照合。独立PG9305-g13-registered-owner-post-v1/manifest.json SHA256 **d7e18d48aa6ab253b3ce981c06dba02a7caf850e892c66ae7b96ee6b41141b03**、CLI0。Git当source tree/blobを分母とし全1789hash・論理所有/明示costを再構成、元audit/resolver helper非import。欠落/重複/unknown推測owner/cost一field/source/正式受入/unknown count/工数推定のmetadata反例8を拒否。製品PT成功件数には加算しない。

コマンドは各toolのinvocation.actualPythonCommandを正本とする。共通環境はLinux host/Python3、PYTHONPATH=tools/quality:tools/quality/vm/050_s1、元compile JDK25.0.4/Maven3.9.12の公開manifest9246参照・再buildなし。実行日時/source/入口/全loaded helper hashは各manifest。pyflakes（TC3.4.0）対象3tool指摘0、既compile/static/arch/4222PT/現在JUnit再演0。最初の補助読取で工具dirの推測path不在、続いて旧toolへのrg一致なしで終了1が各一回（metadata構築/診断2、製品障害/回帰失敗ではない）。是正はrg --filesで実在path確認後の読取で、製品code修正/BUG追加0。

PG9302開始event2124、終了はPG9306参照。開始fresh62→11:33:12 fresh62残38/reset1793382075、丸め共有差0は無料/専有0ではない。usage afc27d4e47c57544f4697ebc409d590e77ca1c67a5a4763aa841b34875ff6eef、専有N/T・工数率null/欠測0補填なし。元90の捕捉下限87/不明区間2/正確null、次もfresh照合・下限＋cap＋保全2<=90が必要。原/v4/v5不変更、当群受入/新ID/Main/coverage増分0、全G13.07/451未受入、正式1964PT/53scope・QA051final・実VM等HOLD保持。
