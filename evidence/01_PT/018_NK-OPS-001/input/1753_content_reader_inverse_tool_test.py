"""Six independent pure-planner checks, no product compile/runtime or file writes."""
from pathlib import Path
import ast,hashlib,json
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';writer=B/'input/1752a_content_reader_fatal_source_static_v2.py';helper=B/'input/1634_web_security_fatal_source_static.py';ns={}
for p,names in [(helper,{'revert_calls','require_owned'}),(writer,{'plan_calls'})]:
 nodes=[x for x in ast.parse(p.read_text()).body if isinstance(x,ast.FunctionDef) and x.name in names];assert len(nodes)==len(names);exec(compile(ast.Module(body=nodes,type_ignores=[]),str(p),'exec'),ns)
plan=ns['plan_calls'];revert=ns['revert_calls'];owned=ns['require_owned'];patterns=['} catch (A failure) {','} catch (B failure) {','} catch (C failure) {'];old='known import\n    } catch (A failure) {\n      oldA();\n    } catch (B failure) {\n      oldB();\n    } catch (C failure) {\n      oldC();\n';results=[];new,calls=plan(old,patterns,False);assert calls==['      SessionStoreException.preserveFatal(failure);\n']*3 and revert(new,calls)==old;results.append('TOOL-CONTENT-INVERSE001_THREE_SAME_INDENT_CALLS_EXACT_LITERAL_ORIGINAL')
reader='import java.nio.channels.FileChannel;\n    } catch (D failure) {\n      fixed();\n';n,cs=plan(reader,['} catch (D failure) {'],True);assert revert(n,cs).replace('import dev.codex.schubert.nk.web.session.SessionStoreException;\n','')==reader;results.append('TOOL-CONTENT-INVERSE002_READER_SINGLE_CALL_IMPORT_EXACT_LITERAL_ORIGINAL')
for id,text,pats in [('003_MISSING_CATCH',old,patterns+['} catch (missing failure) {']),('004_DUPLICATE_CATCH',old+patterns[0]+'\n',patterns)]:
 try:plan(text,pats,False)
 except AssertionError as e:assert str(e)=='CATCH_NOT_UNIQUE';results.append('TOOL-CONTENT-INVERSE'+id)
 else:raise AssertionError('invalid catch inventory accepted')
assert owned(old,old,new) is False and owned(new,old,new) is True
try:owned(new+'foreign\n',old,new)
except AssertionError as e:assert str(e)=='FOREIGN_SOURCE_CHANGE_REFUSED';results.append('TOOL-CONTENT-INVERSE005_FOREIGN_CHANGE_REFUSED')
else:raise AssertionError('foreign source accepted')
try:revert(new+calls[0],calls)
except AssertionError as e:assert str(e)=='CALL_LINE_MULTIPLICITY_MISMATCH';results.append('TOOL-CONTENT-INVERSE006_EXTRA_CALL_REFUSED')
else:raise AssertionError('extra inserted line accepted')
assert len(results)==6;O=B/'evidence/PG27671-content-writer-independent-six-v1';assert not O.exists();O.mkdir();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();v=dict(actualExit=0,toolAssertions=6,results=results,writerSha256=sha(writer),reusedHelperSha256=sha(helper),independentExpectedOriginalLiteral=True,MainOrTestChanged=False,productTestsExecuted=0,actualBackendAndHeldClassActions=0,scope='TOOL_ONLY_NOT_PRODUCT_PT_OR_COVERAGE',bug='BUG-2717',horizontal='YKT-2375');(O/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,toolAssertions=6,productTestsExecuted=0)))
