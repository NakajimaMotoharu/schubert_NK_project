"""Explicit witnessed opt-in only; legacy compiler policy, unit command and counter sums stay exact."""
from pathlib import Path
import ast,json
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';start=json.loads((B/'input/2198_mpol_feature_whole8_normal_start.json').read_text());state=json.loads((R.parent/'PMO/pgpt-completion-stage-20261102/checkpoint.json').read_text());assert state['ordinaryActiveGroup']==start['groupId'] and state['ordinaryGroupNotYetClosed'];p=R/'tools/quality/pgpt_closed_host_profile.py';s=p.read_text();assert 'import pgpt_unstarted_process' not in s
s=s.replace('    validate_optional_capabilities(c)\n','    import pgpt_unstarted_process\n    pgpt_unstarted_process.syntax(c)\n    validate_optional_capabilities(c)\n',1)
s=s.replace("        require(name + '.class' in c['physicalClasses'] or signature_fence or analysis_fence,", "        import pgpt_unstarted_process as process\n        process_fence = c.get('reviewedUnstartedProcess') is not None and name in process.FORBIDDEN_INIT\n        require(name + '.class' in c['physicalClasses'] or signature_fence or analysis_fence or process_fence,",1)
s=s.replace("    return c['mainSources'] + [t['path'] for t in c['testSources']]", "    import pgpt_unstarted_process as process\n    return c['mainSources'] + [t['path'] for t in c['testSources']]",1);s=s.replace("+ (analysis.SOURCE_PATHS if c.get('reviewedAnalysisOnlyContext') is not None else [])", "+ (analysis.SOURCE_PATHS if c.get('reviewedAnalysisOnlyContext') is not None else []) + ([process.SOURCE, process.TESTDIR + 'InspectorUnitSnapshotTest.java'] if c.get('reviewedUnstartedProcess') is not None else [])",1)
s=s.replace("'pgpt_analysis_symbols', 'pgpt_artemis_sdk']", "'pgpt_analysis_symbols', 'pgpt_artemis_sdk', 'pgpt_unstarted_process']",1)
s=s.replace("    for path in c['mainSources'] + [t['path'] for t in c['testSources']]:\n        text =", "    import pgpt_unstarted_process as process\n    process.checked(c)\n    for path in c['mainSources'] + [t['path'] for t in c['testSources']]:\n        text =",1);s=s.replace("'@ParameterizedTest', 'ProcessBuilder', 'DriverManager'", "'@ParameterizedTest', 'DriverManager'",1)
anchor="        require(not any(x in text for x in [*DENIED";i=s.index(anchor);end=s.index('\n',i);s=s[:end]+"\n        require('ProcessBuilder' not in text or process.allow_builder(c, path, text), 'outside closed ordinary host ProcessBuilder scope')"+s[end:]
s=s.replace("    signature = guard.create_compile_carrier(c, work)\n", "    signature = guard.create_compile_carrier(c, work)\n    import pgpt_unstarted_process as process\n    type_signature = process.create_compile_carrier(c, work)\n",1)
anchor="    add(add(root, 'build'), 'plugins').append(copy.deepcopy(compiler))";s=s.replace(anchor,"    if type_signature is not None:\n        d = add(ds, 'dependency')\n        for n, v in [('groupId', 'dev.codex.schubert.quality'), ('artifactId', 'real-outcome-compile-symbols'), ('version', '1'), ('scope', 'system'), ('systemPath', type_signature['compileCarrier']['path'])]: add(d, n, v)\n"+anchor,1)
s=s.replace("    guard.copy_runtime_interface(signature, work)\n", "    guard.copy_runtime_interface(signature, work)\n    process.copy_runtime_enum(type_signature, work)\n",1)
s=s.replace("    compile_only = [signature['compileCarrier']['path']] if signature is not None else []\n", "    compile_only = [signature['compileCarrier']['path']] if signature is not None else []\n    if type_signature is not None: compile_only.append(type_signature['compileCarrier']['path'])\n",1)
s=s.replace("    m.update(analysisOnlyContext=analysis_context, guardSignature=signature,", "    m.update(unstartedProcess=type_signature, analysisOnlyContext=analysis_context, guardSignature=signature,",1);ast.parse(s);p.write_text(s)
p=R/'tools/quality/pgpt_closed_host_stages.py';s=p.read_text();assert 'pgpt_unstarted_process' not in s;s=s.replace('    return p, m, work\n', '    import pgpt_unstarted_process\n    pgpt_unstarted_process.validate_prepared(c, m, work)\n    return p, m, work\n',1);s=s.replace("    compile_only = [m['guardSignature']['compileCarrier']['path']] if m.get('guardSignature') is not None else []\n", "    compile_only = [m['guardSignature']['compileCarrier']['path']] if m.get('guardSignature') is not None else []\n    if m.get('unstartedProcess') is not None: compile_only.append(m['unstartedProcess']['compileCarrier']['path'])\n",1);s=s.replace("    begin['guardSignature'] = m.get('guardSignature')\n", "    begin['guardSignature'] = m.get('guardSignature')\n    begin['unstartedProcess'] = m.get('unstartedProcess')\n",1);ast.parse(s);p.write_text(s)
p=R/'tools/quality/pgpt_closed_host_post.py';s=p.read_text();assert 'type_symbols = ' not in s;anchor="    analysis_context = prep.get('analysisOnlyContext')";insert="""    type_symbols = b.get('unstartedProcess')
    if c.get('reviewedUnstartedProcess') is not None:
        import zipfile
        type_base = 'dev/codex/schubert/nk/batch/platform/MorningBackupUnitCycle'
        type_enum = type_base + '$Outcome'
        type_hashes = {
            type_base: 'dbf0c01bee5c1955ce41b11858d6d855c0ab8d7bf503814951fd8a11ee9216d9',
            type_enum: '86ccc00797c876ed4688bf412cc38c1dbdeba5c9813c495f8fe2ea2fd87dd50a',
        }
        require(type_symbols == prep.get('unstartedProcess') and isinstance(type_symbols, dict), 'same witnessed static type receipt')
        type_carrier = work / 'outcome-compile-symbols.jar'
        require(type_symbols['compileCarrier'] == dict(path=str(type_carrier), sha256=sha(type_carrier)) and type_symbols['runtimeInitializationPermitted'] is False, 'immutable own compile-only type carrier')
        with zipfile.ZipFile(type_carrier) as archive:
            require(len(archive.namelist()) == 2 and set(archive.namelist()) == {n + '.class' for n in type_hashes}, 'exact two real normal type bytes')
            require(all(hashlib.sha256(archive.read(n + '.class')).hexdigest() == v for n, v in type_hashes.items()), 'real normal class hash equality')
        require(physical[type_enum + '.class'] == type_hashes[type_enum] and type_base + '.class' not in physical, 'real enum only, parent absent from runtime/report')
        require(ids[type_enum] == '9bca5185cf2ba25e', 'real enum static CRC, no prior execution claim')
        type_runtime = cmd[cmd.index('--class-path') + 1].split(':')
        require(type_runtime == [str(work / 'target/classes'), str(work / 'test-classes'), *b['dependencies']] and str(type_carrier) not in type_runtime, 'static carrier never runtime path')
        type_forbidden = {type_base, type_enum, 'dev/codex/schubert/nk/batch/platform/InspectorUnitSnapshot', 'dev/codex/schubert/nk/batch/platform/SystemctlStateSource$NativeProcess'}
        require(type_forbidden <= set(c.get('forbiddenInitializedClasses', [])), 'no actual process/Root/snapshot or enum execution permission')
    else:
        require(type_symbols is None, 'no implicit unstarted process/type capability')
""";assert s.count(anchor)==1;s=s.replace(anchor,insert+anchor)
anchor="    targets = {n: counters(classes[n]) for n in c['targetClasses']}";insert="""    if type_symbols is not None:
        never_executed = {type_enum, 'dev/codex/schubert/nk/batch/platform/InspectorUnitSnapshot', 'dev/codex/schubert/nk/batch/platform/SystemctlStateSource$NativeProcess'}
        for name in never_executed:
            require(name not in probes and name not in init and all(row['covered'] == 0 for row in counters(classes[name]).values()), 'all unexecuted real type/factory counters remain missed')
        reader = classes['dev/codex/schubert/nk/batch/platform/InspectorUnitProbe$NativeReader']
        streaming = [x for x in reader.findall('method') if x.get('name') in ['executeStreaming', 'queryFailure'] or x.get('name', '').startswith('lambda$executeStreaming$')]
        require(len(streaming) >= 2 and all(all(row['covered'] == 0 for row in counters(x).values()) for x in streaming), 'unqualified streaming lifetime path never executed or credited')
""";assert s.count(anchor)==1;s=s.replace(anchor,insert+anchor);s=s.replace("    result['guardSignature'] = signature", "    result['unstartedProcess'] = type_symbols\n    result['unstartedProcessInitializationObserved'] = []\n    result['unqualifiedStreamingExecutionObserved'] = False\n    result['guardSignature'] = signature",1);ast.parse(s);p.write_text(s);print('exact feature hooked; Root compiler configuration/unit JVM command/counter sums unchanged')
