#!/usr/bin/env python3
#
# Copyright (c) Bo Peng and the University of Texas MD Anderson Cancer Center
# Distributed under the terms of the 3-clause BSD License.

import os
import tempfile

import pytest
from sos_notebook.test_utils import NotebookTest


class TestPy3Interface(NotebookTest):

    def test_prompt_color(self, notebook):
        '''test color of input and output prompt'''
        idx = notebook.call(
            '''\
            print('this is Python 3')
            ''',
            kernel="Python3")
        assert [255, 217, 26] == notebook.get_input_backgroundColor(idx)
        assert [255, 217, 26] == notebook.get_output_backgroundColor(idx)

    def test_cd(self, notebook):
        '''Support for change of directory with magic %cd'''
        output1 = notebook.check_output(
            '''\
            import os
            print(os.getcwd())
            ''',
            kernel="Python3")
        notebook.call('%cd ..', kernel="SoS")
        output2 = notebook.check_output(
            '''\
            import os
            print(os.getcwd())
            ''',
            kernel="Python3")
        assert len(output1) > len(output2)
        assert output1.startswith(output2)
        #
        # cd to a specific directory
        tmpdir = os.path.join(tempfile.gettempdir(), 'somedir')
        os.makedirs(tmpdir, exist_ok=True)
        notebook.call(f'%cd {tmpdir}', kernel="SoS")
        output = notebook.check_output(
            '''\
            import os
            print(os.getcwd())
            ''',
            kernel="Python3")
        assert os.path.realpath(tmpdir) == os.path.realpath(output)

    def test_expand(self, notebook):
        '''Test %expand --in'''
        notebook.call('var = 100', kernel="Python3")
        assert 'value is 103' in notebook.check_output(
            '''\
            %expand --in Python3
            value is {var + 3}
            ''',
            kernel='Markdown')
        assert 'value is 102' in notebook.check_output(
            '''\
            %expand ${ } --in Python3
            value is ${var + 2}
            ''',
            kernel='Markdown')

    def test_preview(self, notebook):
        '''Test support for %preview'''
        output = notebook.check_output(
            '''\
            %preview -n var
            var = list(range(100))
            ''',
            kernel="Python3")
        # in a normal var output, 100 would be printed. The preview version would show
        # type and some of the items in the format of
        #   0, 1, ... (100 items)
        assert 'list' in output and '100' in output and '1' in output and '99' not in output
        #
        # return 'Unknown variable' for unknown variable
        assert 'Unknown variable' in notebook.check_output(
            '%preview -n unknown_var', kernel="Python3")
        #
        # return 'Unknown variable for expression
        assert 'Unknown variable' in notebook.check_output(
            '%preview -n var[1]', kernel="Python3")

    def test_sessioninfo(self, notebook):
        '''test support for %sessioninfo'''
        notebook.call("print('this is Python3')", kernel="Python3")
        assert 'Python3' in notebook.check_output('%sessioninfo', kernel="SoS")
