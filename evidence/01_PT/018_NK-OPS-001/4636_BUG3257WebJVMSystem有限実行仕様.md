# BUG-3257 Web JVM・System metric fixtureの有限終了単体仕様

NK-OPS-001、RD171/UI252/SS311/351/354、F03/2-2・P018-09、YKT-2387。元[仕様2837](2837_Web標準SDK五whole73_単体テスト仕様.md)のWEBJVM001〜014・WEBSYS001〜014を同候補で実施する。Mainの変更0。WEBJVM014・WEBSYS014それぞれ4 worker、独立64レジストリ。1入力4/2処理、計256/128、同一borrowed registry、close 0、元Future.get 10秒を維持。各finallyで停止を要求し、10秒以内の全worker終了をassertする。

他の元26件で既定SDKのJVM/CPU/fd値を自己所有child内で独立値と比較し、lazy mode、順序、null、未知、例外同一性、partial終了を保持する。別JVM、サービス、ネットワーク、Hikari、DB、Root、native受入は扱わない。旧whole73の実行結果は歴史証跡。現候補でRoot compile/static、28件、独立XML/CRC、生counterの順に確認し、同一execのみで判断する。
