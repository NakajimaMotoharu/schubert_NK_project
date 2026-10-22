# SystemdBinder ABI 後続独立fixture仕様（未着手）

準備追記：6738のsource-only比較工具と管理三canaryを準備し、当public Source/上表21shapeの一致、actual alias型/lookup routing変更・oracle欠落/変更の拒否を確認した。これは現全体待機中の準備で、Production PG/PTの新規受入・新Java test実行ではない。正式review manifest exportとfixture着手は群予算を固定した後に行い、準備費の専有配賦は不明null、後から開始見積を捏造しない。

NK-OPS-001、WBS-P018-03、bootstrap LinuxSystemdSession.Native.bind/invoke。485でbatch側wrapperも同主担当だが費用を二重計上しない。現1475全体/原回収/品質/traceを先行、今はsrc/Testを変えず新jobも起動しない。PGは既実装のABI/責務/例外契約を下記独立根拠と照合し、変更不要なら理由を残す。誤りが見つかれば915先行起票後に必要PG/SS分類を適用する。

## 適用性

旧d48原4184でNative classはL/B/C miss0だがlambda$bind$0(HashMap,String,Object[])Objectがmethod未実行。これは空observerではなくclosed-symbol dispatcherなのでPG-D500共有化の対象外。既LinuxSystemdSessionTestはmissing SymbolLookup/unknown symbol・invoke正常/void/checked/Runtime/Error等を独立に検証する一方、bindが返すdispatcherの正常呼出しを原counterでは確認できない。新source実counterを再照合してから着手する。

PT_DEFAULT候補: JDK25の自己所有upcall stub・confined Arena・fake SymbolLookupだけで、Production bindが作るdowncall dispatcherへ固定入力を渡す。systemd/libcの実libraryLookup/defaultLookup、Native.calls/start/owner/Unit/bus接続、VM/既process/DB/credential/鍵/原本/Backup/permit/intent/failed cohortへアクセスしない。libc freeを含む全symbolは自分のJava callbackだけへ束縛し実libc freeを呼ばない。既native資格や実manager接続の代わりではない。

## 独立ABI oracle（2026-10-22確認）

採用symbolのC型は[systemd v258.8公開header](https://raw.githubusercontent.com/systemd/systemd/v258.8/src/systemd/sd-bus.h)の宣言から手で別表へ固定する。これはhost library versionの認定/変更ではない。freeは既host公開header `/usr/include/stdlib.h` のvoid・単一pointer宣言（line691）を確認した。OpenGroupの公開man URLは403で取得不能、再送/権限変更せずこの事実を保持する。実装のFunctionDescriptorやその戻り値からexpectedを作らない。

型表記P=pointer、I=C int32、L=uint64の64bit表現、B=charの8bit表現、V=void。各FunctionDescriptorは独立した以下の入力表からfixture側で作り、primitiveの両端marker/NULLと自分のArenaのpointerを使って順序・type・bit値を戻り後に照合する。voidのadapter結果は既凍結Test `nativeInvocationPreservesUnknownRuntimeFatalAndSanitizesCheckedFailures` の独立literal MemorySegment.NULLを期待値とする。

|symbol|return:arguments|
|---|---|
|sd_bus_new|I:P|
|sd_bus_set_address|I:PP|
|sd_bus_set_bus_client|I:PI|
|sd_bus_set_allow_interactive_authorization|I:PI|
|sd_bus_set_method_call_timeout|I:PL|
|sd_bus_start|I:P|
|sd_bus_is_ready|I:P|
|sd_bus_process|I:PP|
|sd_bus_wait|I:PL|
|sd_bus_message_new_method_call|I:PPPPPP|
|sd_bus_message_set_auto_start|I:PI|
|sd_bus_message_append_basic|I:PBP|
|sd_bus_call|I:PPLPP|
|sd_bus_message_read_basic|I:PBP|
|sd_bus_close_unref|P:P|
|sd_bus_message_unref|P:P|
|sd_bus_get_property_string|I:PPPPPPP|
|sd_bus_get_property_trivial|I:PPPPPPBP|
|sd_bus_get_property|I:PPPPPPPP|
|sd_bus_message_read_array|I:PBPP|
|free|V:P|

## fixture安全条件と予定Test ID

[JDK25 Linker仕様](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/foreign/Linker.html#upcallStub(java.lang.invoke.MethodHandle,java.lang.foreign.FunctionDescriptor,java.lang.foreign.Arena,java.lang.foreign.Linker.Option...))に従い、upcall targetから例外を外へ伝搬させない。callback内は引数記録と固定戻り値だけ、assertはdowncallが戻った後に行う。予期しないThrowableはfixtureの失敗flagへ保存し、必ず戻り後に失敗と判定してPASSへ正常化しない。own Arenaを最後まで保持・必ずclose、callback/Callsをscope外へ出さず、pointerをdereference/公開logへ出さない。既native-access設定を変更せず、restricted APIの意図的使用は既規約と同じ狭いTest fixture範囲だけで明示する。

- `PT-OPS-MANAGER-ABI-001`: 全21symbolの正常dispatcherを二boundary vectorで呼ぶ。期待=各stub2回/他stub誤呼出0、全引数順/primitive bit/pointer対応、symbol固有fixed return、systemd lookup20/libc lookup1。expectedは上表と公開literalだけ。実systemd関数/権限/manager sessionを実行しない。
- `PT-OPS-MANAGER-ABI-002`: 一symbolずつ欠落するlookupと返却済dispatcherの未知symbol。期待=固定IOException/causeなし、stub呼出0（既正常呼出とは別fresh fixture）、own Arena解放。既null/checked/fatal/closureドメインも当sourceで回帰する。

当候補は新Java2Testの予定で実行済み0、内包するsubvectorを独立JUnit件数へ水増ししない。着手前群予算は後で固定し、source/command/全fixture・原四counter/反証点検を記録する。Source変更や安全条件不明/拒否があればその範囲を保留、拒否を探る試し実行は行わない。nativeQualified=false/正式/個別17-190/工数null/QA051final/代替0は維持する。
