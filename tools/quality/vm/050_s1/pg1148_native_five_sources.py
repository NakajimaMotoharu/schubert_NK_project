"""SSC254/255 current five-role finite management, no startup authority.

PT-DEP-1148 binds independent1147 post/currentD5; never run old518 tools.
"""
import ast
import inspect
from pathlib import Path
from pg1134_failed_recovery_sources import SOURCE, BOM, BOOT, replace

HERE=Path(__file__).resolve().parent
BASE='/var/lib/pgpt-s1-preservation/pg1106-ordinary-cold-before-v1/proven-nested-once-v1/terminal-management-post-v1/after.private.json'
SHA='cfd139237f179e7531b94d28c1570c07af9612b476857f3eb479d9a732a7c0b9'


def common(text):
    return text.replace('Pg518','Pg1148').replace('PG518','PG1148').replace('pg518_','pg1148_').replace('pg518-native-role','pg1148-native-five')


def directory():
    text=common((HERE/'Pg518NativeRoleDirectory.java').read_text())
    text=replace(text,',"ordinary-bootstrap196"','')
    text=replace(text,'void owner(Path held,int uid,int gid)throws IOException;',
                 'void owner(Path held,int uid,int gid)throws IOException;\n    void mode(Path held,int mode)throws IOException;')
    text=replace(text,'public void owner(Path p,int u,int g)throws IOException{Files.setAttribute(p,"unix:uid",u);Files.setAttribute(p,"unix:gid",g);}',
                 'public void owner(Path p,int u,int g)throws IOException{Files.setAttribute(p,"unix:uid",u);Files.setAttribute(p,"unix:gid",g);}\n      public void mode(Path p,int m)throws IOException{Files.setAttribute(p,"unix:mode",m);}')
    # Public adapter is also used by parent-mode preparation; same security contract.
    text=replace(text,'prepare(common,role,uid,gid,new Io(){','prepare(common,role,uid,gid,systemIo());\n  }\n  static Io systemIo(){return new Io(){')
    text=replace(text,'    });\n  }\n  static boolean fixedRole','    };\n  }\n  static boolean fixedRole')
    marker='  static boolean fixedRole'
    parent='''  public static void prepareParent(OwnedTransferDirectory common)throws IOException {prepareParent(common,systemIo());}
  static void prepareParent(OwnedTransferDirectory common,Io io)throws IOException {
    require(common!=null && io!=null);
    common.atDirectory(p->{
      var before=io.metadata(p);require(directory(before,0,0,0711) && io.cleanTmpfs(p));
      var oldNames=names(p);require(oldNames.equals(Set.of("parent","backup","cleanup","expiry","root-api","inspector")));
      require(before.equals(io.metadata(p)));io.mode(p,0755);
      var after=io.metadata(p);require(directory(after,0,0,0755) && io.cleanTmpfs(p) && names(p).equals(oldNames));
      for(String k:List.of("dev","ino","uid","gid","nlink","size","lastModifiedTime"))require(before.get(k).equals(after.get(k)));
      require(after.equals(io.metadata(p)));return Boolean.TRUE;
    });common.sync();
  }
'''
    return replace(text,marker,parent+marker)


def directory_test():
    text=common((HERE/'Pg518NativeRoleDirectoryTest.java').read_text())
    text=replace(text,',"ordinary-bootstrap196"','')
    text=replace(text,'    public boolean cleanTmpfs',
                 '    public void mode(Path p,int m)throws IOException{f.point("beforeMode");Files.setAttribute(p,"unix:mode",m);f.point("afterMode");}\n    public boolean cleanTmpfs')
    marker='    System.out.println('
    extra='''    int parentPositions;
    try(var fixture=new Fixture(temp)){
      Files.setAttribute(fixture.f.parent,"unix:mode",0711);
      for(String role:List.of("parent","backup","cleanup","expiry","root-api","inspector"))Files.createDirectory(fixture.f.parent.resolve(role));
      Files.writeString(fixture.f.parent.resolve("parent/old.exec"),"independent-held-old-exec");
      var before=fixture.metadata(fixture.f.parent);fixture.f.position=0;fixture.f.counts.clear();fixture.f.events.clear();
      Pg1148NativeRoleDirectory.prepareParent(fixture.held,fixture);parentPositions=fixture.f.position;
      var after=fixture.metadata(fixture.f.parent);check(after.get("mode").equals(0040755));
      for(String k:List.of("dev","ino","uid","gid","nlink","size","lastModifiedTime"))check(before.get(k).equals(after.get(k)));
      check(Files.readString(fixture.f.parent.resolve("parent/old.exec")).equals("independent-held-old-exec"));
      try{Pg1148NativeRoleDirectory.prepareParent(fixture.held,fixture);throw new AssertionError("duplicate parent mutation");}catch(IOException expected){check(true);}
    }
    for(int point=1;point<=parentPositions;point++)try(var fixture=new Fixture(temp)){
      Files.setAttribute(fixture.f.parent,"unix:mode",0711);
      for(String role:List.of("parent","backup","cleanup","expiry","root-api","inspector"))Files.createDirectory(fixture.f.parent.resolve(role));
      Files.writeString(fixture.f.parent.resolve("parent/old.exec"),"independent-held-old-exec");
      int fault=point;fixture.f.hook=(name,n)->{
        if(!name.equals("clock") && !name.equals("effectiveUid") && fixture.f.position+1==fault)
          fixture.f.faults.put(name+"#"+n,new dev.codex.schubert.nk.storage.StorageIoException(dev.codex.schubert.nk.storage.StorageIoException.Reason.UNAVAILABLE));
      };
      try{Pg1148NativeRoleDirectory.prepareParent(fixture.held,fixture);throw new AssertionError("parent fault accepted");}catch(IOException expected){check(true);}
      check(Files.readString(fixture.f.parent.resolve("parent/old.exec")).equals("independent-held-old-exec"));
    }
    check(!Pg1148NativeRoleDirectory.fixedRole("ordinary-bootstrap196",999,999));
'''
    return replace(text,marker,extra+marker)


