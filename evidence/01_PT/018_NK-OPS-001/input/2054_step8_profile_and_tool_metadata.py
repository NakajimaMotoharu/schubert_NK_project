from pathlib import Path
import copy,datetime,hashlib,json,sys
R=Path.cwd();sys.path.insert(0,str(R/'tools/quality'));import pgpt_closed_host_profile as h;import pgpt_closed_host_post as post
B=R/'evidence/01_PT/018_NK-OPS-001';ld=lambda p:json.loads(p.read_text());ref=lambda p:dict(path=str(p.relative_to(R)),sha256=h.digest(p));wr=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');closure=B/'evidence/PG28230-batch-step8-internal-source-closure-v1/manifest.json';proof=ld(closure);c=ld(B/'input/2045_batch_run2_profile.json');mains=proof['wholeReviewedMainSources'];owners={x['path']:x['owner'] for x in ld(R/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json')['artifacts']};stem='dev/codex/schubert/nk/batch/repository/';names=[Path(p).stem for p in mains]+['BatchRunRepository$History','BatchStepResult$Status','BatchStepResult$Reason','BatchStepResult$1'];spec=B/'4196_Step公開値原八単体仕様.md';assert not spec.exists();spec.write_text('''# Step公開値原八単体仕様

NK-BAT-001/OPS009/DAT009/UI251/SS331§8.3/341/343/352、BAT130～137、SSC055/PG163。原BatchStepValuesTest全8methodを実行する。PG28230全十Mainと全Testのsource閉包参照、原8の独立literal steps/status/reason/summary、境界1..999999999999/1..99、MIN/MAX、4counter負値/SKIPゼロ/SUCCESS失敗0と和制約を捏造しないこと、µs時間境界・IANA歴史LMT1582・JST翌日、null不変条件/固定redaction/record等価性、64独立virtualtask ID/attempt/JSTを旧assertionそのまま検証する。

nullContractsAndRedactionの既存reflectionはprivate static不変History recordの合成入力constructor/tostringだけ。実DB/親repository instance/Root/認可能力を使わない。Whole parent/transitiveをsourceそのままコンパイルし、BatchRunRepository/RunReferenceRepository/RunReferences/JdbcResourceFailures/BatchRepositoryExceptionのruntime初期化を禁止する。許容はこのTestのこのClass.forName一箇所に限定し、proof/Mainhashを拘束、全Test抽出・代替fixture・一般反射許可0。

BUG2746 workerはFuture5秒を保持し、finally shutdownNow-await10秒を追加、逆変換で全元assertion保持。RootNullAway/Main10/全physical14・JDK/JSpecify/JUnitのみ、全staticとsourceanchor適用判定、Git固定後一whole8。全physicalをreportし、Step/Attempt/Result全三source（Status/Reason込み）をtargetとする。History診断coverageは親Repo全source合格としない。親JDBC未網羅・Run/Activationhelper未網羅も保持する。

javac enum switch mapはBatchStepResult$1/Reasonだけ事前明示。全byte/CRC/class-initを保全し、javapでsynthetic・一staticfinal int[] field・clinit一つ・sourceFileを確認、既定JaCoCo0.8.15 classinfo/reportがzeroであることを独立照合。独自filter/除外設定を追加しない。自然branchなしenumはN/Aと実在branch100を分ける。FESabort/skip/flaky未実行は合格へ算入せず、通常PT結果と正式451/190を分離する。command・環境・source/run・hashは六stage/独立manifest、費用F03追加資格と元artifact ownerを分離。
''')
c.update(id='PG28252-BATCH-STEP-VALUES8',mainSources=mains,productOwnerByMainPath={p:owners[p] for p in mains},testSources=[dict(path=proof['wholeTest'],tests=8)],expectedTests=8,oracleSpecs=[ref(spec)],closureProofs=[ref(closure)],physicalClasses=[stem+n+'.class' for n in names],targetClasses=[stem+n for n in ['BatchStep','BatchStepAttempt','BatchStepResult','BatchStepResult$Status','BatchStepResult$Reason']],reviewedReflection=[{k:proof['reflection'][k] for k in ['testPath','targetClass','sourceAnchor','targetSource']}|dict(closureProof=ref(closure))],forbiddenInitializedClasses=proof['forbiddenInitializedClasses'],standardCompilerSwitchMaps=proof['expectedStandardCompilerSwitchMaps'],slots={k:str((B/f'evidence/PG{v}-batch-step-values8-{k}-v1').relative_to(R)) for k,v in dict(prestyle=28242,prepare=28244,static=28246,preflight=28248,unit=28252,post=28254).items()},privateDirs=dict(prepare='pg28244-batch-step-values8-prepare-v1',unit='pg28252-batch-step-values8-unit-v1'))
p=B/'input/2055_batch_step8_profile.json';assert not p.exists();wr(p,c);checks=[]
def reject(label,mut):
 x=copy.deepcopy(c);mut(x)
 try:h.validate_syntax(x);h.checked_inputs(x)
 except (ValueError,KeyError,TypeError):checks.append(dict(label=label,rejected=True));return
 raise AssertionError(label)
