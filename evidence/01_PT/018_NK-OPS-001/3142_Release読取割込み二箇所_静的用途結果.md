# Release読取 割込み二箇所 静的用途結果

2026-10-31、3141/PG-D1009/BUG2167/YKT1914、Production6b53/normal14216/src不変更・実Product0。

|provisional以下のmanifest|真正結果|SHA-256|
|---|---|---|
|PG16266-release-interrupt-two-purpose-v1|b6cbed/現二Source・二用途/八metadata反例、終了0|9afbe28a7e0fb0197b81c4a2da781a55b9d81dbccf41577ec0f60bc448434cd7|
|PG16269-release-interrupt-purpose-post-v2|95819e/独立二byte span・26＋列端四反例、終了0|ecad14b7409828346ba4223bfe7929052ed1a4cb3a7ab95d5d84e81163ee7d8e|

先行3121/22のMain395/caller424/同package18読取と全二Source hashの不変更を再利用し、checked/read/固定requireだけを追加点検した。二Thread.currentThread().isInterruptedは直接のworker生成/start/sleep/割込みクリアではない。checkedはreader.checked前、readは各channel.read前にrequireで固定StorageIoException(UNAVAILABLE)へ拒否する。readではio.open/size/positionが最初の割込み確認より前にあり得ることをalreadyOpenedChannelPossible=trueとして明示、全I/O前拒否・blocking完了/親30分遵守/間接providerのThread非生成/実取消を証明したとはしない。

八metadata反例は両methodのguard欠落/状態クリアへの置換/直接worker追加/関連read後へのguard移動を拒否する非実行文字列確認。承認SS343は現origin/main同byte、原rawと現診断を全attrs・Sourceで区別し、新manual二であり旧6292理由の転用ではない。Main後方384行Unicode escapeは保持、既bounded ASCII prefix契約だけを使いfullSource hashを併存した。

独立byteはchecked222行・1-based半開column14..20=0-based9603..9609、read268行・22..28=11510..11516、各Thread六byte。旧16268/fb1622/body1はendcolumnをinclusiveと仮定して正しい元spanを拒否、BUG2167/YKT1914先行起票・旧工具/失敗manifest凍結。新16269は明示半開変換と二site各end±1の四負例を拒否、元16266/前16200の正しい原byte長・同byte/元成功を非該当根拠に保持、Product再演0。旧16268の未使用importはcb404b/lint1/bodyFalseの準備記録として分離。平台拒否/製品failure0、全対象是正又は根拠付き非該当/再発防止を確認し、実commit/push後有限閉鎖する。

参照1171不変＋用途119→121=1292/1491、残199=generic192/thread5/emptycatch2。当二箇所はPG変更不要というSource用途判断のみ、actualViolationCount null/PT_EXECUTION_EXEMPT=false。実release検証/crypto/hash計算/署名/配置/Root/FS/Thread処理/DB/JMS/鍵/VM/native0。技術2157/292/480Source670physical/四260-381・正式1964-53/歴史17/190/工数null/QA051final/G07/G13/451/F03/HOLD不変更。

原0.5/1.5/4共有pp cap10・専有N/Tnullを保持、fresh18:36used56/rem44同窓・短期null/券0。共有丸め差を専有0とせず、実command/時刻/source/branch/hash/終了は各manifestに保存。次は未参照普通StorageAttributeGuardTest七（2275の自己所有TempDir/新0700親・SPI・cleanup契約を全文と元工具で再照合後）又は残F03へ継続する。
