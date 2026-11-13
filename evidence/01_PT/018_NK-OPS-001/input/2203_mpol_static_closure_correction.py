from pathlib import Path
import ast,datetime,hashlib,json,subprocess,sys
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';I=B/'input';ld=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(R)),sha256=sha(p));wr=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
f=R/'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/platform/InspectorUnitProbeFixture.java';before=f.read_text();a='''      return next(
          "state",
          states.get(Math.min(stateAt++, states.size() - 1)).getBytes(StandardCharsets.US_ASCII));''';b='''      int currentState = stateAt;
      stateAt++;
      return next(
          "state",
          states.get(Math.min(currentState, states.size() - 1)).getBytes(StandardCharsets.US_ASCII));''';assert before.count(a)==1;f.write_text(before.replace(a,b));tc=R.parent/'toolchain';q=subprocess.run([str(tc/'jdk-25.0.4/bin/java'),'-jar',str(tc/'google-java-format-1.36.1-all-deps.jar'),'--skip-reflowing-long-strings','--replace',str(f)],capture_output=True,text=True);assert q.returncode==0;assert f.read_text().replace(b,a)==before
old=B/'evidence/PG28804-mpol-whole8-current-source-oracle-closure-v1/manifest.json';v=ld(old);v.update(atJST=datetime.datetime.now().astimezone().isoformat(),previousSourceClosure=ref(old),fixtureOperandExpansionInverseExact=True,oldWholeFixtureAllBodyInverseExact=True,verifier=ref(Path(__file__).resolve()));v['testInputHashes'][str(f.relative_to(R))]=sha(f);o=B/'evidence/PG28828-mpol8-static-source-correction-v1';assert not o.exists();o.mkdir();wr(o/'manifest.json',v)
c=ld(I/'2201_mpol8_closed_profile.json');pin=ref(o/'manifest.json');c['closureProofs'][0]=pin;c['reviewedUnstartedProcess']['sourceWitness']=pin;c['slots']={phase:str((B/'evidence'/f'PG{num}-mpol8-qualified-{phase}-v1').relative_to(R)) for phase,num in [('prestyle',28830),('prepare',28832),('static',28834),('preflight',28836),('unit',28840),('post',28842)]};c.update(id='PG28840-MPOL-ORIGINAL7-NEW1-NORMAL');c['privateDirs']=dict(prepare='pg28832-mpol8-qualified-prepare-v1',unit='pg28840-mpol8-qualified-unit-v1');wr(I/'2204_mpol8_qualified_profile.json',c)
p=R/'tools/quality/pgpt_closed_host_post.py';s=p.read_text();anchor="        type_runtime = cmd[cmd.index('--class-path') + 1].split(':')\n";assert s.count(anchor)==1
insert="""        analyzer = work / 'spotbugs-no-outer.pom.xml'
        require(type_symbols.get('analyzerPom') == dict(path=str(analyzer), sha256=sha(analyzer)), 'exact no-Outer analyzer POM hash')
        compiler_root = ET.parse(work / 'pom.xml').getroot()
        ns = compiler_root.tag.split('}')[0] + '}' if '}' in compiler_root.tag else ''
        deps_node = compiler_root.find(ns + 'dependencies')
        require(deps_node is not None, 'compiler dependencies')
        compiler_only = [d for d in deps_node if d.findtext(ns + 'artifactId') == 'real-outcome-compile-symbols']
        require(len(compiler_only) == 1 and compiler_only[0].findtext(ns + 'systemPath') == str(type_carrier), 'only exact compiler type carrier removed for analysis')
        deps_node.remove(compiler_only[0])
        require(ET.tostring(compiler_root) == ET.tostring(ET.parse(analyzer).getroot()), 'independent whole analyzer POM equality, no rule/exclusion change')
""";s=s.replace(anchor,insert+anchor);ast.parse(s);p.write_text(s)
sys.path.insert(0,str(R/'tools/quality'));import pgpt_closed_host_profile as h;import pgpt_closed_host_stages as stage
h.checked_inputs(c)
row=dict(path='sample.java',rule='Example',line='1',message='explicit message');anchor=dict(path='sample.java',rule='Example',sourceLine=1,sourceAnchor='same source',occurrences=1,rawMultiplicity=2,message='explicit message',reason='Exact known duplicate retains both raw messages without suppression.',disposition='NOT_APPLICABLE');raw=[dict(row,path=str(R/'sample.java')) for _ in range(2)];assert len(stage.classify_source_findings(['sample.java'],[anchor],raw,lambda p:'same source'))==2
for values in [raw[:1],raw+[raw[0]], [dict(raw[0],message='unknown')]*2]:
 try:stage.classify_source_findings(['sample.java'],[anchor],values,lambda p:'same source')
 except ValueError:pass
 else:raise AssertionError('multiplicity/unknown message guard')
wr(o/'tool-negative-metadata.json',dict(actualExit=0,exactDuplicatePreserved=2,negativeMissingExtraUnknown=3,rootScopeExpanded=False,productTestsExecuted=0));print('static containment and multiplicity correction: source+metadata0; ProductPT0')
