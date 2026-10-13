import ast
import unittest
from pg2432_current_boot_question_sources import sources,TOOLS,ARCHIVE,BOOT,production
from pg2433_current_boot_question_compile import compiler
from pg2434_current_boot_question_dispatch import source,STAGE
from pg2438_current_boot_question_post import payload


class ActualNames(unittest.TestCase):
    def test_actual_boot_full_graph_basenames_and_consumer_join(self):
        values=sources('a'*64);raw='\n'.join(values.values())
        self.assertIn(BOOT,raw)
        self.assertIn(BOOT.replace('-',''),values['pg526_term_witness.py'])
        for name,body in values.items():
            self.assertNotIn('3d69f5af',body)
            self.assertNotIn('current-normal-unused-tools-v1',body)
        body=source()
        self.assertIn("archive=P/'"+ARCHIVE+"'",body)
        self.assertIn("tools=P/'"+TOOLS+".tar'",body)
        self.assertIn('pg2433-frozen-v1.safe.json',body)
        self.assertIn('pg2434-stage-v1.exit',body)
        self.assertIn(TOOLS+'.tar',STAGE)
        self.assertIn(BOOT,STAGE)
        self.assertNotIn('3d69f5af',STAGE)
        self.assertIn('pg2433-',compiler())
        self.assertIn('Pg2432NativeArgumentTest',compiler())
        # Stage filenames and copied tar are the same exact literal, not a
        # shortened prefix-only assertion that missed the original defect.
        quoted=[n.value for n in ast.walk(ast.parse(body))if isinstance(n,ast.Constant)and isinstance(n.value,str)]
        self.assertIn(ARCHIVE,quoted)
        self.assertIn(TOOLS+'.tar',quoted)

    def test_independent_post_uses_new_placement_and_original_current_reader(self):
        raw=payload({'actualExit':0,'candidateSource':production(),'signatureVerified':True,
                     'manifestSha256':'a'*64,'signatureSha256':'b'*64})
        self.assertIn('pg2436-current-boot-question-placement-v1',raw)
        self.assertIn('pg2410-retired-current-before-v1',raw)
        self.assertNotIn('pg2416-question-unused-placement-v1',raw)


if __name__=='__main__':unittest.main()
