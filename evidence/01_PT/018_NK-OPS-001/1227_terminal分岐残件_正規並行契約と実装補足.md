# 1227 terminal分岐残件：正規並行契約と実装補足（実行前）

PG-D445/BUG1501継続、SS321§6～7/322§11/352/451、WBS-F03/P005-03。現在source0f572da66のPG5860全3971が実行中であり、本書は追加PG/PTの準備、Production/Test未変更・追加動的試験未実行。元全体真正終端と独立実counterを確認してから当必要部分だけ適用する。既成功確認目的の再実行ではない。

SS321はSync四独立session、Question/WebLog/Web reply各専用一sessionを定める。[Jakarta Messaging 3.1 §6.2/6.2.5](https://jakarta.ee/specifications/messaging/3.1/jakarta-messaging-spec-3.1.html)はJMSContextの内部sessionと同一session listenerの逐次実行を規定する。したがって後続callbackが入口haltを観測する単一sessionと、異なるSync contextで既に処理中の複数callbackを区別する。同一contextへの再入・並行を合成してcoverageのfalse側を作らない。

全体の実counterでもterminal通知CASのfalse側が未達なら、次の同等な製造整理と正規並行の独立試験を行う。単なる到達不能宣言・除外ではなく、不要な競合分岐を単一session実装から除き、必要な競合分岐は実際に検証する。

1. Question/WebLog/Web replyのCommittedFatalと非commit fatal経路は、入口haltとJMS逐次実行により各runtime一度だけ入る。各catchでhalt/terminalを確定し通知する明示的処理へ整理する。元IOException/JMS/Runtime/Error分類、Error rollback/伝播、owner close、ready、onTerminal/onFatalの区別は維持する。constructor/外部API/DB/wire/SSは変更しない。通知中の再入も既haltが先に遮断する。
2. Syncは四contextなので通知CASを維持する。独立context二つが各一workerで既に入場した状態を、commit又はrollback port内の有限barrierで確定する。一つのcontextを複数threadへ渡さず、再帰callbackを呼ばない。両方が処理中であることを確定後にcatchへ帰す。
3. 新TERM005（両者のDLQ隔離commit正常）はmetadata/send/commit各二・protocol通知一/fatal0/business0、TERM006（両者の隔離失敗＋正常rollback）はmetadata/rollback各二・commit/send0/fatal通知一/protocol0/business0。いずれもowner close四・callback内close0、以後全四contextの再callbackで追加処理0。これらは既inflight二件の許容であり、終了後の新入場二件を許す期待ではない。
4. メモリfixtureは各context独立counter、barrier二party/有限timeout、future完了後だけcounterを読む。未知provider method0・失敗時executor終端を確認する。API三/Web一の既TERM001～004・旧API/Web oracle・通常再送・Error・null・startup/close境界も維持する。

予定は新@Test二つ/既class内で、source確定後の選択83/22と必要全3973/592/1666（元3971identity＋新二）を記録する。これは計画値であり実績へ加算しない。全Main/実byte/公開ABI/未除外raw/全XML/八core四counterを新sourceで独立照合し、元sourceのMain/coverage/nativeを輸入しない。scope外の通常成功や実Root/cleanup/VM/Unit/permitのHOLDは解除しない。追加QA/SSCは不要な内部実装補足だが、外部仕様を変更する必要が判明すれば所定台帳を先行する。
