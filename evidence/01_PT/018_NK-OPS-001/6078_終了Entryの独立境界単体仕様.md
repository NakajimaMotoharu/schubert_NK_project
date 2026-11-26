# Cleanup終了Entryの進捗値・時刻・所有

NK-BAT-001、WBS-P017-07.03/2、OPS009・DAT009、UI251、SS331・332・341（SSC201）・343。対象はCleanupTerminalRepository.Entryの純値。64文字は公開固定テスト値。実証跡の作成・進捗参照・権限操作とは切り離して検証する。

PT-BAT-REJVAL009はCLEAN_LOGとCLEAN_INBOX_OUTBOXの成功だけ固定進捗値を許可。既存列・空の場合を維持。不正文字、63桁、空、別ステップ、SKIP、WARNINGは固定例外。明示getterで同じ値を保持する。
PT-BAT-REJVAL010は開始時刻と日時上限を含め、時刻前後、microseconds未満、不適用step、FAILED、引数nullを個別に拒否する。
PT-BAT-REJVAL011は独立に構成した同値で検索でき、終了時刻または明示進捗値の変化で別値になる。進捗値が空の診断では子のrun IDが出ず、AttemptとResultの固定部分が維持される。

現正規四JARの同一実行で関連11件とEntry／Snapshotの未加工四計測を採取する。実DB・原本・親操作、全体451と正式受入の結果は別に扱う。
