# 監視時間窓の通常試験と状態factory

F03/2-2、P018-09、NK-OPS-001、MON005～013、UI252、SS351 §7／10、PT-OPS-MONWINDOW001～008、GENB001～007。現Core `559f5b5945e82374e0843dcfae11a8d07faef1ea`。時間窓8件は1561、状態名・順序・lookup・未知値・配列所有の独立期待は1657の既仕様を使用。

PG24962の元23を再起動せず、その単一execと正規Batch JAR内の対象2 classを照合した。生はmethod 2／instruction 9未到達。関係する八時間窓と既七生成値試験だけを組み合わせ、PG41108で当候補を一回実行。成功15／2 suite、失敗・エラー・skip・未実行0。元execの合算なし。対象の生L18/M7/C2/B14/I127は各未到達0。当15件と元23件は別の実行として保存。物理classと実execの二CRCは別Python decoderでも照合した。

製品Main・試験source変更なし。承認済み閉包のJAR収録classだけを一時領域へ取り出し、実監視、clock authority、DB・Unit・Root・nativeを実行しなかった。周辺型・実経路・全451の認定は未成立。

実行 `python3 -B evidence/01_PT/018_NK-OPS-001/input/5586_f03_window_state_joint.py`。 [元／現の生測定と実行結果](evidence/PG41108-f03-window-state-joint-scope-v1/manifest.json)
