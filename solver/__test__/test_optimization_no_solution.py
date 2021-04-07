import unittest
from solver.helper.convert import constr_string_convert, obj_string_convert
from solver.helper.tableaus import TableauBuilder

from solver.optim import Optimization
from solver.simplex.plain_tableau import PlainTableau


class Test(unittest.TestCase):

    def setUp(self):
        from .factories import tableau_no_solution
        self.tb = tableau_no_solution()

    def test_output(self):
        table = self.tb.get()

        rows = list(table.table)
        self.assertEqual(list(rows[0]), [-1.0, -1.0, 1.0, 0.0, -1.0, -1.5])
        self.assertEqual(list(rows[1]), [1.0, 1.0, 0.0, 1.0, 0.0, 1.0])

    def test_run_for_solution(self):
        t = self.tb.get()
        result_table = Optimization().run_simplex(t.table, t.var_names)

        tabl = PlainTableau(
            result_table,
            var_names=["x1", "x2", "_s_1", "_s_2", "_a_1"],
            model_vars=['x1', 'x2'],
            base_var_indices=[1, 4]  # s=["x2", "_a_1"]
        )
        # print(t.collect_result())
        vv = tabl.intermediate_solution()

        self.assertEqual(vv._as_dict(), {'_a_1': 0.5, 'x2': 1.0})
        # self.assertEqual(sol, {'x1': 1.0, 'x2': 1.0})

    def test_no_solution_objective(self):
        result, sol = Optimization.min(self.tb.get())
        self.assertEqual(sol, {'x1': 1.0, 'x2': 1.0})


