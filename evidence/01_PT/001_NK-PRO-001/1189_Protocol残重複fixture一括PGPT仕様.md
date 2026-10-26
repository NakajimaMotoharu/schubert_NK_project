# 1189 Protocol残重複fixture一括PGPT仕様

2026-10-27、event2469、BUG1869/YKT1620先行。主責WBS-F03、P00103/P00201/P00301参照費追加0、開始2/5/9pp cap10。source1f20074c/Main21d7の原97指摘のうちTest duplicate59を一括是正し、小さな定数単位の工具/六正常反復を避ける。原見積り/費用・既受入17は不変。

対象は原PG10690全finding indexにあるProtocol TestのAvoidDuplicateLiteralsでSemanticFieldValueTest以外の全59。各findingの元source SHA/ID/初出行/実Java文字列token/参照数を固定し、意味名private static final String一と全同値token置換だけを許す。日本語/Unicode escape/固定wire ID/大文字小文字・分解Unicode/他assert/fixtureは不変。Production methodをexpected producerにしない。Main変更0、設計修正不要。

独立逆展開は生成planの期待変換関数を呼ばず、固定宣言を除去して識別子を元literalへ戻し全Java tokenを原sourceと照合する。誤定数値・無関係assert変更・宣言欠落のnegativeを拒否する。formatter後source固定、必要六正常/現Protocol全静的、具体的安全性と既成功source差を照合した通常Protocol PT、元JUnit XML/exit/CRC/session/完全counter/traceを独立に確認する。F/E/S/aborted/flaky/not-runを成功へ算入しない。残38指摘を抑制/未分類0としない。

候補PTはProtocolだけのmemory codec/型/例外identity/有限golden classpath読取/自作byte stream/限定concurrencyであり、元Graph9/Root/DB/VM/HTTP/JMS接続/実file/credential操作を含めない。23Test sourceと実呼先・resource/副作用を具体確認後にcatalogを固定し、未確認部分は起動しない。元保留Test抽出harnessを作らず、現在module sourceに対する必要回帰・coverageを目的とする。既8実行を算術加算せず新scope元結果で確認する。

期待値はSS322323/333/UI232～237のoffset/lengthからの固定vector/保持されたgolden TSV/明示literal/JCA digest/JDK日時で独立。branch/null/例外/並行/再送の非該当根拠を実Test毎に残す。全物理Protocol176の実counterと無実行memberを各exec別に列挙し、未達/CRC不一致を成功や除外へ変えない。全moduleの独立oracle/G01/451資格は別criterionであり、普通PT成功だけで正式認定を更新しない。

実command/日時/OS/JDK/tool/source/branch・期待/実値・終了code/XML・coverage/hash/関連障害を1190結果と各manifestへ記録する。原本DB/Backup/鍵/stash/Current baseline/元成功失敗証跡・保留二fileを保持し、外部状態UNOBSERVED_HOLD/正式1964-53/17-190/工数null/QA051finalは不変更。fresh残10%以下又は取得不能では新規着手を止める。
