"""SS343 current completed run: distinct future activation preparation, no Root start."""
import ast
from pyflakes.api import check
import pg1980_fresh_completed_resume_sources as template
from pg2274_current_signed_owned_sources import sources as current_sources,SOURCE,BOM

TOOLS='pg2304-current-completed-resume-tools-v1'
SAVE='pg2308-current-completed-resume-preparation-v1'
CLASS='Pg2304FreshResumePreparation'
BASE='/var/lib/pgpt-s1-preservation/pg2274-native-stop-v1/after.private.json'
BEFORE='e7456ef531cde4d5e09161f401861ad0f718febbe786e59038e46dc869298a1e'
RUN='91f5484b-9702-4c7c-97f3-dd5110a853f9'


def bind(raw):
    pairs=[(template.TOOLS,TOOLS),(template.SAVE,SAVE),('Pg1980','Pg2304'),('pg1980','pg2304'),('PG1980','PG2304'),('PG1846','PG2126'),('pg1846','pg2126'),('0fd734195b4d5338f6b7e860e087cce561d49562',SOURCE),(template.BOM,BOM),(template.BEFORE,BEFORE),('pg1963-reload-ref-scoped-full-post-v1/before.private.json','pg2274-native-stop-v1/after.private.json'),('3d69f5af-6bac-46b1-a540-7591c4a79a0d','b2d6f605-61cf-425f-8fbd-12d606f6ee66'),('4148e3e8-f107-431a-ab27-d6e6d1f1772e',RUN),('9adbf05a-61d0-408b-b51d-ab19c7e5b16a','9be93262-fbb2-438f-b2b0-c4a27f5563a4'),('2026-10-12T18:20:32.598894Z','2026-10-13T15:01:53.237266Z'),('2026-10-12T18:46:52.677350Z','2026-10-13T15:28:38.568622Z'),('b5a12ee25dc44ec49b08f5d084b4052f','2f23a5f7362a48958f1cb24ed3fde748'),('81404764713','6647105558'),('83018953880','8284602928'),('/proc/389748','/proc/5204')]
    for old,new in pairs:raw=raw.replace(old,new)
    return raw


def one(raw,old,new):
    if raw.count(old)!=1:raise ValueError('one current completed resume boundary required')
    return raw.replace(old,new)


def sources():
    current=current_sources()
    result={bind(name):bind(raw)for name,raw in template.sources().items()}
    # Current parent may be GC'd. Use independently qualified current receipt and projection,
    # not the historical PID1 full-F18 assumption.
    for suffix in ['parent_receipt.py','warning_parent_projection.py','configuration.py','configuration_capture.py','row_bound.py','stable_journal.py']:
        result['pg2304_'+suffix]=current['pg2274_'+suffix].replace('pg2274','pg2304').replace('Pg2274','Pg2304').replace('PG2274','PG2304')
    java=result[CLASS+'.java']
    tree=ast.parse(current['pg2274_native_refs.py'])
    # Original verification includes the current ISSUED epoch, unchanged completed anchor,
    # no start intents, and same owner. Do not rewrite ISSUED to historical INVALID.
    text=current['Pg2274NativeStop.java']
    start=text.index('  static void verifyOriginalValues(')
    end=text.index('  public static void main(',start)
    original=text[start:end]
    start=java.index('  static void verifyOriginalValues(')
    end=java.index('  static void verifyCurrentIdentity(',start)
    java=java[:start]+original+java[end:]
    result[CLASS+'.java']=java
    result['Pg2304OriginalTupleTest.java']=current['Pg2274OriginalTupleTest.java'].replace('Pg2274','Pg2304').replace('Pg2304NativeStop',CLASS)
    if not any(isinstance(n,ast.FunctionDef)and n.name=='verify_pid1'for n in tree.body):
        raise ValueError('qualified current receipt boundary absent')
    for name,raw in result.items():
        if name.endswith('.py'):
            if check(raw,'<current completed resume '+name+'>'):raise ValueError('all current resume source globals required')
            compile(raw,'<current completed resume>','exec')
        if any(v in raw for v in ['PG1846','pg1980','b5a12ee25dc44ec49b08f5d084b4052f']):
            raise ValueError('historical authority survived current resume: '+name)
    return result
