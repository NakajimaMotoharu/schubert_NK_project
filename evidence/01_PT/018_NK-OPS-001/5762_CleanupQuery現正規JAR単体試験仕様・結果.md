# CleanupQuery 現正規JARの単体試験仕様・結果

WBS-P017-07.02/2、NK-BAT-001、NTF-006/007/011・QST-009、SS331 §8.3・SS332 PG180、YKT-2864。CleanupRepository.execute／readLogProgress、CleanupQueryPortTest 10件、CLNQUERY010を含む。JDK25.0.4、2026-11-23 JST、dev-foundation、製品source `51e8da82333e56515e059e8f32d615cafeacff37`。

固定SQL・JDBC bind、時刻、各kind最小／最大／範囲外、保持・ロック返却、件数・進捗の欠落／重複／nullと未知値の期待は試験fixture側のリテラル。二入口のstatement／row取得と例外位置では、入力の到達と、一次の同一性、各解放回数と順序、借用Connection非commitを確認する。合成代理を使用。実DB、実削除、保持原本、正式451の判定は対象外。

PG42974、実行10／合格10、F/E/S・選択漏れ0。対象1クラスの無フィルター L102/M20/C1/B22/I403各不足0。独立decoderと単一execのCRC一致。旧試験sourceと現CLNQUERY010を含む原全体を合算しない。試験実行命令、入力、元終了、期待値、原XML／exec／公開レポート参照はmanifestに記録。公開SHA-256 `88e8637a2b7e63b0f689577a4274cc0eddb5494dd6c5170d2f10993283984e55`。
