import ast
import unittest
from copy import deepcopy
from pg2338_current_reloaded_pair_proof import payload,declared_configuration


class ReloadedPair(unittest.TestCase):
    def test_whole_exact_eleven_fds_and_parent_action_bytes(self):
        raw=payload();tree=ast.parse(raw)
        assignment=next(n for n in tree.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='EXPECTED_ARGV'for t in n.targets))
        self.assertTrue(ast.literal_eval(assignment.value).endswith(b'Pg2330ExistingRuntimeFinish\x00finish-runtime\x00'))
        for literal in ['101019','1808679','101050','1808864','101048','range(11)',"fixed={'4':'/'",'flags&os.O_NOFOLLOW','reloadKnownReturnedBeforePostGuard','configurationDeclaredDeltaAndClosedOnly']:
            self.assertTrue(literal in raw,'missing complete reload proof '+literal)
        for old in ['98485','98516','98514','prepare-resume','pidfd_send_signal','SIGTERM']:
            self.assertFalse(old in raw,'foreign/mutation '+old)

    def test_declaration_triple_fixed_all_32_and_closed_five_only(self):
        unit='schubert-nk-morning-controller.service';row={str(i):''for i in range(30)};row.update(ExecStart='old',DropInPaths='fixed')
        before={unit:row,'ordinary':dict(row)}
        after={unit:{**row,'ExecStart':'resume','DropInPaths':'fixed /run/systemd/system/schubert-nk-morning-controller.service.d/zz-pg2316-once-resume.conf'},'ordinary':{**row,'ExecStart':'closed'}}
        def parse(value):return ('/usr/bin/java','fixed'+(' --resume 91f5484b-9702-4c7c-97f3-dd5110a853f9'if value=='resume'else''),'no','n/a','n/a','0','(null)','0/0')
        self.assertTrue(declared_configuration(before,after,parse))
        self.assertFalse(declared_configuration(None,after,parse))
        self.assertFalse(declared_configuration(before,None,parse))
        self.assertFalse(declared_configuration(before,after,lambda _:None))
        self.assertFalse(declared_configuration(before,after,lambda _:('/usr/bin/java','foreign','no','n/a','n/a','0','(null)','0/0')))
        self.assertFalse(declared_configuration(before,after,lambda _:('/usr/bin/java','fixed','no','now','n/a','0','(null)','0/0')))
        for name in after:
            for key in after[name]:
                if key=='ExecStart':continue
                changed=deepcopy(after);changed[name][key]='foreign'
                self.assertFalse(declared_configuration(before,changed,parse))


if __name__=='__main__':unittest.main()
