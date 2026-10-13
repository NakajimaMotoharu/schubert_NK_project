# BUG1240/YKT1006 親18 Source契約

NK-OPS-001／SS343/353/354、774/775続行。旧pg2457/session46585 actual1はhostSource admission通過後、guestpayload内部 `SOURCE=3b7f...` が当sealedbefore sourcecdbcと不一致で拒否した。durable公開projection無し、2459ABI/stage/stop未発行、guestwrite/Root/Backup/ADMIN/Unit/DBwrite0。旧2457は不変更・再演せず、操作の成功へ補完しない。

新PG2472 actualprojectionは当2456 beforeSHA42d9dabb9ede1da17018153cd82f1f731b26a3eaabc5d3426cd57aa0d0675d23／sourcecdbc／BOM6e06／親18全field名・string型・RootunitIdを固定。2458 consumerを新2472へ一箇所結合、2459/2460/2464/2466/2468は未発行のまま当current profileを維持する。Production/Main/current/baseline変更なし。

PT-OPS-PG2472-001：全actualpayloadで正常固定fixture、異なるbyte/hash拒否、旧source/null、旧BOM/null、foreign UnitId/null値/余剰/欠落/18個でもunknownfieldの反例を実行。expected hashは独立標準SHA256でfixtureから算出、production methodを呼ばない。immutable旧payload3bの再現literalを保持。全namespace static0。

PT-OPS-PG2472-002：producer/consumer全entry/Source/BOM/全seal/hash/親18依存を照合。2458当consumerは2472、2459未発行freezeからそのgraphを作成、2460実STAGE currentboot/SRC/BOM・親two-source prequalと別fullseal→stop順、2464独立retainedSource/BOM/全24を当sealへ結合、2466receipt保持＋旧16copy非輸入、2468当full3637/cdbc/全1643・九最新CRC/session、2470実A01 Currentdriver/baseline維持。旧sourceの歴史copy/旧run拒否/否定vectors・旧祖先は非該当で改変しない。

初期2fixture＋当terminal/rows/fullseal/owned/native全fixture=13成功（共通Receipt固定4を含む）、Source/BOM/shape十negative、static0。私有2457失敗は保存、真正親1722.989861秒DONE10/全24/whole/A01合格は独立証跡として維持。新actual2472→2459全ABI→2460stage/ownedstop→2464別post→2466/2468を実測して工具対象完了とする。全正式451/global100/CHR/leafは別未完、検索だけでYKT完了にしない。実command/commit/time/exit/hashは取得後追記。
