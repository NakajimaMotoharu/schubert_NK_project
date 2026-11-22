# 保守観測record四型の値契約

F03、NK-OPS-001、OPS-003/008、UI251 §3、SS341 §4.1/4.2、BUG-3648／YKT-2866。JDK25.0.4、dev-foundation、試験source `276339f7fac4f630793cd755d9a23d16991eaddb`、製品source `dbdd79f2fa415e91ff29bf9bafecd4984d11eb40`。

- PT-OPS-MAINT-VALUE001。合成run/boot/時刻と停止結果の同値別個体は等しく同一hash。Markerの3成分、StopReceiptの4成分を一つずつ変えると別の値。
- PT-OPS-MAINT-VALUE002。同値別個体で構成したSafetyChecks／UpdateReceiptは等しく同一hash。安全観測5成分と更新receipt4成分を一つずつ変えると別の値。

PG42986、2026-11-23 JST、実27（元同製品25、新2）全成功、F/E/S0。単一元exec、正規JARの13物理は再buildなし。無フィルターL121/124・M69/76・C13/13・B88/88。残る4汎用toString、3private ctorは未達を保持。実保守／Root、DB、QA056、既保留の実行なし。試験source、元コマンド、CRC、入力、Test名、元JUnitと公開hashはmanifestで照合可能。公開SHA-256 `5f1d186f3340c84e338eb04fe42551f22d049a5175bdcf0594843e486683b131`。
