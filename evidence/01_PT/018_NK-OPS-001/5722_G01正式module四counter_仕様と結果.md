# G01 正式module四counter

NK-OPS-001、WBS-G01/G08、SS354・451第4節。新規正式収集の006が読む既定のJaCoCo module XML計七領域。PT-OPS-G01-MODULE001は固定された2packageの合計と行8、method3、class2、branch2を検証。うち1packageに分岐が無い場合も、moduleに分岐があれば成立する。002は必須4種類それぞれの欠落、重複、分母0を拒否。003はpackageの合計不一致、重複・欠落、負数と未知種別を拒否。既表示の補助counterもmissed0条件を維持した。

PG42812、dev-foundation、対象commit1d497691cd。Python 3.14.4、収録工具116件全成功。PG42762の固定済みProtocol元XMLは14package、line3551／method751／class162／branch1080、全missed0の再照合に合格。旧処理がBRANCH欠落を受け入れたことをメモリで確認し、修正後は同じ入力を拒否した。製品PT・coverage実測は再実行していない。仕様どおりの正式収録は全同source・全実行・静的解析の前提待ち。入力・command・終端と結果は [PG42812 manifest](evidence/PG42812-formal-module-counter-canaries-v1/manifest.json)。BUG-3624、YKT-2849の工具範囲を完了。
