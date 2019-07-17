from mock import patch
from bonodoo import OdooServer, OdooReader
import bonobo
from bonobo.nodes.io.csv import CsvWriter
from bonobo.structs.graphs import Graph
import unittest
import tempfile
import os
import ast


class TestSignature(unittest.TestCase):
    def test_bonodoo(self):
        server = OdooServer(
            hostname='localhost',
            user='admin',
            password='admin',
            database='test'
        )
        folder = tempfile.TemporaryDirectory()
        filename = 'test_file.csv'
        value_1 = {'id': 2}
        value_2 = {'id': 3}
        read = OdooReader(model='res.users', config=server, domain=[])
        with patch('xmlrpc.client.ServerProxy') as mk:
            mock_auth_server = mk.return_value
            mock_auth_server.login.return_value = 1
            server.authenticate()
            mk.assert_called()
        with patch('xmlrpc.client.ServerProxy') as mk:
            mock_auth_server = mk.return_value
            mock_auth_server.execute_kw.return_value = [value_1, value_2]
            graph = Graph()
            graph.add_chain(read, CsvWriter(filename, fs='fs.data'))
            bonobo.run(graph, services={
                'fs.data': bonobo.open_fs(folder.name)
            })
            mk.assert_called()
        with open(os.path.join(folder.name, filename), 'r') as f:
            lines = f.readlines()
            self.assertEqual(len(lines), 2)
            self.assertEqual(ast.literal_eval(lines[0]), value_1)
            self.assertEqual(ast.literal_eval(lines[1]), value_2)
        folder.cleanup()
