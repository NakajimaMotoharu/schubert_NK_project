# 4686 SSC-470 API Outbox単一型付き解放の単体テスト仕様

- Program NK-DAT-001／NK-OPS-001。OutboxObservationRepository.read、型付き解放、Snapshot、借用呼出元OutboxMetricCollector.collect。
- RD171／UI252／SS332 SSC-470／SS351／411／451、BUG-3292／YKT-2597。元WBS-P004-05/2とF03/2-2。
- 前提は純メモリJDK JDBC ProxyとローカルのMicrometer SDK。所有・外部DB/driver、サービス、QA056/057/058の型や実経路は使わない。
- 元OUTBOXDB001～010・OUTBOXCONN001～008は1664/1668/3963の固定SQL、取引前提、1秒timeout、null・未知・重複・非正件数・将来時刻、UTC時刻境界、非所有契約、取得／read／closeのSQL/RTE/Error、一回解放・抑制順、有限並行、公開snapshotと再送が観測を作らない条件を原試験のまま保持。
- OUTBOXDB011は二つの独立Proxyで同じSQLExceptionオブジェクトを行read/行close、又は文設定/文closeへ渡す。JDKのThrowable自己抑制契約からIllegalArgumentExceptionを期待し、causeは元一次とobject identity一致。行側の場合は文の別SQLExceptionだけが新しい一次へ抑制され、資源順RS→PS。文側の場合はRS取得や実行なし、文だけ一回解放、抑制なし。元一次のsuppressedは双方空。固定入力・固定資源履歴を使い製品コードで期待値を算出しない。
- 候補固定後に5186のprestyle→prepare→static→preflight→run→独立post。コンパイル、JUnit XML、同一runのraw/nonfiltered四counter、静的、既公開ABI、旧入力一致と支援行の不足をPG39606で記録。合否・候補git・run時刻・環境・証跡SHAは実行結果4687を参照。全451、実DB、正式受入は別条件。
