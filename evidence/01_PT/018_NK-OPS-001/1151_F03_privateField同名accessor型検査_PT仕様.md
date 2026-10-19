# private field同名accessor・serialization制約の型検査

Program OPS-F03／SS311343354・411/451、Source2fc。原PMD field/accessor64行はa19診断の実座標である。新全3904進行中のMain/Testを変更せず、64宣言spanが当sourceでも不変であることを先に検証する。既SourcePrivateFieldRenameのSerializable/record拒否guardを変更しない。

OPS-F03-ACCESS001：JDK25の公開compiler APIを使い、source全849の型・private field symbol・同名zero-arg getterのreturn symbolを一意照合する。enum/Throwable/Serializable/非Serializable、default serialization対象field、public getterかを**事実として出力**。何でも自動N/Aへせず、source/code変更・class初期化・private state/method呼出・coverage加算0。非単純getter/未一致座標/未知fieldは拒否する。

OPS-F03-ACCESS002：当selected71/all1664のclass rootとBOM85fb内の固定third-party Jarだけで型解決する。旧project Jarはclasspathへ入れず、Main sourceをprivate mirrorへ完全copyしてhash前後一致を確認する。probe自身javac -Xlint:all -Werror0／processor無し、実NoVM。old field座標から新座標を推定せず、変わっていれば調査へ戻す。

OPS-F03-ACCESS003：新probeのpure二はenum/Throwable/通常classの区別とdefault serialized field、間違ったgetter literal/座標/fieldを否定し、源を変更0と確認する。actual commandは所定PYTHONPATH付き`python3 -B tools/quality/pg5584_field_accessor_inspection.py`。結果は1152へ、currentDiagnosticBindingPending=true/F03falseを必須とし、型検査だけで64指摘を合格にしない。

既quality/業務互換条件は維持、private rename制約を回避する新modeやserialization変更を導入0。群1290 .25/.75/2ppは将来の型検査・証拠整備/再bindingだけ、既読取を遡及配賦0。正式/工数/残予測を件数から改変せず、通常小区切りでは自走を止めない。
