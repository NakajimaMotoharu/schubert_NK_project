import json
import unittest
import pg4852_selected_public_evidence as role


class ExactPublicCases(unittest.TestCase):
    def test_allowlisted_fields_and_id(self):
        name='dev.codex.schubert.nk.api.bootstrap.ApiAdmittedConfigurationTest'
        raw=('<testsuite name="'+name+'" tests="1" failures="0" errors="0" skipped="0"><properties><property name="synthetic.private" value="DO_NOT_EXPORT"/></properties><testcase classname="'+name+'" name="ssc301001Fixture"/><system-out>DO_NOT_EXPORT</system-out></testsuite>').encode()
        value=role.cases(raw,name)
        self.assertEqual(value,[{'class':name,'method':'ssc301001Fixture','testId':'PT-OPS-API-CONFIG-SSC301001','actualResult':'PASS','newIndependentCase':True}])
        self.assertNotIn('DO_NOT_EXPORT',json.dumps(value))
        for changed in (raw.replace(b'failures="0"',b'failures="1"'),raw.replace(b'tests="1"',b'tests="2"'),raw.replace(b'/><system-out>',b'><skipped/></testcase><system-out>')):
            with self.assertRaises(ValueError):role.cases(changed,name)


if __name__=='__main__':unittest.main()
