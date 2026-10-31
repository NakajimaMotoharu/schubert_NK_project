# Storage18件global参照接続結果

2026-11-01 08:16 JST、PG-D1071。仕様3340、事前event3603の1/3/6pp・cap10を保持。Source6b53efeec87f3ec36a840dd8e7759656cb4aee5c、HEAD353b106aを基点とする品質工具のみの追加。

- PG17152-storage-pmd-identity-join-v1/manifest.json SHA256 `d0a07853a00831db903c91b2e462506be251e33df28a622ff4b292e0a5b003c8`。checked entry `e02650f0ba2a022cb73985ea45075097492a760ebbbaaa3825d4001b1416727b`、元終端504168、lint/body/終了0。
- PG17154-storage-pmd-identity-post-v1/manifest.json SHA256 `dcdb2a44fc1c72ad095744060d89f0ccd28c78f9002d3ceacf41d3d8effc96d1`。entry `a832e674655585ceb98e4fe369ab93f4c367a40745f4ec2a37ab67fc1dbafb7f`、元終端e14a06、lint/body/終了0。独立再構成18行、メタデータ反例23件成功。製品PTのPASS件数ではない。

全pathは `evidence/01_PT/018_NK-OPS-001/evidence/provisional/` 配下。pg17152のlinks.jsonとremaining-selected-review-queue.jsonのhashは一次manifest、一次hashは独立manifestに結合。原review、raw XML、current全Main観測、旧queueのhashはinputManifestPinsに保存した。通常commandは `python3 -B tools/quality/pg11123_checked_python_entry.py tools/quality/pg17152_storage_pmd_identity_join.py` と同pg17154。いずれもnew-onlyであり確認目的に再実行しない。

原18行/14署名/重複超過4を保持。重複該当8行は候補集合を明記し個体対応を推測していない。identity2のordinalはPG14664の原XML領域であり、global XMLのordinalとして転用しない。原14665はrawがnested schemaのため15930の直接参照対象になっていなかった。historical reviewのpending値は書き換えず、本接続を後続証拠とする。

当群の新規実績：参照接続18、purpose/reference706→724、selected reference610→628、未接続785→767。新manual review0、製品PT0、解析再実行0、Source/Test/設計/抑制変更0。raw18/qualityGate1/actualApplicableViolations null、F03・451未受入。既26PTは元証拠参照のみ。固有2606/377、四100% Source284/physical428、正式1964PT/53scope、歴史17/190、工数null、新WBS受入0を保持。

共有観測は開始used70・08:16 fresh used71/残29、reset1793774153同一、短期null。共有1表示ppをPGPT専有費又はtoken数としない。実配賦/N/Tはnull、cursor92b62f7e…/次09:06:16を維持。当群は既レビューの参照接続として記録し、見積減額・再認証・新規受入と混同しない。

新BUGなし。RootFailedSource・二held・原本・stash等の保全と全actualHOLDを維持。次は既fullSource同6b proof16620を再利用し、MorningStartupLaunchOwnerTest原whole3の具体sequence/fixtureを残確認して許可済みホストPTへ進む。API/WEB実起動・実stopの許可を意味しない。
