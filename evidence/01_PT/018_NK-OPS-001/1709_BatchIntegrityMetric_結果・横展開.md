# 1709 Batch integrity metric 結果・横展開

1708 INTEGRITYMET001..008/PG-D566/group1929（手戻り1930）、当検証source `5ac3d6a18d8c3ed4c6c5a0c70466b9f8d4553340`。新製造8＋必要既Batch245の当253/33。初期sourcef9dは253case/FES0でもbundle gate exit1であり合格扱いしない。別source Web51/API130・初期失敗のcaseを合算0。

| provisional原run | 真正結果 | manifest SHA256 |
|---|---|---|
| PG7788-integrity-metric-host-v1 | 初期253case/FES0、追加依存getter L1/M1未網羅でverify exit1 | 64fb9d04a836a1fe0d478e7e00150131e123a77a56f7282d1bfb055255454dc5 |
| PG7792-integrity-metric-six-compile-v1 | 初期sourceの正常六compile0/PT0・歴史保全 | 56ba3adac2b7b95c249506e025f15c002dafec9cfae64d78e490ad1b087d6c58 |
| PG7802-integrity-metric-host-v2 | Test補完後の当253/33/FES・flaky・rerun0、verify真正0 | 54a5a8f5f322eb58635df94279b2113d6a173cc674557c287df234e4daf13415 |
| PG7804-integrity-metric-six-compile-v2 | 当source正常六Main/Test compile-package/NullAway0、PT0/UNRUN | 6cbe02a5c1aeb15b5f423fad535c930dd94c6a773887f7ab07cc8b9092d3ad1b |
| PG7790-integrity-metric-post-v1（7806明示依存verifier） | 67Java/実63＋metadata1、同一exec/session CRC0・L947 M219 C63 B435全miss0、SB-CS0/raw既28-新0 | 37cbd4239538d378a060c475fadd7a0151fe99f73046985376161f6d8e36a448 |
| PG7794-integrity-metric-six-post-v1 | 全1772/元1669debug不変、当monitoring63physical＋元1669内依存1・歴史API26-Web14、三POM/SDK/五rule0 | e7a67d6ca91ea0b8f168fd9f15e9401c218383ed72936fde65e3786cf89468d9 |
| PG7810-integrity-metric-trace-v2 | 全119追加source/103追加physical・旧117不変2新、元依存1を別owner/sourceへ結合・六世代metadata負例 | 8916b963b9bc844588d8057a78c996e8306d9ca0fff00353a7358a4640834cb6 |
| PG7798-integrity-metric-review-v1 | 生成既120＋新Area2＋当元依存2=124当ordinary/javap、raw28全個別理由chain/五domain負例 | f424ed86a5ebf39b2ef95ee979186de22ddac8791f27947179d2e9bd78acf668 |

元sessions47452/60825の失敗/compile-onlyと、修正後5196/5087/1551/36140の真正終端を別回収。日時/OS/JDK25.0.4/Maven3.9.12/branch/source/command/actual exit/全input/原XML33・253一意case/実exec/CRC/SDK4とnormal API専用2の分離/counter/static/hashは元manifestへ結合。実VM等UNKNOWN/HOLD、チャット/session終了をruntime成功へ読み替え0。

## BUG1674 / YKT1425：追加の元依存を隠さず明示

既BatchMetricRecorderのstepはmonitoring.BatchMetricContract.Stepで、今回importしたrepository.BatchStepとは別enum。初期scopeがこの違いを見落とし、harnessへ暗黙compileされた後者のbackup()が未網羅となった。修正前起票/元証拠cde30b746を保持し、修正5ac3d6a18ではProduction Mainを変えずTest001にSS341の二backup=true/他八false、全typed values/配列分離/valueOf/未知/nullを追加した。新製造8とTest補完手戻りを分離、期待値はSS十stepから独立、除外/閾値変更0。

7790は新7806で固定Repository source一件を**追加包含**し、全実class63/physical64・全67JavaとPMD/CS/実SpotBugsを同sourceで検証。7806全codeは既coreと固定source追加/そのprovenance以外完全一致と7798で検証し、原core/既run改変0。監視部品だけは62実class/L932 M216 C62 B435、元Repository依存は1実class/L15 M3 C1 B0（実際に分岐なし）で、同一execから合計L947 M219 C63 B435を実測した。別runのcounter合成ではない。

元依存physical SHA06e90b35/CRC3a814d328e8e73bfは原1669/current正常Jar/当execと一致し、元1669内を追加physical103へ二重加算しない。ownerはWBS-P017-02、当依存再資格の追加共通費0/親WBS受入0。既metricの別Step型を確認し、当Main/Test/post・class/source inventory・raw全未網羅検索の全対象を是正/非該当へ分類した。Testだけの必要再実行後、global bundle正常0/全counter0・生成元依存2直接契約を実証して当範囲CLOSED。

## BUG1675 / YKT1426：485の歴史/原current世代を区別

元7796はrecursive path検索で485のroot歴史artifactsとcurrentPhysicalCandidate.artifactsを平坦化し、一意sourceを誤拒否（exit1、成功manifestなし）。元工具ed7f6a1dを52bc391d8へ保持、new-only7810で是正した。起票時のJAVA/CLASS仮説は後続読取で誤りと判明し、915/916へ訂正履歴を先行追記した。実際は**両JAVA**で、root歴史source7fff/SHAf139と、original-current e7/SHAf736という別世代である。

7810はJSON階層/source/対象path一意/kind JAVA/同owner P01702/各hashを別検証し、両sourceのGit実byteへ結合。current source SHAf736のみ当5ac/normal/execへ結合、歴史SHAf139は保持して転用0。current欠落/重複・hash/source/owner alias・未知kindの六負metadataを拒否、7798の五domain負例にも元依存の二重計上/owner/source偽装を含めた。119 deltaは元から正規Git差分/別class tableで生成され今回recursive485検索をせず非該当、全対象と非該当を確認して当工具範囲CLOSED。253普通PT/正常六compile/CRC/全Jarの再実行0、485原本/Production不変更。

## 品質と残り

全raw28は旧7712と属性・行位置が一致し、既64source/61physicalのdebug byteも一致、旧7720の25個別理由chain＋Mode三field理由へ当source/現在253を結合。新Main/元依存のraw0、未分類/適用違反0・抑制0。既生成120は同byte/JDK/公式filterと当普通suite、新Area2はINTEGRITYMET003、元BatchStep2はINTEGRITYMET001のtyped独立契約とcurrent javapへ結合、四counterへ算術加算0。

群開始3/5/9pp上限10/fresh5→6残94/reset1793382075、同窓共有観測差1ppは専有費でなくN-T/工数null。原見積/v4/v5不変・旧markerlast27区間/共有累積null/元90再基底化0、usage39cb1888（05:23:16JST/explicit0/完全性未証明）継承。供給三area×十step event Counterだけで実検査/調査/修復/自動close/退役/原本/Backup/DB/key/VM/Root/配備操作0。正式1964/53/原190新受入0/QA051final/PTALT0/whole451-native-CHR未受入、原保全物/stash7/Scenario3/Currentbaseline保持、工程全完了は宣言しない。
