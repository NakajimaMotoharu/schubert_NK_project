# SSC-027 段階Scenario serviceのPG/PT

正式再試験完了: 正式PT-SCN-20260908-23、source e6b4368407043850f0d11a8227d5577977f4868c、2026-09-08 11:46:25～11:49:26 JST、全487件（Protocol80/Storage26/API282/Web58/CHR41）。failed/error/skipped0、5対象module全line/method/class/branch100%、NullAway/Enforcer/format PASS、SpotBugs0。 T01～T07正式成功。実PG/JMS再送、DB-free file区間、fresh final認証/owner拒否、100同時、実writer/inspector201/10000件全byte/hash、再生成/24h保持/ready保全を確認。full startup/単一instance/本番登録/readiness/HTTP/実NK CHRは未完了。

関連: SSC-023/024/027、PG-D-069、BUG-038/YKT-034、PT-SCN-009-T01～T07。正式source/run/環境/command/exit/全module counters/証跡hashはmanifest・002へ固定する。探索成功を正式PASSに加算しない。

対象はScenarioApplicationServiceのprocess/run/inspect/prepare/complete/identity/sameSaved/transaction/owner/requireとprivate型、既存auth/query/Inbox/replay/file/JMSの接続。T01は6要求と空/missing、T02はSpeaker501/明細0/200/201/10000/10001/file quota、T03は元結果再生成、T04は100同Message/現在認証、T05は全NULL/JDBC/clock/UUID/key/identity/late replay/PROCESSING/metadata境界。実SQL後条件、手組UI232/234 bytes、test側LP/JCE/AESによる保存snapshot復号が期待値である。

接続の証拠を区別する:

- T02～T05のpublisher/inspectorは制御順序を検証するtest代替部品。各file callbackで当該serviceのconnection数0、別PG connectionからUser/session/InboxをFOR UPDATE NOWAITで取得できる。物理fileを生成したとは主張しない。
- T06は本番broker templateを隔離Artemisのvm transportへ適用し、実PG確定後のsend/commit失敗→配送回数2、別broker message同業務ID→配送回数1でもInbox1/初回1/生成counter1を確認。手組request・response全bytes/property/持続送信とqueue空を検査。fixture brokerの認証無効は本番設定・security PTの代替でない。
- T07はtest-only storage package bridgeから内部実writer/inspectorを取得。本番可視性を広げず、ext4の保持inode/共有users groupで201/10000件（最大48MB）を実際に書き、各4800byte/全SHA/0640/0750/group/EOFを独立比較。自分の合成readyだけ削除して再生成し、期限/初回完了を保持。次要求のDB commit故障後も新readyの全byteが残ることを実体で確認。別実UID、Linux server IT、full root/exclusive起動gate/本番登録/HTTP/実NK CHRは未完了。

処理中のreadyを勝手に削除する新APIはない。JMSとfile I/OをDB transactionへ持ち込まず、各commit/close成功後だけ次段階へ進む。失敗のcause/suppressed/provider textは外へ出さない。Coverage除外追加なし。満たしていない全体gateをこの接続試験で完了扱いしない。
