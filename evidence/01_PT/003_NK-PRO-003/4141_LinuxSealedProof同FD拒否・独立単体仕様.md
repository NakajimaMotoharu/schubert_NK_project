# LinuxSealedProof reserved dup同FD拒否・独立単体仕様

Program NK-PRO-003 / WBS-P003-06 / BUG2840・YKT2404。RD FIL001009/OPS009・UI251・SS333 nativeFD補足、SS342343・SSC308を正とする。

PT-OPS-SEAL-009（新1定義、未実行）: public fixture originalを128/129/65535に設定しdupが同値を返す。期待は固定StorageIoException.UNAVAILABLE、callback0、当original closeが一回だけ、公開inputと書込byteは元VECTORと一致。独立根拠はSS333の「同じFDは新所有でない」、close期待はliteral順序 create→mode0600→write→seal15→dup1030/min128→originalclose。production methodでexpectedを生成しない。original8のgolden/assert・defaultoriginal17は保持する。

既PT-OPS-SEAL-001～008の負値・範囲127/65536・別129/65535・partialIO・各syscall失敗・同一unknown・native/並行の全期待は不変更。追加仕様は既SS333違反の是正で外部能力/権限拡張なし。

実行条件: whole LinuxSealedProofTestはactualnative/FD/Root等HOLD、抽出・代替authority fixture・試し実行・再試行をしない。新Testsourceの作成/静的レビューを実行済PT/PASS/coverageにしない。静的確認は対象sourceのformat/Checkstyle/PMDと許可された非初期化解析を別slotへ記録する。全counterは未測定null、実PT/例外/資源後条件は未実行。正式1964PT/53scope据置、個別受入0/工数null。対象source・command・hashは製造と静的manifestへ記録。
