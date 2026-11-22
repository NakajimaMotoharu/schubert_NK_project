# NK-MIG-001 現候補のマスター出力マニフェスト

WBS-P019-03.02/2、RD141 MIG-DAT-003〜006、UI254、SS343 §10.1・SSC410。Java候補 b5d5009768a04bb69468beed2471441b2a57ce27。現在の単体結果は仕様140と結果141に対応する追加照合。

| Test ID | 承認設計から固定した条件 | 現候補の結果 |
|---|---|---|
| PT-MIG-COPYMAN001・002 | 固定六区分の順、行数、バイト数、小文字SHA、空6区分の既知SHA | 両件成功 |
| PT-MIG-COPYMAN003 | mappingまたはdatasetが欠落する場合の固定異常 | 成功 |
| PT-MIG-COPYMAN004～007 | 対応表があるfile、entry、speaker、audioの件数の各不一致を別々に拒否 | 4件成功 |
| PT-MIG-COPYMAN008・009 | 返却バイト配列の防御コピー、固定六区分の件数と不変性 | 両件成功 |
| PT-MIG-COPYMAN010～012 | 同じ六指紋でも別mappingは異なる結合SHA。共有入力の独立計算、固定redactionも確認 | 3件成功 |

六区分の指紋にはmedia assetsとentry audio linksも含む。四対応表との件数比較はfile、entry、speaker、audio。現行ログは移行対象外の設計であり、実データ抽出は後続で検証する。Asset manifestは別スコープで新1件と再利用19件。12件に合算しない。

COPYMANの失敗・エラー・skip・未実行は各0。型付き到達範囲39物理、対象一主クラス線41・method7・class1・branch14で各100%。Checkstyle/SpotBugs0、PMD生5は8workerの当該単体箇所に紐付け、全体の正式品質判定は保留。旧実行のcoverageを加算していない。

SSC417のPgJDBC COPY24件は仕様149/150の実行保留を維持する。実素材、Currentの原本、DB/COPY、現環境の所有・権限及び451が正式受入に残る。
