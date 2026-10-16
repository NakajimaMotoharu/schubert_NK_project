"""SSC287 precursor: real M/A/RODB + typed issued owner/launch/original inspection, mutation0."""
import ast
import base64
import hashlib
import inspect
import json
from pathlib import Path
import pg4058_original_read_profile as transport
import pg4060_original_profile_dual_stack as dual
import pg3509_tcp_pair_contract as tcp
import pg4080_failed_ordinary_full_capture as full

SLOT = 'pg4084-recovery-inspection-v1'


def java():
    original = (Path(transport.ROOT) / 'tools/quality/RootOriginalReadProfile.java').read_text()
    if hashlib.sha256(original.encode()).hexdigest() != 'd863da5bd27db7a0ff9c3a15907fe2d1b802064d084c798ff290dd247b24cfa3':
        raise ValueError('fixed qualified readonly owner/DB helper first')
    raw = original[:original.index('  private static MaintenanceRunFiles.Io measured()')]
    raw = raw.replace('RootOriginalReadProfile', 'RootRecoveryInspect')
    raw = raw.replace('import java.io.BufferedReader;', 'import dev.codex.schubert.nk.storage.ServiceConfigFiles;\nimport java.io.BufferedReader;')
    return raw + JAVA


JAVA = r'''
  private static void inspectRuntime() throws IOException {
    try (var directory = OwnedTransferDirectory.open(LinuxDirectoryCalls.create(),
        Path.of("/run/schubert-nk/startup"))) {
      var security = LinuxInodeSecurity.create();
      var permits = new StartupPermitFiles(directory, security);
      var epoch = permits.current();
      require(epoch.state() == StartupPermitRecords.State.ISSUED
          && epoch.boot().toString().equals("79a3260a-e16d-42bf-942a-b914ed144c28")
          && epoch.activation().equals(ORIGINAL));
      var permit = permits.readIssued();
      require(permit.boot().equals(epoch.boot()) && permit.epoch().equals(epoch.epoch())
          && permit.activation().equals(ORIGINAL)
          && permit.releaseDigest().equals("0a409301e552d8019440edcbf096ad9b20c15b35c0ee6472cd9c4cef65bd8dab"));
      StartupLaunchFiles.requireNoServiceResidue(directory, security);
      var launches = new StartupLaunchFiles(directory, security, epoch);
      var owner = launches.readOwner();
      // Expired parent's data only: never invoke parentsGuard or assert a live Root.
      require(owner.morning().invocation().equals("820851b8291a4c958bb34f6c48430ca3")
          && owner.morning().pid() == 696557 && owner.morning().startTicks() == 12873540);
      var api = launches.readLaunch(ServiceConfigFiles.Service.API);
      var web = launches.readLaunch(ServiceConfigFiles.Service.WEB);
      require(api.child().pid() == 758821 && api.child().startTicks() == 13004447
          && api.child().invocation().equals("c9444dbf2e6a43dca0d52ab220d59b1d"));
      require(web.child().pid() == 759868 && web.child().startTicks() == 13005817
          && web.child().invocation().equals("af0eb750d72443739bead6a879a51e13"));
      var observed = MaintenanceRunFiles.create().execute(session -> session.observeStartup(ORIGINAL));
      require(observed.completed().isPresent()
          && observed.completed().orElseThrow().outcome().exitCode() == 10);
      require(epoch.equals(permits.current()) && permit.equals(permits.readIssued())
          && owner.equals(launches.readOwner()) && api.equals(launches.readLaunch(ServiceConfigFiles.Service.API))
          && web.equals(launches.readLaunch(ServiceConfigFiles.Service.WEB)));
    }
  }

  public static void main(String[] args) throws Exception {
    require(args.length == 0 && LinuxInodeSecurity.create().effectiveUid() == 0);
    require(MaintenanceFileLock.create().tryExclusive(() -> checked(() ->
        StartupAdmissionFile.create().tryExclusive(admission -> checked(() -> {
          try (var db = database()) {
            db.setReadOnly(true); db.setAutoCommit(false); int backend;
            try (var s = db.createStatement(); var r = s.executeQuery(
                "select pg_backend_pid(),set_config('application_name','PG286-original-profile',false),pg_try_advisory_lock(71419602)")) {
              require(r.next()); backend = r.getInt(1); require(!r.wasNull() && r.getBoolean(3) && !r.wasNull() && !r.next());
            }
            heartbeat(db, backend); frame("ORIGINAL_PROFILE_READY " + backend);
            inspectRuntime();
            heartbeat(db, backend); frame("ORIGINAL_PROFILE_MEASURED");
            db.rollback();
          }
          return Boolean.TRUE;
        })).orElseThrow())).orElseThrow());
    frame("ORIGINAL_PROFILE_CLOSED");
    System.out.println("ORIGINAL_PROFILE_NORMAL_RETURN");
  }
}
'''


