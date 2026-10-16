# 999 Root proof相関・ordinary環境固定 独立PT仕様

NK-OPS-001、`RootServiceLauncher.proof/environment`、OPS009/SYS002/004・UI212/251/253・SS342/343/SSC137。PG4662の同class proof4branch/environment9line欠測から対象化。Main/業務/Unit/VMは不変更、Root self仕様997と同起動契約の独立負試験群。

| Test ID / method | 固定入力と操作 | 独立期待値 |
|---|---|---|
| ROOTPROOF005 / RootServiceProofTest.eachIndependentEpochBootAndActivationContradictionNeverEmitsProof | 既手書きNKSTART1 golden/同typed原値に対し、self.boot/current.boot不一致、current/permit boot不一致、epoch不一致、activationだけ不一致の四入力 | 各IOException、proof非発行。正常API/WEB全17fieldは既goldenを継続 |
| ROOTENV001 / eachServiceExportsExactlyFiveLiteralBindingsAndNoInheritedExtras | 別owned test JVM、API/WEB各正規credential location。親から偽INV/別config/未知extraを与える | 明示literal Mapの五fieldだけ：INV=2×32、当service固定credential path、config=/etc/schubert-nk、admissionFD128/proofFD129。Map不変、偽/未知envを継承しない |
| ROOTENV002 / missingWrongServiceRelativeAndExtraSuffixCredentialPathsAreRejected | 各API/WEBでcredential path欠落/別service/相対/正規+.part | 各IOException、Map非返却 |
| ROOTENV003 / absentOrForeignSelfFailsBeforeReadingAnyCredentialLocation | service/null、self/null、自己APIに引数WEB | 明示null契約fail-fast又はIOException、native/DB/Unit操作0 |

各childは公開fixture専用Process所有、normal TERMだけの限定後始末。実server/VM/元成功jobへsignalしない。現在Surefireの唯一固定JaCoCo agentをchildにも適用し、全child終了後だけ親試験を終える。default同run execへのappendで当byteを採取し、childの同Input source/classと親の実XMLへ結合する。agent不在・child時間内未終端・非0・固定marker以外出力は不合格。期待Map/四矛盾はProductionから計算しない。公開fixture値であってrawcredential/session/tokenを用いない。

新runner **pg4678_root_proof_environment_selected.py** は4674の実六project/厳密suite-class-method inventory/NoTests fatalを維持し、RootServiceProofTestとRootServiceEnvironmentTestを加えた関連10suiteを選択。固定snapshot、compiler/null/format、全XML FES0・未実行0、proof/environment各LINE/METHOD/適用BRANCHのmiss0を要求する。class全体/Mainの他native例外分岐をこの二methodの成功へ読み替えない。

実command=`PYTHONPATH=tools/quality:tools/quality/vm/050_s1:<pyflakes-runtime> python3 -B tools/quality/pg4678_root_proof_environment_selected.py`。証跡=PG379/pg4678-root-proof-environment-selected-v1（begin/source全hash/owner/command/exit/XML/log SHA/target counter）。実行日時/source commit/結果は実行後追記、現時点not-run。旧3721/native9/正式1964を新caseで算術加算せず、全体counter/正式source-runは後続所定gateで再照合する。
