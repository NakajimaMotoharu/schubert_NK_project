"""Independent19 property literals and strict complete parser negative vectors."""
import unittest
import pg4480_complete_inspect_pair_read as tool


class CompleteProperties(unittest.TestCase):
    def test_all_literal19_fields_required_without_reducing_old_image(self):
        expected={'Id','LoadState','ActiveState','SubState','MainPID','ControlPID','Job','InvocationID','ControlGroup','Result','ExecMainCode','ExecMainStatus','ExecMainStartTimestampMonotonic','ExecMainExitTimestampMonotonic','Type','KillMode','SendSIGKILL','RemainAfterExit','Restart'}
        self.assertEqual(expected,set(tool.PARENT_FIELDS))
        values={key:'literal-'+key for key in expected};raw=''.join(key+'='+value+'\n'for key,value in values.items())
        self.assertEqual(values,tool.strict_unit_values(raw,expected))
        for key in expected:
            bad=raw.replace(key+'='+values[key]+'\n','')
            with self.assertRaises(ValueError):tool.strict_unit_values(bad,expected)
        for bad in [raw+'Type=extra\n',raw+'Unknown=extra\n',raw[:-1],raw.replace('Id=','Id')]:
            with self.assertRaises(ValueError):tool.strict_unit_values(bad,expected)
        text=tool.payload()
        self.assertIn("'all19UnitFieldsAnd32SettingsPreserved':True",text)
        self.assertIn('first_config==second_config',text)
        self.assertIn("a==b and a['pid']==pid",text)
        self.assertIn("['units','actors','durable','native','startup','runtime']",text)


if __name__=='__main__':
    unittest.main()
