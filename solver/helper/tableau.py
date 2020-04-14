import numpy as np


def _table_rows_columns(table):
    lc = len(table[0, :])
    lr = len(table[:, 0])
    return lr, lc


def _update_table(table):
    lr = len(table[:, 0])
    empty = []
    for i in range(lr):
        total = 0
        for j in table[i, :]:
            total += j ** 2
        if total == 0:
            empty.append(total)
    return empty


def _add_constraint(table):

    empty = _update_table(table)

    if len(empty) > 1:
        return True
    else:
        return False


def _add_objective(table):
    empty = _update_table(table)

    if len(empty) == 1:
        return True
    else:
        return False


LAST_ROW_IDX = -1


class PlainTableau:
    def __init__(self, table):
        self.__table = table
        lr, lc = _table_rows_columns(table)
        n_model_variables = lc - lr - 1

        v = []
        for i in range(n_model_variables):
            v.append('x' + str(i + 1))
        for i in range(lc - n_model_variables - 1):
            v.append('s' + str(i + 1))
        self._column_names = v

    @property
    def table(self):
        return self.__table

    @property
    def right_side(self):
        return self.__table[:, -1]

    def convert_min(self):
        table = self.table
        table[LAST_ROW_IDX, :-2] = [-1 * i for i in table[-1, :-2]]
        table[LAST_ROW_IDX, -1] = -1 * table[-1, -1]
        return PlainTableau(table)

    def column_names(self):
        return self._column_names

    """
    def variable_values(self):
        lrows, lcols = _table_rows_columns(self.table)
        for i in range(lcols):
            col = self.table[:, i]
            s = sum(col)
            m = max(col)
            if s == m:
    """

    def basis_indices(self):
        base_ids = set()
        _, lcols = _table_rows_columns(self.table)
        for i in range(lcols - 1):
            col = self.table[:, i]
            if float(sum(col)) == 1.0:
                base_ids.add(i)
        return base_ids

    def current_solution(self):
        table = self.__table

        lrows, lcols = _table_rows_columns(table)
        n_model_variables = lcols - lrows - 1

        val = {}
        bi = self.basis_indices()
        for i in range(lcols - 1):
            if i in bi:
                col = table[:, i]
                row_idx = np.where(col == max(col))[0][0]
                val[self._column_names[i]] = self.right_side[row_idx]
            else:
                val[self._column_names[i]] = 0.0
        # print(val)
        return val


class TableauBuilder:

    def __init__(self, var=None, cons=None):
        self.constraints = []
        self.objective = None

        self.var = var
        self.cons = cons
        self._table = None

        self.row_counter = 0
        self._result_table = None

    @property
    def table(self):
        return self._table

    def add_constraint(self, constraint):

        assert self.var is None or (len(constraint) == self.var + 1)
        if self.var is None:
            self.var = len(constraint) - 1

        self.constraints.append(constraint)

    def set_objective(self, objective):

        assert len(objective) == self.var + 1

        self.objective = objective

    def _build_constraint(self, eq):
        table = self.table
        if _add_constraint(table):
            lr, lc = _table_rows_columns(table)
            var = lc - lr - 1

            row = table[self.row_counter, :]

            for i in range(len(eq) - 1):
                row[i] = eq[i]
            row[-1] = eq[-1]

            row[var + self.row_counter] = 1

            self.row_counter += 1
        else:
            print('Cannot add another constraint.')

    def _build_objective(self, eq):
        table = self.table
        if _add_objective(table):
            # eq = simple_convert(eq)
            lr = len(table[:, 0])
            row = table[lr - 1, :]
            i = 0
            while i < len(eq) - 1:
                row[i] = eq[i] * -1
                i += 1
            row[-2] = 1
            row[-1] = eq[-1]
        else:
            print('You must finish adding constraints before the objective function can be added.')

    def get(self):
        self.cons = len(self.constraints)
        self._table = np.zeros((self.cons + 1, self.var + self.cons + 2))

        for c in self.constraints:
            self._build_constraint(c)

        self._build_objective(self.objective)

        return PlainTableau(self._table)