def payload(action):
    if action not in {'compile', 'run'}: raise ValueError('compile or inspect-only run')
    raw = transport.payload(action).replace(transport.SLOT, SLOT)
    line = next(line for line in raw.splitlines() if line.startswith('JAVA_B64='))
    raw = dual.once(raw, line, 'JAVA_B64=' + repr(base64.b64encode(java().encode()).decode()))
    raw = raw.replace('RootOriginalReadProfile.java', 'RootRecoveryInspect.java')
    raw = raw.replace('dev.codex.schubert.nk.batch.file.RootOriginalReadProfile', 'dev.codex.schubert.nk.batch.file.RootRecoveryInspect')
    if action == 'compile':
        old = "(save/'compile.safe.json').write_text(json.dumps(value,sort_keys=True))"
        raw = dual.once(raw, old, "value['classHashes']={str(p.relative_to(classes)):hashlib.sha256(p.read_bytes()).hexdigest()for p in classes.rglob('*.class')}\nrequire(r.returncode!=0 or bool(value['classHashes']))\n" + old)
    else:
        raw = dual.once(raw, " table={}\n for line in Path('/proc/net/tcp').read_text().splitlines()[1:]:\n  v=line.split()\n  if v[3]=='01':table[(v[1],v[2])]=v[9]",
                        " table=[line.split()for family in ['tcp','tcp6']for line in Path('/proc/net',family).read_text().splitlines()[1:]]")
        raw = dual.once(raw, "  client='0100007F:'+format(row['port'],'04X');server='0100007F:1538'\n  require(table.get((client,server))in inodes(pid)and table.get((server,client))in inodes(row['pid']))",
                        "  tcp_pair(table,row['port'],inodes(pid),inodes(row['pid']))")
        raw = dual.once(raw, 'def peers(value,owned=None):', 'import ipaddress\n' + inspect.getsource(tcp.endpoint) + '\n' + inspect.getsource(tcp.tcp_pair) + '\ndef peers(value,owned=None):')
        raw = dual.once(raw, 'select pid,classid,objid,objsubid,mode,granted from pg_locks',
                        'select pid,classid::bigint as classid,objid::bigint as objid,objsubid,mode,granted from pg_locks')
        frozen = json.loads((transport.W / (SLOT + '-compile') / 'manifest.safe.json').read_bytes())
        if frozen['actualExit'] != 0 or frozen['result']['actualExit'] != 0: raise ValueError('actual complete compile first')
        pins = frozen['result']['classHashes']
        raw = dual.once(raw, "require(not os.path.lexists(save/'run-reserved.private'))",
                        "require(compiled['classHashes']==" + repr(pins) + " and {str(p.relative_to(classes)):hashlib.sha256(p.read_bytes()).hexdigest()for p in classes.rglob('*.class')}==" + repr(pins) + ")\nrequire(not os.path.lexists(save/'run-reserved.private'))")
        definitions = []
        for n in ast.parse(full.BODY).body:
            if isinstance(n, ast.FunctionDef) and n.name in {'nss', 'detailed'}: definitions.append(ast.get_source_segment(full.BODY, n))
            if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'accounts' for t in n.targets): definitions.append(ast.get_source_segment(full.BODY, n))
        extra = 'actor_policy={};exec(' + repr(inspect.getsource(full.policy)) + ',actor_policy)\n' + '\n'.join(definitions)
        extra += "\noriginal_snapshot=snapshot\ndef snapshot():\n value=original_snapshot();value['detailedActors']={u:detailed(u,a)for u,a in value['actors'].items()};return value\n"
        raw = dual.once(raw, 'import dbus\nbus=', extra + '\nimport dbus\nbus=')
        raw = dual.once(raw, "['units','actors','durable','native','startup','runtime']", "['units','actors','detailedActors','durable','native','startup','runtime']")
        raw = dual.once(raw, "'newMARDDBTenRefNormalClose':True", "'newMARDDBTenRefNormalClose':True,'typedIssuedOwnerLaunchAndDoneInspected':True,'recoveryAuthorityIssued':False")
    compile(raw, '<typed recovery inspection no mutations>', 'exec')
    return raw


def main():
    namespace = {**transport.__dict__, 'payload': payload, 'SLOT': SLOT}
    exec(compile(inspect.getsource(transport.main), '<new typed inspection>', 'exec'), namespace)
    return namespace['main']()


if __name__ == '__main__': raise SystemExit(main())
