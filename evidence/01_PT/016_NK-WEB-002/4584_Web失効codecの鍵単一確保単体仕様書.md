# Web失効codecの鍵単一確保 単体仕様

NK-WEB-002、WBS-P018-10.03、QA050、UI226／234、SS314／331／352、BUG-3484／YKT-2779。通常入力検証・CSPRNG・固定AES256GCM/AAD・既永続化形式・旧鍵保持契約は元仕様のとおり。

- PT-REV-KEYOWNER-001の独立静的期待。二世代の32 byte幅、paired、version、randomの事前検証後に一回だけ所有配列を確保し、固定範囲copy、closeで全体を一度消去する。旧二段clone／範囲外copyなしを原javapと新javapで区別する。実OOMは発生させない。
- 元RERUN003 A～G、REVOCATION OWN001、FATAL001～005。合成の固定JCA、旧鍵／現鍵、caller入力の後続変更、鍵世代違い、例外原形、nonce消去、closeと並行を同sourceの元13観点で検証する。
- 変更候補をRoot NullAway/Werror、Checkstyle/SpotBugs/PMD、CRC、独立生四指標へ接続する。実失効・DB・JMS・資格鍵の観測は対象外。正式451と区別する。
