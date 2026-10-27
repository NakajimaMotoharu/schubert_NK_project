# 残Main非空理由22・現在source照合仕様

候補ID訂正（BUG1926/YKT1675）：v2理由は隣接06162を含むが既参照一のためindex v1がactual1/OUT前に拒否。別v3理由は現未参照の06163（shutdown内same Thread判定）へ置換。06161/06163が当対象、既06162は再加算0・既参照を保持。元v2成功とv1失敗を保存し、後続はv3/v2 indexへ明示pinする。

事前前提訂正（BUG1925/YKT1674）：v1はExpiry stage/finishにも無関係な8c全file一致を要求してactual1/OUT前。旧記述を履歴として保持し、新v2は各理由の実origin（6048/8c又は6354/aed）へ個別一致を要求する。Expiryはaed一致・8cのread差を保存、他七Main/四helperは両方一致。製品source/元理由/期待値/PG/PT結果は不変更、成功確認の再演0。

群REMAINING_MAIN22_NONEMPTY_REASON_REAUTH_V1/event2594、WBS-F03、原.75/2/5pp cap10。source7f035ccfe89c46e8f4fae52099b1c0e4e890e66b、正式1964-53/17-190/工数率nullを保持する。

PG11600固定22ID：LogCleanupService十三、ExpiryAuditRepository stage/finish二、AuthContextCodec local map一、InspectorEnvironmentFiles/FixedNativeCoverageStopHold/Web三classのidentity比較六。既参照の同class十四を再加算せず、PG6048非空十九＋PG6354非空三に限定する。他の空理由・未分類は保持する。

独立期待はorigin/main SS314§7.2.6（同repository instance）、SS332のSQL/unknownと局所scope差、SS341/343のcallback thread/共有期限/終端区別。source/補助classは旧8c/aedとの全byte一致と現在normal snapshotへ束縛。Logはprecommit rollbackとcommitted後guard失敗を区別、Expiry stage/finishの固定変換/TWR・同handle readbackはreadのSSC310順位と機械統一しない。Auth mapはconstructor-local→clone/Map.copyOf、後続private lockと消去契約を維持。Thread/指定repositoryの同instance比較はequalsへ変更しない。

既後続1362/1981/1994/2046/2065/2100/1918/641等を候補索引し、関連sourceと必要補助を読取確認。現PGの意味は契約と一致し当scope変更不要。これはPG省略ではなく当22指摘の適用性判断で、新PG/実行PT/coverage/Root/実接続/実shutdown等を追加計上しない。旧runtimeを新sourceへ流用しない。

`python3 -B tools/quality/pg11123_checked_python_entry.py tools/quality/pg11600_remaining_main_source_reauth.py`、11602 metadata負例、11604現在集合、11605独立全履歴/原row/負例へ。Java text/既公開JSON/設計読取と新metadata保存だけで、class load/constructor/callback/Session/crypto実行・鍵・実DB/VM/Root/native hook・サービス/file操作・保留工具/Graph9/deferred8へ進まない。新fixture/harnessや拒否操作再演なし。

全source/座標/message SHA/理由非空・元row identityを要求し、SOURCE_REBOUND_CURRENT_WHOLE_PENDING/raw保持。正常と同じ負例を生成前拒否するBUG1924対策を継承、元失敗byteは不変。metadata負例を製品PTへ加算しない。実行環境・command/終了はinvocation、path/hash/結果は2234。全F03/451/実所有・停止・CHR/native/QA051final等の残存条件を維持する。
