# SSC-458 Canonical field／requestの一般診断

NK-MSG-002、UI231/234、SS324 §3／351 §12／352、WBS-P006-01、P018-10.03、BUG-3228、YKT-2677。CanonicalField／CanonicalRequest、支援Fingerprint／FingerprintVerification。PT-IDEM-CANONVALUE001..006のwhole純値は既存4 Main・6定義の独立16進／所有／正規化／不正値oracleを継承。001と004の診断期待を確定SSC-458の固定値へ反映した。条件の入力・固定hex・異常値の独立期待値は既元仕様を維持する。

PT-IDEM-CANONVALUE007／PT-P01810-CATALOG-006/007。合成field 2種、型版2種、正当な異なるlayout ID・版を構築し、sourceの異なる実値を既accessorで確認。同じ型の診断2回が独立固定値 CanonicalField[<redacted>]／CanonicalRequest[<redacted>] となることを確認する。所有requestは終了時close、業務fieldのcopy/wipeは元全6ケースで確認する。

OperationFingerprintTestの同じ独立診断2リテラルを横断反映。HMAC・QA056のFingerprintKeyRing依存がある元wholeは今回の実行対象外で別保留。元fixtureを切り出したり代替しない。通常JDK25の実行command、source、hash、型・例外、XML、coverageを公開結果書で照合する。再送・実ログ・Maven六module・実環境は別条件。
