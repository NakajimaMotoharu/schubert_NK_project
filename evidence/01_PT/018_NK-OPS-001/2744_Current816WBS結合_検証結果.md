# Current816 WBS接続・独立検証結果

2026-10-30 10:03 JST、仕様2743。Production6b53固定未配備。主費用F03、元.25/2/4pp。限定registry/WBS更新は完了、正式受入ではない。

|段階|manifest（本directoryのevidence/provisional配下）|sha256|真正結果|
|---|---|---|---|
|registry|PG14680-current816-incremental-registry-v1|2060df0aefd44244ce8a944c79d96e800fbcd8abe5ed3bcfbb0c64e4fe8d3b29|0、旧772全case/owner/unit不変＋新44/九Source|
|元独立工具停止|PG14682-module-index-stop-v1|本manifest自体を公開scanで固定|元body1/製品0、失敗は失敗として保持|
|新独立post|PG14683-current816-incremental-registry-post-v2|ada11a00d7ee4f5aea2c2881dd95dec2fdf086e09a661c4998ec8d9f77f6dbed|0、XML/実Jar全closure/metadata/20反例＋六module正常/四反例|
|二WBS追記|PG14684-current816-wbs-v1|e012b8e8941f0b6f6fc645b6040ca64c13679b11a887e4de13dd9fd94b00d35e|0、旧sideを残す新sideのみ|
|WBS独立post|PG14686-current816-wbs-post-v1|6274ce4c4203d4773e9b24c7b67cebfc162794f74a520b6d432d66fca5f632f0|session90565真正0、22反例・wholeaudit前後1/HOLD|

新side `typedGuardCurrentHostPG14684Overlay` を485二sectionへ記録、486はinventorySha256だけ更新。485 hash `8380360348b22b9cf9878434162894674c84c7cdbc1c47eeb0753b1df6b0ffb0`、486 `b0e3390afe333d6bfc3c67b7fc2c1f27ac938ddd552f6129eda7e6777c002e3d`。481/484・全旧semantic/runtime/費用/acceptance/旧side/元Catalog置換履歴は不変。owner299=147baseline/80candidate/72UNKNOWN、UNKNOWNを担当確定へ変換しない。

unique816/109suite、189Source254physical=243code+11metadata（五code-bearing synthetic/六trueNoCode）。四counter100は117Source180physical=170code+10metadata、自然branch0は67Source69physical、noCode1/1、未達4Source4physical（Inbound L10M2、User L8M1B2、Log L4M1、Question L15M1B6）。全Sourceの実execは単一、coverage合成0。初回43＋必要Catalog資格1=44JVM/延べ872method、再資格56を新規数へ加算しない。元772から新規44、うち今回batch5/六Source・他39/三Sourceは保存済み成果の接続。製品再演0。

BUG2108/YKT1855は修正前起票後、失敗14682/entry31e88270を凍結。新14683v2/entry42980c30はpackage/module/classを閉じた構文で検証し六module対応/未知module/別prefix/欠落class/aliasを確認。直近14680/14636/14638はmodule位置の抽出なし、shared postと14678は明示module tableで非該当（限定読取・既成功再演0）。元失敗はProduct/出力/WBS0、原発生時刻不明null・観測時刻と分離。限定工具修正と全対象確認は完了、修正commitは本書を含む最初の保存commit。

正式1964PT/53scope・歴史17/190・工数null・QA051final・全F03/451/wholeWBS/G07/BUG2092-93動的HOLDを維持。共有used31/rem69/reset1793774153/短期null、usage4099fe30（9:56）N/Tnull/専有費不明。工具手戻り・新規PT・source再資格を混同しない。
