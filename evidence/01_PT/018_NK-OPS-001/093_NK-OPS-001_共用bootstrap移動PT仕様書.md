# NK-OPS-001 共用bootstrap移動PT仕様（PG289、未認定）

SSC084/SS311・342・343、RD SYS-002/004・DAT-001、UI212/243/253、471 D01/02/05。Production所有は`schubert-nk-bootstrap`、互換package/Test IDは変更しない。固定inventoryは`tools/quality/bootstrap_ownership.py`。API/Webへの業務依存・秘密増配・Current oracle変更なし。

既存CRED/DBADMIT/DBSOURCE/DBPOOL/API-RES/MAIN Test IDを継承。目的は物理module移動後も固定材料、全接続role検査、close/消去、異常/null/並行/境界を保存すること。入力/期待値/独立根拠は各既存仕様書とliteral固定SQL/Golden値。移動を理由にassertionや期待値を弱めない。移動11main/9suite/2fixtureを019負canaryで独立走査、旧API重複なし・未知owner拒否・manifest構築順を確認する。

実行: Java25.0.4、Maven wrapper/offline固定m2。Production6 module `clean test org.jacoco:jacoco-maven-plugin:0.8.15:report com.github.spotbugs:spotbugs-maven-plugin:4.10.4.0:check`。POM/security所有境界の横断影響回帰であり、新機能受入/正式53scope収集ではない。API native mainは必須gate未結線、成功経路未網羅を除外/到達不能認定しない。

BUG264/YKT198: 016 metadata追加順を修正前起票、105canaryで限定再試験。実行結果094/provisional PG289 manifestで対応。OS root/systemd実配布、DB SCRAM実Production起動、JMS必須gate、外部正常停止、実NK CHR-A01/L01は未実行。正式coverage/全scope gate後にだけ再認定する。
