# 公開source metadata判定と段別failclosed

BUG3179/YKT2648、SS351354/451、Coding411。工具修正 .15/.40/.90 cap1.5、F03費用一回、追加発見/製品Source再資格と別欄。旧scan失敗37560とremoteに進んだ事実を保存し、書換/force/既存成果破棄をしない。

新工具はGit committed public deltaのみ・三既知形式のみ、protected二pathを必ずblob読取前deny、private/raw default denyを維持する。公開PG37538の一metadata pathを固定hash/厳格schemaで認証する。source path/sha/constructor行/boolean候補/status/既存PG参照だけのschema、unexpected key/私有path/型alias/hash不一致は拒否する。private word全体のguard削除や別経路で保護資料を読むことはしない。

negative selfchecksは許可path1と通常公開path、protected2・別private/raw・絶対/../・hash/schema不正を確認する。工具自己試験は製品PT/coverage/正式受入へ加算0。scanのexit0とmanifestを確認してから別commandで必要exactファイルをstage/commit、その成功後に別commandでpush・remote照合する。依存shellでの無条件後続は使用しない。共有枠token実数/専有費不明はnull、正式1964/53・17/190・工数null保持。
