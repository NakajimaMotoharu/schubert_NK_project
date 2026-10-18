# 所有保護全回帰・原外四bytecode PT仕様

BUG1448/初回依存失敗追補: 実commandは `PYTHONPATH=/home/mini/codex/project1/work/toolchain/pyflakes-3.4.0/runtime python3 -B tools/quality/pg5414_ownership_whole.py`。初回は依存importより先にlocal source.tarのみ作成して停止1、remote転送/Maven0。是正後は依存/standalone staticを新出力より先に確認、同専用outにsource.tarだけ・byte hashが改めて生成した同source git archiveと完全一致する場合のみ、未作成helper/begin/未発行remoteを続行する。begin/helper等が既存なら再開を拒否し元job照合へ戻る。旧archive/失敗を消去・上書きせず、回帰の二回発行にしない。

source29612b2a484a5ab7418e02a491c4360af7444626固定、原baselinee8ecff1bec1d7ddd51cdfbf803acda07c2f6cdb9/PG5130全3814を保持。PG5404-v3の1164/137・六target四100・三static0とPG5406/5410を前提に、**必要な新sourceの全六3896PT/562suite/1664Mainを一度**実行する。旧3791/3814成功の確認再演ではない。git diffから原@Test名削除0・新82、旧RepeatedTest十回は既存で新加算0、suite純増六を独立source inventoryで照合する。実数・元終了code/XMLが期待を満たさなければ全合格にしない。

対象全六module protocol/storage/bootstrap/api/web/batch、全新既Java/JS/SQL/config testcase、関連全RD/UI/SS/SSC308/BUG1414/YKT1178。command `python3 -B tools/quality/pg5414_ownership_whole.py`。既承認LANサーバ上の新専用source/run/tools/archive名だけ使用、host鍵固定/actual転送hash/source不変・全六format-before-any-PT/全Maven・NullAway/ErrorProne/全六SpotBugs/全XML FES・flaky・notrun0/全Main jar-target hash/JaCoCo四counterを保存。NoTests、interrupt、unknown exitや欠測は不合格/UNKNOWN、同一job再発行0。親や業務Unit起動ではなく隔離PG/PT host jobで、原本/VM DB・Backup/配備/鍵操作0、隔離fixtureDB使用。既工具version/envは421・各run/private/manifestへ。

独立資格は元のexit/開始・入力・XML/coverage/static/Jar/Main/hashを回収し、原3814の各case名を保持＋新82だけ、全1664を同sourceで実測する。selectedの三module全767は現実hashで照合、unbuilt897の旧値は期待値のみで、新全体の実測と一致するまで成功を転用しない。旧native/counterの新source合算0。sourceの各入力不変を最後にも確認する。

原237外の追加factory四は既限定。別readonly候補四の**各全取得箇所**を全six current bytecodeで個別確認する:

- ApiApplicationPreparation: codecs/transfer/assets/outboxのcompiler TWRはfactory返却→astore→次body操作を覆う例外範囲・既逆順closeを検証。
- InspectorApplication: native credential rootと内部root/password/connectionsの各TWR、factory途中失敗でも以前取得分のcloseを確認。
- BootstrapAdminMain: root/username/password/dbPassword/source/pool/connectionのTWRと既secret消去、read-only inspectionで新ADMINを実行しない。
- WebNativeRuntime: runtime本体/全状態はstart前、broker/codecs/transfer/assets等の返却直後field store、WebProcessMainの事前全port→WebRuntimeExecution保護で部分ownerのclose/UNKNOWN保持。元WebRuntimeStop期限と順序を維持する。検索だけで非該当認定しない。

四sourceファイルはe8ecから不変であることをsource diffで確認済みだが、それだけでbytecode受入としない。個々のprotect PC/handler/field store/外側scopeを証跡へ記録する。TWRの元addSuppressed契約はcommon ResourceScopeの異なる優先へ勝手に置換しない。実取得の追加gapがあればBUG/YKTを修正前登録し、必要な設計補足を先行する。

全体のJaCoCo missは隠さず公開し、native-only分は当sourceの正式CRC/session資格・同source/run条件で閉じるまで四100や451完了にしない。F03適用性/CHR・DIF/trace/QA051final/BUG1414全体/引継ぎ・正式1964/53は別未完。source/run/OS/JDK/tool/command/expected実数/actual/hashをmanifestへ、raw property/session/credential公開0。
