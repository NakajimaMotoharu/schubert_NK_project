# 2869 API/Web NonSecretConfig原whole14 単体テスト仕様

NK-OPS-001/WBS-P018-01（481実leaf「設定・credential loader・redaction境界」）、Production6b53/normal14216/dev-foundation固定。RD SYS-002/004・MQ-001・DAT-001・AUT-002・MED-001、UI212/231/253/223/226/237、SS311/321/342/343§4–5・SSC150、PG272/273。event3268で元2/6/10pp cap10固定。二Main399行とAPI216/Web263行の原whole/全initializersを全読、fixture公開template三件も全読。

原Test ID opsApiCfg001～007/opsWebCfg001～007（実method名/宣言順は原sourceと元XMLへ一意join）。固定API23/Web20キーの独立GOLDEN textと独立MessageDigest SHA-256、redacted toString、common/service/default優先、scalar String/Integer、strict key/重複/未知/secret名/構造/YAML複数doc/alias/interpolation/BOM/CR/16KiB超・decoded改行/nullを検証。API inventory1/7/59627可・0/leadingzero/59628等不可、DB/MQ loopback URL/port境界・固定consumer/pool/retention/protocol/tz、asset/transfer絶対非重複path（構文だけ）を確認。Webhttp/management1～65535別port、timeout100～2000ms/1s/1500ms、wait1～20初期<=max、media stream1～20/Range上限/session上限2固定の独立literalを確認。有限8worker/32jobs、親180秒。期待値は元GOLDEN/固定literal/独立hashでProduction default mapから生成しない。

原006だけは公開src/deployment/config/{common,api,web}.yml.templateを読取る。nk.pt.repository propertyを固定normal snapshotへ一回設定し、run前後にSOURCE git show/normal.begin.inputHashes/current/snapshotの全三実byte/hash・regular非symlinkを一致させる。全inputは原manifest.begin.sourceHashesへ含まれる。actual config/credential tree/env/DB/MQ/HTTP/VM/Root/Graph/鍵/配備0、URL/pathは文字列構文のみ、実rootやportへアクセスしない。negative入力中のprivate/passwordは固定canary文字列で実credentialではない。

Main二件のcanonical owner/costは正本P01801/BASELINE_LOGICAL_REFERENCE（旧PTや旧byte成功は転用0）。原Test二件は正本未登録UNKNOWNであり、変更群の担当から推定して書換えない。本仕様のMain/Test/要件対応とcanonical未確定を区別し最終G13/trace完了を宣言0。二suite/二Sourceはcurrent1697と重複なし。

command: `env PYTHONPATH=tools/quality python3 -B tools/quality/pg11123_checked_python_entry.py tools/quality/pg15222_nonsecret_config_fourteen_pt.py`。Java25.0.4/freshjavac -proc:none -Xlint:all -Werror/六normalJar/empty public exporter config。post15224で同一exec/CRC/全二bootstrap Source closure/四counterを測定し、独立15226で全原14宣言XML/三template/SS343/独立GOLDEN/実ownerを照合する。元OS/JDK/時刻/command/exit/source/hash/input/XML/exec/coverage/BUGを2870/public manifestへ保存。未実測は未確認、manual除外0/公式filter不変/execunion0、Failed-flaky-skipped-not-run合格0。未達があれば実測のまま受入留保、障害は修正前915/916。

正式1964-53/歴史17-190/工数null/QA051final/451-F03-G07/全安全HOLD維持。parse/公開template整合をactual resource admissionやcredential loader資格へ拡張しない。
