# BUG-3254 Web標準metric並行fixture単体仕様

NK-OPS-001、RD171、UI252、SS311/351/354、WBS-F03/2-2・P018-09、BUG-3254／YKT-2387。対象は WebStandardMetrics.bind/install と元WEBSTD001〜013。元[仕様2691](2691_APIWeb標準組立原whole26_単体テスト仕様.md)、[試験表2837](2837_Web標準SDK五whole73_単体テスト仕様.md)の期待値を使用。

WEBSTD013は4 workerへ別々の自己所有レジストリ64件を投入。各3 phaseで計192回、レジストリの借用先close 0、Future get各10秒を維持。終了経路のfinallyで全workerに停止を要求し、10秒以内に終了しなければ失敗。全13件で通常、無効mode、null、所有拒否、先行成功、例外同一性、close順、並行を確認する。

SDKは既hashのMicrometerだけ。標準SDKの対象はowned child JVM、実endpoint/DB/Hikari/Root/承認保留型を使わない。Root compiler、静的適用、元13 ID/XML、独立CRC、当型のunfiltered line/method/class/branch/instructionを確認。製品sourceを固定し、関連補助型の未到達は別に残す。
