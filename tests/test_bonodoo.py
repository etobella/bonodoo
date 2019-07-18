from mock import patch
from bonodoo import OdooServer, OdooReader, OdooModelFunction
import bonobo
from bonobo.nodes.io.csv import CsvWriter
from bonobo.structs.graphs import Graph
import unittest
import tempfile
import os
import ast


class TestBonodoo(unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.server = OdooServer(
            hostname='localhost',
            user='admin',
            password='admin',
            database='test'
        )

    def test_bonodoo_reader(self):
        folder = tempfile.TemporaryDirectory()
        filename = 'test_file.csv'
        value_1 = {'id': 2}
        value_2 = {'id': 3}
        read = OdooReader(model='res.users', domain=[])
        with patch('xmlrpc.client.ServerProxy') as mk:
            mock_server = mk.return_value
            mock_server.login.return_value = 1
            self.server.authenticate()
            mk.assert_called()
        with patch('xmlrpc.client.ServerProxy') as mk:
            mock_server = mk.return_value
            mock_server.execute_kw.return_value = [value_1, value_2]
            graph = Graph()
            graph.add_chain(read, CsvWriter(filename, fs='fs.data'))
            bonobo.run(graph, services={
                'fs.data': bonobo.open_fs(folder.name),
                'odoo.server': self.server,
            })
            mk.assert_called()
        with open(os.path.join(folder.name, filename), 'r') as f:
            lines = f.readlines()
            self.assertEqual(len(lines), 2)
            self.assertEqual(ast.literal_eval(lines[0]), value_1)
            self.assertEqual(ast.literal_eval(lines[1]), value_2)
        folder.cleanup()

    def test_bonodoo_reader_fields(self):
        folder = tempfile.TemporaryDirectory()
        filename = 'test_file.csv'
        value_1 = {'id': 2}
        value_2 = {'id': 3}
        read = OdooReader(
            model='res.users', domain=[], fields=['id'],
        )
        with patch('xmlrpc.client.ServerProxy') as mk:
            mock_server= mk.return_value
            mock_server.login.return_value = 1
            mock_server.execute_kw.return_value = [value_1, value_2]
            graph = Graph()
            graph.add_chain(read, CsvWriter(filename, fs='fs.data'))
            bonobo.run(graph, services={
                'fs.data': bonobo.open_fs(folder.name),
                'odoo.server': self.server,
            })
            mk.assert_called()
        with open(os.path.join(folder.name, filename), 'r') as f:
            lines = f.readlines()
            self.assertEqual(len(lines), 3)
            self.assertEqual(ast.literal_eval(lines[1]), value_1.get('id'))
            self.assertEqual(ast.literal_eval(lines[2]), value_2.get('id'))
        folder.cleanup()

    def test_bonodoo_function_multi(self):
        folder = tempfile.TemporaryDirectory()
        filename = 'test_file.csv'
        read = OdooModelFunction(
            model='res.users', function='test_function'
        )
        value_1 = {'id': 2}
        value_2 = {'id': 3}
        with patch('xmlrpc.client.ServerProxy') as mk:
            mock_server = mk.return_value
            mock_server.login.return_value = 1
            mock_server.execute_kw.return_value = [value_1, value_2]
            graph = Graph()
            graph.add_chain(read, CsvWriter(filename, fs='fs.data'))
            bonobo.run(graph, services={
                'fs.data': bonobo.open_fs(folder.name),
                'odoo.server': self.server,
            })
            mk.assert_called()
        with open(os.path.join(folder.name, filename), 'r') as f:
            lines = f.readlines()
            self.assertEqual(len(lines), 2)
            self.assertEqual(ast.literal_eval(lines[0]), value_1)
            self.assertEqual(ast.literal_eval(lines[1]), value_2)
        folder.cleanup()

    def test_bonodoo_function_single(self):
        folder = tempfile.TemporaryDirectory()
        filename = 'test_file.csv'
        read = OdooModelFunction(
            model='res.users', function='test_function'
        )
        value_1 = {'id': 2}
        with patch('xmlrpc.client.ServerProxy') as mk:
            mock_server = mk.return_value
            mock_server.login.return_value = 1
            mock_server.execute_kw.return_value = value_1
            graph = Graph()
            graph.add_chain(read, CsvWriter(filename, fs='fs.data'))
            bonobo.run(graph, services={
                'fs.data': bonobo.open_fs(folder.name),
                'odoo.server': self.server,
            })
            mk.assert_called()
        with open(os.path.join(folder.name, filename), 'r') as f:
            lines = f.readlines()
            self.assertEqual(len(lines), 1)
            self.assertEqual(ast.literal_eval(lines[0]), value_1)
        folder.cleanup()
