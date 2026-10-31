# 現release collector Map三 用途レビュー仕様

2026-10-31 / PG-D1001 / 主WBS-F03 / 開始0.5/2/5共有pp cap10、freshused55/rem45。保存2048d20f2/push79242真正0。残Map三は旧12260のwhole Source不一致で参照対象外としたまま、現ReleasePayloadVerification395行とStartupReleaseManifest424行を全文読み直し、新静的用途として扱う。先行読む時間は選定調査/専有配賦不明、過去予算・判断を消さない。

Mapはjars/checksumsのprivate final instance field二とarchive callbackのlocal sql一。package-private final collectorは同package全18Mainのconstructor検索でStartupReleaseManifest.verify/verifyCandidate内の二つのinline new→verifyだけが見つかり、保存field/戻り値でcollectorを公開しない。callback/recursive walk/agreementは同じ局所collectorを使い、公開Contentsはinventory由来unmodifiable valuesを返す。archive sqlは順次構築しprivate JarValueへMap.copyOfする。Source-levelの現構成用途であり、任意の再利用・反射・別thread/実FS動作の安全証明に一般化しない。

旧d8a2から現6b53のMain差はPG-D804/sqlChecksum readLine loopの一回評価明示だけで、比較前後の全byteを固定置換で照合する。ただしこれは旧whole資格の転用ではなく、現全Source/readと新判断三を保存する。callerは同byte、原10690 rowSHA/全attrs/診断は一致し旧inputShaと現sourceShaを別々に残す。SS343 SSC095096の全BOM/immutable結果・検証と原本発行の分離を正本にし、このレビューでactual verification/署名/配備・permit/鍵・Root/DB/Backup/VMを呼ばない。

予定16198新purpose三→16200独立source/line/byte/field/caller再構成と26metadata反例。参照933不変、用途116→119、用途又は参照1052/1491、残442→439予定。UseConcurrentHashMap当queue残は0になるが全F03/適用性gateは未受入・違反null、新ProductPT/coverage0。現2144/289・四258-376/正式1964/53/工数null/QA051final/全HOLD不変更。
