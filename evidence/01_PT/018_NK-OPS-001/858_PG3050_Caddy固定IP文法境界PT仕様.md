# 858 Caddy公開設定の固定IP/frame境界

NK-OPS-001、主担当/費用leaf WBS-P018-01、PT-OPS-CADDY3050-001、SS342/343/SSC178・451。開始見積り0.2/0.5/2ppを別群で固定、共有費配賦null。Production a9/PG2802・exact3026 Main不変更、Caddy reload/起動/VM操作0。

独立literal Caddyfileの既3Test methodを全件再試験する。追加入力=global blockとsite headerだけ（後続改行/本文なし）、IPv6開閉bracket片方のみ、colon無しhex `[11]`、IPv4 mapped hex `[::ffff:7f00:1]`。SS342の固定IPv4/IPv6/internalCA/55160のみという契約から全てIOExceptionを期待し、host名/URL/DNS/HTTP downgradeを許可しない。Production encoder/URI結果をexpected生成に使わない。IPv4 mapped表記はJava InetAddressがInet4Addressへ解決するため、見た目のbracketだけでIPv6として受入しない。

既正常IPv4/IPv6・整形・null・独立deployment template照合を同時実行。template基点は既module directoryとしfixtureを改変しない。javac -Xlint:all -Werror/全3JUnit/FES0/JaCoCo対象counter、src Main jar/fixture/依存hash不変・原XML/logを保存する。全体回帰3689（新methodは先の四件のみ）・native/四100/正式451へ未実行結果を加算しない。独立null/未知/境界は本群、TLSネイティブreadは既実経路と後続未網羅へ分ける。

実結果は実行後追記、秘密/CA秘密鍵・session・DB原本はGit非格納。

実結果: edf2f8931固定/exec14416 actual0、全三/FES-aborted-notRun0、server manifest9bc8b6cb915a2a7471bb334abc00aaf121a1d22e3773481c8a60d3e7dcf2cbe5/XML688272057c495c746dbb768698fd209206c4f681e99faac8dd43c6cfdf94ff2d/execb9a90e9b/coverageXMLd1d86d99。host-only class78L/13M/32B missed、四100=false（当nativeとこの限定execの統合はここでは未実行）。原template・依存・Main jar不変、VM操作/native輸入0。PG379/pg3050-caddy-grammar-selected-v1・aru PG3050-candidate-v1へ原証跡保全。
