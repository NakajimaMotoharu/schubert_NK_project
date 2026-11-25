# 公開証跡のstage参照照合 実行結果

PG44204。固定されたGit index treeから公開manifestと対象blobを選択する方式を追加。合成Gitは既存9＋追加3の12件成功、失敗／エラー／skip各0、終了0。作業ファイルだけの変更と欠落、明示旧commitのhash不一致を区別した。既存確定commit比較も同じ試験で維持。製品や全451の測定外。 [実行・ハッシュ](evidence/PG44204-public-pin-early-staged-verify/manifest.json)

## 明示pathの独立負例の結果

PT-OPS-PINPATH001。修正前1選択は失敗し、空pathを外部分類に数えた。修正後は五つの不正値をstaged、確定commit各入口で独立確認した。検証工具とscope guardの合成35件、関連索引の合成6件が成功。限定12公開manifestのpinは未解決0。製品試験と全451は対象外。 [PG44966](evidence/PG44966-published-pin-explicit-path-regression/manifest.json)

## 表現不能な明示pathの再試験

PT-OPS-PINPATH002。修正前は合成の公開相対形・外部相対形がともに外部に数えられ、二つのGit入口の比較4件が失敗。修正 e0392b5581 後は不正明示pathとして各未解決1、正常公開と正常外部各1。関連工具45件成功、現公開6manifest未解決0。製品PTと全451は別。 [PG44986](evidence/PG44986-public-path-representability/manifest.json)
