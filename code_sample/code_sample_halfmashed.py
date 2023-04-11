"""Koninklijke Philips N.V., 2019 - 2020. All rights reserved."""

import os
import subprocess
import unittest
from unittest.mock import patch

from test.test_resource import TestResource
import pandas as pd
from condition_checker import check_condition
from core_extractor import get_file_names, get_report, filter_reg_files
from core_extractor import get_function_names
from core_extractor import get_func_body
from core_extractor import extractor
from core_extractor import get_py_annot_method_names
from extractor_cmd import validate_inputs


def get_log_data(line):
    """ function to get the line requested from log data"""
    ini_path = os.path.abspath(os.path.join
                               (os.path.dirname(__file__), os.pardir))
    file_name = os.path.join(ini_path, "functiondefextractor", "extractor.log")
    file_variable = open(file_name, encoding='utf-8', errors='ignore')  # pragma: no mutate
    all_lines_variable = file_variable.readlines()
    return all_lines_variable[-line]


class SimpleTest(unittest.TestCase):
    """Class to run unit test cases on the function definition extractor test"""
    src_files = os.path.join(TestResource.tst_resource_folder, "test_repo", "src")
    file_path = (os.path.join(os.path.dirname(__file__), os.pardir)).split("test")[0]

    def test_get_func_body(self):
        """Function to test filter_reg_files method"""
        files = get_file_names(self.src_files)
        filter_files = filter_reg_files(files, r'*.py,*.cpp,*.js,*.ts')
        expected = [os.path.join(self.src_files, "CerberusTest.java"),
                    os.path.join(self.src_files, "HelloController.java"), os.path.join(self.src_files, "test_c.c"),
                    os.path.join(self.src_files, "test_repo.java")]
        self.assertEqual(set(expected), set(filter_files))

    def test_get_function_names(self):
        """Function to test get_function_names method"""
        func, line_num = get_function_names(os.path.join(self.src_files, "HelloController.java"))
        expec_func = ['meth', 'index1', 'index2']  # Expected method names
        expec_line_num = [29, 61, 67]  # Expected method line numbers
        self.assertEqual(expec_func, func)
        self.assertEqual(expec_line_num, line_num)

    def test_process_python_test_extract(self):
        """Function to test get_function_body method"""
        func_body = get_func_body(os.path.join(self.src_files, "CerberusTest.java"), '24')
        func_body_format = func_body.split()
        func_body_formated = ''.join(func_body_format)
        expec_func_body = "publicvoidafterAll(){super.restoreStreams();}"
        self.assertEqual(expec_func_body, func_body_formated)

    def test_process_ad(self):
        """Function to test the complete end to end process of function definition extractor with
        Annotation and delta)"""
        dataframe = extractor((os.path.join(self.file_path, "test_resource", "test_repo")), annot="@Test", delta="5")
        df2_list = pd.read_excel(os.path.join(os.path.dirname(__file__), os.pardir, "test_resource",
                                              "codeextractor_T_T_A_D.xlsx")).sort_values('Uniq ID')
        dataframe["Code"] = dataframe["Code"].str.replace(os.linesep, "")
        df2_list["Code"] = df2_list["Code"].str.replace("\n", "")
        self.assertTrue(dataframe["Code"].equals(df2_list["Code"]))

    def test_process_annot(self):
        """Function to test the complete end to end process of function definition extractor"""
        dataframe = extractor((os.path.join(self.file_path, "test_resource", "test_repo")), None, None)
        df2_list = pd.read_excel(os.path.join(os.path.dirname(__file__), os.pardir, "test_resource",
                                              "codeextractor_T_T_A.xlsx")).sort_values('Uniq ID')
        dataframe["Code"] = dataframe["Code"].str.replace(os.linesep, "")
        df2_list["Code"] = df2_list["Code"].str.replace(os.linesep, "")
        df2_list["Code"] = df2_list["Code"].str.replace("\r", "")
        self.assertEqual(dataframe["Code"].values.tolist().sort(), df2_list["Code"].values.tolist().sort())

    def test_process_extract(self):
        """Function to test the complete end to end process of function definition extractor (True False annotation)"""
        dataframe = extractor((os.path.join(self.file_path, "test_resource", "test_repo")), annot="@Test",
                              report_folder=None)
        df2_list = pd.read_excel(os.path.join(os.path.dirname(__file__), os.pardir, "test_resource",
                                              "codeextractor_annot.xlsx"))
        dataframe["Code"] = dataframe["Code"].str.replace(os.linesep, "")
        df2_list["Code"] = df2_list["Code"].str.replace("\r\n", "")
        self.assertTrue(dataframe["Code"].equals(df2_list["Code"]))

    def test_filter_reg_files(self):
        """Function to test the complete end to end process of function definition extractor (True True)"""
        dataframe = extractor((os.path.join(self.file_path, "test_resource", "test_repo")), functionstartwith="test_",
                              report_folder=None)
        df2_list = pd.read_excel(os.path.join(os.path.dirname(__file__), os.pardir, "test_resource",
                                              "codeextractor_T_T.xlsx"))
        dataframe["Code"] = dataframe["Code"].str.replace("\r\n", "")
        df2_list["Code"] = df2_list["Code"].str.replace(os.linesep, "")
        self.assertEqual(len(dataframe["Code"]), len(df2_list["Code"]))

    def test_invalid_path(self):
        """Function to test valid input path"""
        self.assertEqual(extractor(os.path.join("abc", "sdr")), "Enter valid path")

    def test_extractor_cmd(self):
        """Function to test python annoted method names"""
        line_data = list([line.rstrip() for line in open(os.path.join(self.src_files, "python_annot_file.py"),
                                                         encoding='utf-8', errors='ignore')])
        self.assertEqual(str(get_py_annot_method_names(line_data, "@staticmethod", 0)), "['validate_return']")
        file_dir = os.path.join(self.file_path, "test_resource", "test_repo", "test")
        for file in os.listdir(file_dir):
            if file.startswith("ExtractedFunc_"):
                os.remove(os.path.join(file_dir, file))

    def test_get_report(self):
        """Function to test report generated"""
        dataframe = get_report(extractor((os.path.join(self.file_path, "test_resource", "test_repo")), None, None),
                               (os.path.join(os.path.dirname(__file__), os.pardir, "test_resource")))
        df1_list = pd.read_excel(os.path.join(os.path.dirname(__file__), os.pardir, "test_resource",
                                              "codeextractor_T_T_A.xlsx")).sort_values('Uniq ID')
        dataframe["Code"] = dataframe["Code"].str.replace(os.linesep, "")
        df1_list["Code"] = df1_list["Code"].str.replace(os.linesep, "")
        df1_list["Code"] = df1_list["Code"].str.replace("\r", "")
        self.assertEqual(dataframe["Code"].values.tolist().sort(), df1_list["Code"].values.tolist().sort())
        my_dir = os.path.join(os.path.dirname(__file__), os.pardir, "test_resource")
        for fname in os.listdir(my_dir):
            if fname.startswith("ExtractedFunc_"):
                os.remove(os.path.join(my_dir, fname))

    def test_py_annot_method_names(self):
        """Function to test pivot table"""
        res = check_condition("assert",
                              os.path.join(os.path.dirname(__file__), os.pardir, "test_resource", "Pivot_test.xlsx"),
                              "(")
        my_dir = os.path.join(os.path.dirname(__file__), os.pardir, "test_resource")
        for fname in os.listdir(my_dir):
            if fname.split('.')[-1].upper() == "HTML" and fname.startswith("Pattern_"):
                df1_pivot_table = pd.read_html(os.path.join(os.path.dirname(__file__), os.pardir, "test_resource",
                                                            "Test_Pivot_table_assert.html"))
                df2_pivot_table = pd.read_html(os.path.join(my_dir, fname))
                self.assertEqual(res, "Report files successfully generated at input path")
                self.assertEqual(str(df1_pivot_table[0].columns), str(df2_pivot_table[0].columns))
                os.remove(os.path.join(my_dir, fname))
            if fname.split('.')[-1].upper() == "XLSX" and fname.startswith("Pattern_Result_"):
                os.remove(os.path.join(my_dir, fname))

    def test_cmd_inputs(self):
        """Function to test command line input validation function"""
        validate_inputs((os.path.join(os.path.dirname(__file__), os.pardir, "test_resource",
                                      "codeextractor_T_T.xlsx")), "Excel file")
        self.assertTrue("Input path validated" in get_log_data(1).strip())
        with patch('sys.exit') as exit_mock:
            validate_inputs("no/path", "sample_path")
            self.assertTrue("Enter valid sample_path path" in get_log_data(1).strip())
            assert exit_mock

    def test_pivot_table(self):
        """Function to test command line working"""
        cmd = 'python -m functiondefextractor --p "%s"' \
              % (os.path.join(self.file_path, "test_resource", "test_repo", "test"))
        subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        my_dir = os.path.join(os.path.dirname(__file__), os.pardir, "test_resource", "test_repo", "test")
        for fname in os.listdir(my_dir):
            if fname.startswith("ExtractedFunc_"):
                df1_list = pd.read_excel(fname).sort_values('Uniq ID')
                df2_list = pd.read_excel(os.path.join(os.path.dirname(__file__), os.pardir, "test_resource",
                                                      "Extracted_java.xlsx")).sort_values('Uniq ID')
                df1_list["Code"] = df1_list["Code"].str.replace(os.linesep, "")
                df2_list["Code"] = df2_list["Code"].str.replace(os.linesep, "")
                df2_list["Code"] = df2_list["Code"].str.replace("\r", "")
                self.assertEqual(df1_list["Code"].values.tolist().sort(), df2_list["Code"].values.tolist().sort())


if __name__ == '__main__':
    unittest.main()