def preparation():
    text=common((HERE/'Pg518NativeRolePreparation.java').read_text())
    text=replace(text,'a2e98ce9e96c42425921e3686e8ae7a94bff9e6c',SOURCE)
    text=replace(text,'f6992c4de95477594987d2f10def06110d0c28cb6d4fd063da47bd0bab7e7d44',BOM)
    text=text.replace('PG495','PG1068').replace('pg495','pg1068').replace('cc9ed874-7f4f-450e-a188-8de1e42c8441',BOOT)
    text=text.replace('pg1148-native-five-tools-v3','pg1148-native-five-tools-v1')
    text=replace(text,'91a748b4-1abe-484c-9682-44f46429b324','343a5a1b-d064-47d5-88c2-31c36d7ba7a4')
    text=replace(text,',"ordinary-bootstrap196"','')
    text=text.replace('Pg513SingleApiIntent','Pg1144SingleApiIntent')
    marker='        for(String role:List.of('
    text=replace(text,marker,'        Pg1148NativeRoleDirectory.prepareParent(common);refs.check("roles");\n'+marker)
    return text.replace('nativeRoles6Prepared','nativeRoles5Prepared').replace('original24TablesAnd452BatchPreserved','original24TablesAnd604BatchPreserved')


def refs():
    import pg1148_native_five_policy as policy
    text=common((HERE/'pg518_native_role_refs.py').read_text())
    start=text.index('COVERAGE=');end=text.index('\ndef require(value)',start)
    text=text[:start]+inspect.getsource(policy)+text[end:]
    text=text.replace('cc9ed874-7f4f-450e-a188-8de1e42c8441',BOOT).replace('0.1.0-PG495','0.1.0-PG1068').replace('/proc/5872','/proc/242818')
    text=replace(text,'/var/lib/pgpt-s1-preservation/pg517-terminal-api-recovery-v1/after.private.json',BASE)
    text=replace(text,'df3c5fc4f918c52941cf8acee3b0d26e5c7b96dc404ec73c10b084c0835e19e2',SHA)
    start=text.index('def startup_preserved(');end=text.index('def values():',start)
    text=text[:start]+text[end:]
    start=text.index('def actor(');end=text.index('def execute():',start)
    text=text[:start]+'''def all_terminal():
 cohort();return {u:show(u,FIELDS)for u in UNITS}
'''+text[end:]
    start=text.index(" require(set(baseline)==");end=text.index(' backend=int(sys.argv[1]);',start)
    text=text[:start]+''' require(len(baseline['rows'])==24 and len(baseline['rows']['schubert.batch_runs'])==604)
 FIELDS.clear();FIELDS.update(baseline['units'][UNITS[0]])
 baseline['trees']={min(v,key=len):v for v in baseline['durable'].values()}
 baseline['trees'][STARTUP]=baseline['startup'];baseline['trees'][COVERAGE]=baseline['native']
 require(all(not pathlib.Path('/proc',str(pid)).exists()for pid in [404585,404614,253968]))
 namespace_config()
 require(hashlib.sha256(pathlib.Path(STARTUP+'/epoch.current').read_bytes()).hexdigest()=='b54c6d46594575e9c46f3d2e46e8a282f657bfeca6f194a38060f3533684e72d')
'''+text[end:]
    text=replace(text,"require(set(pathlib.Path(COVERAGE).iterdir())=={pathlib.Path(COVERAGE,n) for n in set(ROLES)|LEGACY});retired=True",
                 "require(set(pathlib.Path(COVERAGE).iterdir())=={pathlib.Path(COVERAGE,n)for n in set(ROLES)|LEGACY}and metadata(pathlib.Path(COVERAGE))[4]==stat.S_IFDIR|0o755);retired=True")
    text=replace(text," v=values();require(v==values());save('before.private.json'", " v=values();require(v['trees'][COVERAGE]==baseline['trees'][COVERAGE]);require(v==values());save('before.private.json'")
    # Dead legacy namespace-failure extractor is not an authority for this new scope.
    parsed=ast.parse(text);node=next(n for n in parsed.body if isinstance(n,ast.FunctionDef)and n.name=='namespace_failure_proof')
    lines=text.splitlines(keepends=True);text=''.join(lines[:node.lineno-1]+lines[node.end_lineno:])
    ast.parse(text);return text


def files():
    return {'Pg1148NativeRoleDirectory.java':directory(),'Pg1148NativeRoleDirectoryTest.java':directory_test(),
            'Pg1148NativeRolePreparation.java':preparation(),'pg1148_native_role_refs.py':refs()}
