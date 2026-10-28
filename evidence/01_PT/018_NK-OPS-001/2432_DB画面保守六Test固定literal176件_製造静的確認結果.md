# 2432 DB・画面・保守六Test固定literal176件・製造静的確認結果

2026-10-28、2431/PG-D783/BUG2041/YKT1789。source1762d68747c3460afd90a03377858572dfc25931（六Test private compile-time String176だけ、Main不変更・未配備）。新TestID/新physical0、Product PT0、動的DB/file whole NOT_EXECUTED_HOLD、coverage NOT_MEASURED、実行免除/代替PASSではない。

|工程・元owned session|公開manifest（evidence/provisional/配下）|SHA256・真正結果|
|---|---|---|
|修正前原本、49045|PG13224-db-web-literal-v1|a7c19b56ac51963b29115de3b5a4aab715f5317fa20f4bc8957d340af10997c2 /0|
|全source逆/194反例・PMD/CS、8698|PG13226-db-web-literal-v1|f27a3f8cb48dd642c6c125355b7a34db2eac4b4b8ef98654fef9df7a6ba4c729 /0|
|当source六normal、82066|PG13228-db-web-literal-v1|3919599fe1f9798297a75b209802f656f3af603af3ed0df21f114e1dc0c39e74 /0・PT0|
|fresh六static、3629|PG13230-db-web-literal-v1|5f9866229ef228a4a83831dbc65184149158d36fe82f20bda49b38fdf967a8f0 /0・PT0|
|独立全物理/176定数、16038第一entry|PG13232-db-web-literal-v1|831b167d07a65a79ca3df889b26ca36423c50c055a88a559cdd8d53ce4f6860e /0|
|独立class binary/静的分母、同第二entry|PG13233-db-web-literal-v1|a32d5d6fc28df9fb963b6ea3216074836caee553911ddd5c70e310895ee14d6f /0・8反例|
|995中六SHAだけ、3229第一entry|PG13234-db-web-literal-v1|0787176b50c51f1dd2dd8722cbf8cf4771304b2d28fb95248b35b56a783ef402 /0|
|WBS独立、同第二entry|PG13235-db-web-literal-v1|fd1c42b5a7b64282fcd307de9ae27934ebbf3ef41413deb213f3736b0db881d0 /0・8反例|

## 確認した範囲

原静的448rawから176だけ消滅し、他272を元集計schema（message whitespace/埋込行位置）で一致確認、PMD自体は4/rawgate1を保持・Checkstyle0。raw文字列/全assert/処理順/例外/所有/全Test methodは原全文token逆で別に保全し、診断schemaの正規化をコード値の正規化へ広げていない。全176値＋各file assertion binding/Test annotation/終端の194非同値反例を拒否した。BUG2037で得た原schema補正と実行前全hash保存を初回から適用し、工具失敗/再実行は0。

全1843Mainが元source6d7と同byte、既1974Test keyset不変、六SourceFileのclosure20class内18だけ変化・他1956同byte・新class0。追加private176 ConstantValue以外の全private/public metadata・全method形状が不変。rawCode表現にはCP index/debugの影響があるため意味差判定に単独使用せず、全token逆と正確なConstantValueを独立根拠とした。

fresh SpotBugsは既4.10.4/Max/Low、当sourceの新六JARと固定外部依存だけを解析auxへ束縛した。旧2430のruntime構成はtool byteだけの部品参照であり旧Product解析成功ではない。六新解析の対象はAPI467/batch645/bootstrap117/protocol176/storage80/Web358＝1843、全ClassStats集合が物理class集合と一致、BugInstance/MissingClass/解析Error各0。独立13233では全classfileの内部binary identityもPythonで検査し、同scope/全hash/typed counter・八反例を確認、対象classロード/実行/解析再演0。旧local snapshot経路・除外/抑制/低閾値化を使用しない。

## trace・未完・費用

995registryの六SHAだけ更新、他989row・全canonical owner/cost/旧runtime/unknown二/原WBS論理941歴史943/原見積は不変。原raw8143=Main1502+Test6641、累計原是正1282、用途参照3271・current-source再照合pending1118（当六sourceの既参照94を追加保留）・参照なし4872。actualViolationCountnull、全WBS audit1/HOLD、全F03/451未受入。正式1964PT/53scope・歴史17/190・新leaf0・工数率null/QA051final保留を維持し、静的成果や旧sourceのPT/coverageを新sourceの実測へ変換しない。

BUG2041/YKT1789は六Test全176のPG是正・当静的確認済だが、実DB/file wholeの動的再試験HOLDのため全面完了日なし。関連SS/RD/UI/業務仕様を変えていない。新sourceのTool build/独立確認をもって実業務/実Browser/CHR/native/IT/ST合格を宣言しない。

群2798開始、原2/5/9pp・cap10不変更、観測共有7→7（同reset1793774153・整数表示の差0であり真の費用0とはしない）、専有費/N/Tnull。主費用WBS-F03、六artifact元owner/cost/歴史費は再配賦0。今回原計画176是正、追加発見0、工具手戻り0、追加source再資格cycle0。使用cursor5b644587（20:36:05JST・新explicit0）保持。次点検used10/残10以下又は不明停止、保存push/次作業は最新456参照。通常小群/commit/PMO待ちで止めず継続する。
