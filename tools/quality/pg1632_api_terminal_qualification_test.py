"""Independent literal API13 validator negative oracle, not Production test count."""
import copy
import unittest
from pg1632_api_terminal_qualification import PRODUCTION,qualify_result


class ContractQualificationTest(unittest.TestCase):
    def test_exact_api_thirteen_rejects_empty_missing_fail_skip_stale_or_static_gap(self):
        m={'productionSource':PRODUCTION,'actualExit':0,'mavenExit':0,'dependencyCompileExit':0,'globalCacheUnchanged':True,'dependencyTestGoalAbsent':True,'sourceInputsUnchanged':True,'staticIssues':dict.fromkeys(['protocol','storage','bootstrap','api'],0),'suites':{n:{'module':'api','tests':v,'failures':0,'errors':0,'skipped':0,'freshAfterBegin':True}for n,v in {'ApiProcessMainTest':4,'ApiProcessLifetimeTest':4,'ApiTerminalCaptureTest':3,'ApiCommittedFatalBindingTest':2}.items()}}
        self.assertEqual(13,qualify_result(m))
        variants=[None,{},dict(m,actualExit=1),dict(m,actualExit=False),dict(m,mavenExit=1),dict(m,dependencyCompileExit=1),dict(m,globalCacheUnchanged=False),dict(m,dependencyTestGoalAbsent=False),dict(m,sourceInputsUnchanged=False),dict(m,productionSource='old'),dict(m,suites={}),dict(m,staticIssues={'api':0})]
        for key,value in [('tests',0),('tests',14),('failures',1),('errors',1),('skipped',1),('freshAfterBegin',False),('module','bootstrap')]:
            wrong=copy.deepcopy(m);wrong['suites']['ApiTerminalCaptureTest'][key]=value;variants.append(wrong)
        for wrong in variants:
            with self.assertRaises(ValueError):qualify_result(wrong)


if __name__=='__main__':unittest.main()
