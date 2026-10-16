"""Same artifact's explicit nonmutating inspection before one unused placement."""
import ast
from pyflakes.api import check
import pg4444_failed_current_unused_sources as previous

W, CURRENT, CURRENT_BOM, SOURCE, BOM, BEFORE, BOOT = previous.W, previous.CURRENT, previous.CURRENT_BOM, previous.SOURCE, previous.BOM, previous.BEFORE, previous.BOOT
TOOLS = 'pg4444-failed-current-unused-tools-v4'; SAVE = 'pg4448-failed-current-unused-placement-v4'
ARCHIVE = 'pg4448-shared-manager-release-v4.tar'; REMOTE = '/home/ubuntu/pg4448-shared-manager-input-v4'
PROOF_SAVE = SAVE + '-inspect'
qualify, candidate_bom, production, pinned = previous.qualify, previous.candidate_bom, previous.production, previous.pinned


def role_text(raw):
    return raw.replace(previous.TOOLS, TOOLS).replace(previous.SAVE, SAVE).replace(previous.ARCHIVE, ARCHIVE).replace(previous.REMOTE, REMOTE)


def sources(bom=None, before=None):
    previous.qualify(); previous.require(bom is None or bom == BOM); previous.require(before is None or before == BEFORE)
    values = {name:role_text(raw) for name,raw in previous.sources().items()}
    once = previous.once
    name = 'Pg4444UnusedStage.java'; raw = values[name]
    raw = once(raw, 'static final Path SAVE=', 'static Path SAVE=')
    marker = '  static String phase="PREFLIGHT";'
    raw = once(raw, marker, '''  static boolean inspectOnly;
  static boolean inspection(String[] args){
    require(args!=null && args.length==1 && ("inspect".equals(args[0]) || "place".equals(args[0])));
    return "inspect".equals(args[0]);
  }
''' + marker)
    raw = once(raw, '"place",Integer.toString(pid)', 'inspectOnly?"inspect":"place",Integer.toString(pid)')
    marker = '    require(args!=null && args.length==1 && "place".equals(args[0]) && !Files.exists(SAVE,LinkOption.NOFOLLOW_LINKS));'
    raw = once(raw, marker, '    inspectOnly=inspection(args);if(inspectOnly)SAVE=Path.of(' + repr('/var/lib/pgpt-s1-preservation/' + PROOF_SAVE).replace("'", '"') + ');\n    require(!Files.exists(SAVE,LinkOption.NOFOLLOW_LINKS));')
    raw = once(raw, 'phase="SIGNED_UNUSED_PLACEMENT";', 'phase=inspectOnly?"SIGNED_UNUSED_INSPECTION":"SIGNED_UNUSED_PLACEMENT";')
    raw = once(raw, 'unusedCandidatePlaced=true\\nallNewScopesReturnedNormally=true', 'unusedCandidatePlaced="+(!inspectOnly)+"\\ncandidateInspectOnly="+inspectOnly+"\\nallNewScopesReturnedNormally=true')
    raw = once(raw, 'privateWrite(SAVE.resolve("complete.private"),"', 'privateWrite(SAVE.resolve("complete.private"),("')
    raw = once(raw, 'oldUnknownNormalized=false\\n".getBytes(StandardCharsets.US_ASCII)', 'oldUnknownNormalized=false\\n").getBytes(StandardCharsets.US_ASCII)')
    values[name] = raw
    name = 'pg4444_native_refs.py'; raw = values[name]
    raw = once(raw, "SAVE = pathlib.Path('/var/lib/pgpt-s1-preservation/" + SAVE + "')",
                "INSPECT_ONLY = len(sys.argv)>1 and sys.argv[1]=='inspect'\nSAVE = pathlib.Path('/var/lib/pgpt-s1-preservation/" + SAVE + "' + ('-inspect' if INSPECT_ONLY else ''))")
    raw = once(raw, "(sys.argv[1] == 'place')", "(sys.argv[1] in ('inspect','place'))")
    raw = once(raw, 'def place_candidate():', 'def place_candidate(inspect_only=False):')
    marker = '            root.mkdir(mode=488)'
    raw = once(raw, marker, '''            if inspect_only:
                evidence=SAVE/'candidate-manifest-inspect.private.json'
                with evidence.open('xb')as f:
                    os.fchmod(f.fileno(),0o600);f.write(raw);f.flush();os.fsync(f.fileno())
                subprocess.run(['openssl','pkeyutl','-verify','-rawin','-pubin','-keyform','DER','-inkey','/etc/schubert-nk/deployment-key/pin.der','-in',str(evidence),'-sigfile',str(signature)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
                fd=os.open(SAVE,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
                try:os.fsync(fd)
                finally:os.close(fd)
                require(not os.path.lexists(root)and not os.path.lexists(sig))
                return
''' + marker)
    raw = once(raw, '            place_candidate()', '            place_candidate(INSPECT_ONLY)')
    # Explicit inspection proof artifact is the only extra private filename.
    # Before/release preserve the complete current data; the business release,
    # signature destination, approval/current/epoch/Units remain unmodified.
    values[name] = raw
    name = 'pg4444_native_owned_stop.py'; raw = values[name]
    raw = once(raw, 'import os, pathlib, stat', 'import os, pathlib, stat, sys')
    raw = once(raw, "ROOT = pathlib.Path('/var/lib/pgpt-s1-preservation/" + SAVE + "')",
                "ROOT = pathlib.Path('/var/lib/pgpt-s1-preservation/" + SAVE + "' + ('-inspect' if len(sys.argv)>1 and sys.argv[1]=='inspect' else ''))")
    raw = once(raw, "argv[-3:]==[b'Pg4444UnusedStage',b'place',b'']", "argv[-3:]in ([b'Pg4444UnusedStage',b'place',b''],[b'Pg4444UnusedStage',b'inspect',b''])")
    values[name] = raw
    name = 'Pg4444NativeArgumentTest.java'; raw = values[name]
    # Add an independent actual pure mode-method test without executing main or
    # ownership. Keep all original native argument checks and their count.
    marker = '  public static void main(String[] args)'
    if marker not in raw:
        marker = '  public static void main(String[] ignored)'
    previous.require(raw.count(marker) == 1, 'exact original argument fixture entry')
    # Insert a static initializer so the established main/check counter remains
    # unchanged; success requires these literal assertions too.
    position = raw.index(marker)
    raw = raw[:position] + '''  static {
    if(!Pg4444UnusedStage.inspection(new String[]{"inspect"}) || Pg4444UnusedStage.inspection(new String[]{"place"}))throw new AssertionError("literal mode");
    for(String[] bad:new String[][]{null,{}, {"other"},{"inspect","place"},{null}}){
      try{Pg4444UnusedStage.inspection(bad);throw new AssertionError("foreign mode");}catch(IllegalStateException expected){}
    }
  }
''' + raw[position:]
    values[name] = raw
    for name, raw in values.items():
        if name.endswith('.py'):
            header = "BUNDLE_HASH='fixed-before-transfer'\n" if name in ['pg4444_native_refs.py','pg4444_input_preflight.py'] else ''
            previous.require(check(header+raw,'<inspectable complete closed role>') == 0, name)
            compile(header+raw,name,'exec')
    return values


def inspection_has_no_release_writes(raw):
    """Verify the actual archive loop's inspect branch returns before extraction."""
    tree = ast.parse(raw)
    function = next(n for n in ast.walk(tree) if isinstance(n,ast.FunctionDef) and n.name == 'place_candidate')
    branch = next(n for n in ast.walk(function) if isinstance(n,ast.If) and isinstance(n.test,ast.Name) and n.test.id == 'inspect_only')
    previous.require(isinstance(branch.body[-1],ast.Return))
    text = ast.get_source_segment(raw,branch)
    previous.require('root.mkdir' not in text and 'extractall' not in text and 'sig.open' not in text)
    previous.require(branch.end_lineno < next(n.lineno for n in ast.walk(function) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr == 'extractall'))
    return True
