# PyZX - Python library for quantum circuit rewriting
#        and optimization using the ZX-calculus
# Copyright (C) 2018 - Aleks Kissinger and John van de Wetering

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#    http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import unittest
import random
import sys
import os
from types import ModuleType
from typing import Optional

if __name__ == '__main__':
    sys.path.append('..')
    sys.path.append('.')
mydir = os.path.dirname(__file__)
from my_pyzx.generate import cliffordT, cliffords
from my_pyzx.simplify import clifford_simp
from my_pyzx.extract import extract_circuit
from my_pyzx.circuit import Circuit

np: Optional[ModuleType]
try:
    import numpy as np
    from my_pyzx.tensor import tensorfy, compare_tensors
    import math
except ImportError:
    np = None

SEED = 1337


@unittest.skipUnless(np, "numpy needs to be installed for this to run")
class TestCircuit(unittest.TestCase):

    def setUp(self):
        c = Circuit(3)
        c.add_gate("CNOT",0,1)
        c.add_gate("S",2)
        c.add_gate("CNOT",2,1)
        self.c = c

    def test_to_graph_and_back(self):
        g = self.c.to_graph()
        c2 = Circuit.from_graph(g)
        self.assertEqual(self.c.qubits, c2.qubits)
        self.assertListEqual(self.c.gates,c2.gates)

    def test_to_qasm_and_back(self):
        s = self.c.to_qasm()
        c2 = Circuit.from_qasm(s)
        self.assertEqual(self.c.qubits, c2.qubits)
        self.assertListEqual(self.c.gates,c2.gates)

    def test_to_qc_and_back(self):
        s = self.c.to_qc()
        c2 = Circuit.from_qc(s)
        self.assertEqual(self.c.qubits, c2.qubits)
        self.assertListEqual(self.c.gates,c2.gates)

    def test_to_quipper_and_back(self):
        s = self.c.to_quipper()
        c2 = Circuit.from_quipper(s)
        self.assertEqual(self.c.qubits, c2.qubits)
        self.assertListEqual(self.c.gates,c2.gates)

    def test_load_quipper_from_file(self):
        c1 = Circuit.from_quipper_file(os.path.join(mydir,"test_circuit.circuit"))
        c2 = Circuit.from_quipper_file(os.path.join(mydir,"test_circuit_nocontrol_noqubits.circuit"))
        self.assertEqual(c1.qubits, c2.qubits)
        self.assertListEqual(c2.gates,c2.gates)

    def test_cliffordT_preserves_graph_semantics(self):
        for i in range(1,5):
            with self.subTest(i):
                random.seed(SEED)
                g = cliffordT(i,20,0.2)
                c = Circuit.from_graph(g)
                g2 = c.to_graph()
                t = tensorfy(g,False)
                t2 = tensorfy(g2,False)
                self.assertTrue(compare_tensors(t,t2, False))

    def test_cliffordT_raises_exception_with_pcnot(self):
        self.assertRaises(ValueError, cliffordT, 1, 1, p_cnot=0.1)

    def test_cliffords_preserves_graph_semantics(self):
        random.seed(SEED)
        g = cliffords(5,30)
        c = Circuit.from_graph(g)
        g2 = c.to_graph()
        t = tensorfy(g,False)
        t2 = tensorfy(g2,False)
        self.assertTrue(compare_tensors(t,t2,False))

    def test_circuit_extract_preserves_semantics(self):
        random.seed(SEED)
        g = cliffordT(5, 70, 0.15)
        t = g.to_tensor(False)
        clifford_simp(g, quiet=True)
        c = extract_circuit(g)
        t2 = c.to_tensor(False)
        self.assertTrue(compare_tensors(t,t2,False))

    def test_two_qubit_gate_semantics(self):
        c = Circuit(2)
        c.add_gate("CNOT",0,1)
        cnot_matrix = np.array([[1,0,0,0],[0,1,0,0],[0,0,0,1],[0,0,1,0]])
        self.assertTrue(compare_tensors(c.to_matrix(),cnot_matrix))
        c = Circuit(2)
        c.add_gate("CZ",0,1)
        cz_matrix = np.array([[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,-1]])
        self.assertTrue(compare_tensors(c.to_matrix(),cz_matrix))

    def test_verify_equality_permutation_option(self):
        c1 = Circuit(2)
        c2 = Circuit(2)
        c2.add_gate("SWAP",0,1)
        self.assertTrue(c1.verify_equality(c2,up_to_swaps=True))
        self.assertFalse(c1.verify_equality(c2,up_to_swaps=False))

if __name__ == '__main__':
    unittest.main()
