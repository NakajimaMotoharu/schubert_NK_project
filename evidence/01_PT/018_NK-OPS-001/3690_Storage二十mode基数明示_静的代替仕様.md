# Storage二十mode literal・基数明示の静的代替仕様

BUG2452/YKT2191/411451/SS311318341、原2/5/9pp cap10・F03 REWORK。current Storage29 raw122のAvoidUsingOctalValues20だけをXML位置で固定。installed PMD7.28の実rule説明を照合した結果、POSIX表記を理由に一括非該当とせず、数値は同値の明示hexとし元POSIX octal注記を残す。元正/異常mode値を独立Linux UAPIのmacro（公開SDKヘッダー）とビット組合せへ対応する。

Source/meta-only。既存全対象source・診断・header/package version/hashを保存し、hex↔octal整数と全他token/fixture/期待値の逆変換を独立確認。own JDK parse/GJF/PMD/Checkstyleだけ。元Test compiler/runtime/FFM/native/process/Root/access/credential動作/fixture置換0、PT PASS/実測coverageへ加算0。kernelヘッダーのABI値確認を実guest/kernelの適合実測へ読み替えない。元実platform PT-HOLD・QA051 final保留・正式1964PT/53scope/工数nullを維持。

二十siteの消滅と他診断のsource位置結合を一対一で確認し、残102は個別分類前の未分類として保持する。全29engine/元成功PT/六Main静的の不要再演を行わない。
