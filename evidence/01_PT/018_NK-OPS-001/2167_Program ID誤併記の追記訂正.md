# Program ID誤併記の追記訂正

2026-10-27、BUG1903/YKT1654。431の正規ProgramはNK-OPS-001、監視responsibility/cost ownerはWBS-P018-09。今回生成した2157/2161/2165仕様および11170/11196 completionで、未登録のNK-MON-001をProgram IDとして併記した。これは説明名の誤生成で、新Program作成・業務仕様/要求追加を意味しない。

2157/2161と11170/11196の原producer・manifestおよびそのspecificationSha256/sourceは歴史証跡として変更しない。原誤記を消さず、新metadata manifestで各path/hash/source/元実結果を保持したまま **effectiveProgramIds=[NK-OPS-001]** へ明示訂正する。既原34/46試験・static/counter/source/Mainbyte/原owner registryの事実を取り消したり、新source成功へ合算したりしない。

2165はまだcompletion seal前だったため原Program表記を是正し、11222 current completionは正規NK-OPS-001のみ。PG/PT実施範囲や原見積2/5/9cap10は不変更、追加発見/文書trace手戻りとして分離し、修正・metadata確認費を新しい元計画消化へ算入しない。正式1964/53・17/190・工数null・全F03/451/QA051final/全安全HOLDは不変更。

PT-OPS-PROGRAM-ID-META-001：431に正規IDあり・誤IDなし、明示旧spec/producer/manifestに誤記あり・各原seal/hash/source不変を確認。

002：旧両completionのsource/原試験件数/結果を保持し、正規Program対応だけ訂正。期待は431登録ID・既完了原manifestから独立、元製品再演/追加PT/coverage0。

003：未知Program/別source/架空新PT/旧hash変更のmetadata改ざんを拒否。全対象を列挙し未確認を完了へ含めず、実command/環境/source/exit/hash・関連commitを新公開11226証跡へ保存する。通常Linux/Python3読取metadataだけ、私有data/保留工具/実環境0。