h.validate_syntax(c);h.checked_inputs(c);checks.append(dict(label='ExactHistoryAndAll10WholeSourcesClosed',accepted=True))
reject('NoProofBinding',lambda x:x['reviewedReflection'][0].update(closureProof=dict(path='evidence/missing.json',sha256='0'*64)))
reject('RootInsteadOfHistory',lambda x:x['reviewedReflection'][0].update(targetClass='dev.codex.schubert.nk.RootFailedStartRecoveryTest'))
reject('DifferentReflectionAnchor',lambda x:x['reviewedReflection'][0].update(sourceAnchor='Class.forName(userInput);'))
reject('ParentInitializationAllowed',lambda x:x.update(forbiddenInitializedClasses=[]))
reject('OtherParentsNotForbidden',lambda x:x.update(forbiddenInitializedClasses=x['forbiddenInitializedClasses'][:1]))
reject('HistoryPhysicalOmitted',lambda x:x['physicalClasses'].remove(stem+'BatchRunRepository$History.class'))
reject('CompilerMapPhysicalOmitted',lambda x:x['physicalClasses'].remove(stem+'BatchStepResult$1.class'))
reject('UnreviewedReflectionNoCapability',lambda x:x.update(reviewedReflection=[]))
reject('MapCounterClaimAsTarget',lambda x:x['targetClasses'].append(stem+'BatchStepResult$1'))
reject('MapSourceWrongOwner',lambda x:x['standardCompilerSwitchMaps'][0].update(sourcePath=x['mainSources'][0]))
reject('ForeignEnum',lambda x:x['standardCompilerSwitchMaps'][0].update(enumClass='foreign.X'))
reject('CoverageExclusion',lambda x:x.update(coverageExclusions=['*Repository*']))
reject('ArtifactOwnerClone',lambda x:x['productOwnerByMainPath'].update({x['mainSources'][0]:'WBS-P016-21'}))
shape='flags: (0x1020) ACC_SUPER, ACC_SYNTHETIC\n interfaces: 0, fields: 1, methods: 1, attributes: 4\n static final int[] $SwitchMap$dev$codex$schubert$nk$batch$repository$BatchStepResult$Reason;\n flags: (0x1018) ACC_STATIC, ACC_FINAL, ACC_SYNTHETIC\n static {};\n SourceFile: "BatchStepResult.java"\n';item=c['standardCompilerSwitchMaps'][0];post.validate_switch_map_shape(shape,item);checks.append(dict(label='SyntheticMetadataShapeOnlyNotProductBytecode',accepted=True))
for old,new,label in [('ACC_SUPER, ACC_SYNTHETIC','ACC_SUPER','MapNotSynthetic'),('fields: 1','fields: 2','MapExtraField'),('methods: 1','methods: 2','MapExtraMethod'),('$Reason;','$Other;','MapForeignField'),('static {};','void work();','MapNoClinit'),('SourceFile: "BatchStepResult.java"','SourceFile: "Foreign.java"','MapForeignSource')]:
 try:post.validate_switch_map_shape(shape.replace(old,new),item)
 except ValueError:checks.append(dict(label=label,rejected=True));continue
 raise AssertionError(label)
O=B/'evidence/PG28234-step8-tool-capability-metadata-v1';assert not O.exists();O.mkdir();wr(O/'manifest.json',dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),checks=checks,count=len(checks),profile=ref(p),toolHashes=h.tool_hashes(),productClassesRead=0,productCompileOrTests=0,syntheticMetadataNotProductCoverage=True,newAcceptance=0,holdChanged=False,sourceClosure=ref(closure),verifier=ref(Path(__file__).resolve())));print(json.dumps(dict(actualExit=0,checks=len(checks),profile=ref(p),evidence=ref(O/'manifest.json'))))
