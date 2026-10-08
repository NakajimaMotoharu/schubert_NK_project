"""Independent current tuple, full output inventory and unchanged external helper versions."""
import ast,pathlib,re,subprocess,tempfile,unittest

R=pathlib.Path(__file__).resolve().parent


class Test(unittest.TestCase):
    def test_all_compiler_outputs_are_new_and_noclobber_rejects_existing(self):
        for name in('pg557_native_compile_v1.sh','pg557_native_compile_v2.sh'):
            raw=(R/name).read_text();self.assertIn('set -euC',raw)
            outputs=re.findall(r'>\s*"\$task_work/([^"\n]+)"',raw)
            self.assertEqual(len(outputs),5);self.assertEqual(len(set(outputs)),5)
            self.assertTrue(all(s.startswith('pg557-')for s in outputs));self.assertNotIn('pg526-',raw)
        with tempfile.TemporaryDirectory()as t:
            p=pathlib.Path(t)/'literal-log';p.write_bytes(b'original')
            result=subprocess.run(['bash','-c','set -euC; printf changed > "$1"','literal',str(p)],capture_output=True)
            self.assertNotEqual(result.returncode,0);self.assertEqual(p.read_bytes(),b'original')

    def test_cohort_and_baseline_not_old_source(self):
        java=(R/'Pg557NativeStop.java').read_text();refs=(R/'pg557_native_refs.py').read_text();owned=(R/'pg557_native_owned_stop.py').read_text();driver=(R/'pg557_native_stop_v1.py').read_text()
        for old in('a2e98ce9','0.1.0-PG495','91a748b4','f72d6c82','07b5dc48','16431357068','15089848500','16889848500'):
            self.assertNotIn(old,java+refs+owned+driver)
        self.assertIn('8a524559eaa3a6560fb0c844210a0c90bcae04922f57113731b362a1b9b70787',refs)
        self.assertIn('pg556-completed-readonly-v2/before.private.json',refs)
        self.assertIn('pg557_native_refs.py',java)
        for name in('command','metadata','owner','show','tree','configuration_fields'):
            self.assertIn(name,refs)
        self.assertIn("'pathlib':pathlib",refs);self.assertIn("'sys':sys",refs);self.assertIn("'re':re",refs)
        self.assertIn('pg480-backup-tools-v3/pg480_backup_refs.py',refs)
        self.assertIn('pg477-completed-tools-v1/pg477_unit_references.py',refs)
        self.assertIn('from pg526_term_witness import',owned)
        self.assertIn('from pg526_native_term_witness import',owned)
        self.assertNotIn("W/'pg526-",driver)
        module=ast.parse(driver)
        payload=next(ast.literal_eval(n.value)for n in module.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='payload'for t in n.targets))
        self.assertIn('pg557-native-tools-v1',payload)
        self.assertIn('r.mkdir(mode=0o700)',payload)


if __name__=='__main__':unittest.main()
