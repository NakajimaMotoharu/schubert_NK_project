# Transfer容量の状態語彙とスナップショット 単体仕様

NK-SCN-001、WBS-P008-03/2、FIL/PER、UI237、SS333 §13、SS351。

| Test ID | 対象 | 独立した入力と期待値 |
| --- | --- | --- |
| PT-SCN-008-C04 | TransferCapacity.snapshot／Snapshotの値契約 | 8,192 byteと7ファイルで初期化し、独立値(8192, 7, NORMAL)と対称等値。bytes・files・levelを各一つだけ変えた別値は等しくない。別に構築した等値のキーで連想表から取得できる。値診断に現れる要素はbytes、files、level。4,800 byteを一件予約すると現在値(12992, 8, NORMAL)。先の観測値は8192と7のまま。予約解放で元の集計へ戻る。 |
| PT-SCN-008-C05 | TransferCapacity.Levelの閉じた語彙 | 固定集合はNORMAL、WARNING、CRITICAL。配列を書き換えても次の語彙取得に影響しない。文字列CRITICALは同じ定数、未定義UNKNOWNはIllegalArgumentException。 |

JDK25.0.4、JUnit Jupiter、製品の通常局所入力5型を同一execの対象とする。既存6件を新2件と同じexecに選択し、元PG43072のexecを合算しない。予約はJVM内のカウンタだけを使う。FileStore、実ファイル、配備、運用接続、保持原本は対象外。原定義PG43072、残る測定箇所と実結果は後続manifestへ記録。
