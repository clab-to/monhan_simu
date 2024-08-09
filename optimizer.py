from enum import Enum

import pandas as pd
from ortools.linear_solver import pywraplp


class Solver_Ids(Enum):
    CLP_LINEAR_PROGRAMMING = "CLP_LINEAR_PROGRAMMING"
    CBC_MIXED_INTEGER_PROGRAMMING = "CBC_MIXED_INTEGER_PROGRAMMING"
    GLOP_LINEAR_PROGRAMMING = "GLOP_LINEAR_PROGRAMMING"
    BOP_INTEGER_PROGRAMMING = "BOP_INTEGER_PROGRAMMING"
    SAT_INTEGER_PROGRAMMING = "SAT_INTEGER_PROGRAMMING"
    SCIP_MIXED_INTEGER_PROGRAMMING = "SCIP_MIXED_INTEGER_PROGRAMMING"
    GUROBI_LINEAR_PROGRAMMING = "GUROBI_LINEAR_PROGRAMMING"
    GUROBI_MIXED_INTEGER_PROGRAMMING = "GUROBI_MIXED_INTEGER_PROGRAMMING"
    CPLEX_LINEAR_PROGRAMMING = "CPLEX_LINEAR_PROGRAMMING"
    CPLEX_MIXED_INTEGER_PROGRAMMING = "CPLEX_MIXED_INTEGER_PROGRAMMING"
    XPRESS_LINEAR_PROGRAMMING = "XPRESS_LINEAR_PROGRAMMING"
    XPRESS_MIXED_INTEGER_PROGRAMMING = "XPRESS_MIXED_INTEGER_PROGRAMMING"
    GLPK_LINEAR_PROGRAMMING = "GLPK_LINEAR_PROGRAMMING"
    GLPK_MIXED_INTEGER_PROGRAMMING = "GLPK_MIXED_INTEGER_PROGRAMMING"


class EquipmentOptimizer:
    def __init__(self, equipments_list: dict, **kwarg):
        # 装備組合せ作成回数の取得、デフォルト10個
        self.create_answer_count: int = kwarg.get("create_answer_count", 10)

        # 要求されている制約の辞書を取得
        self.constraints: dict = kwarg.get("constraints", {})

        # 装備/装飾品と紐づくステータスの辞書を取得
        self.eq_list: dict = equipments_list
        self.eq_count: int = len(list(equipments_list.values())[0])

        # solver用意
        solver_id = kwarg.get("solver_id", Solver_Ids.SAT_INTEGER_PROGRAMMING)
        self.solver = self._create_solver(solver_id)
        self.flags = {
            index: self.solver.BoolVar(f"rowindex_{index:04}")
            for index in range(self.eq_count)
        }

    def _create_solver(self, solver_id):
        return pywraplp.Solver.CreateSolver(solver_id.value)

    def _sum_rule(self, key):
        # すべての装備/装飾品に対して、
        # その装備/装飾品を利用するかのフラグとカラム別の値の積のリストを作成する
        is_use_flag_and_value = [
            self.flags[i] * self.eq_list[key][i] for i in range(self.eq_count)
        ]
        sum_value_in_use_equipments = self.solver.Sum(is_use_flag_and_value)
        return sum_value_in_use_equipments

    def _create_rule(self):
        # 条件追加
        # 防御力が最大であることを最適化の目的とする
        for key in ["def"]:
            self.solver.Maximize(self._sum_rule(key))
        # 各部位は全身1つずつのみ装備できる
        for key in ["head", "torso", "arm", "wst", "leg"]:
            self.solver.Add(self._sum_rule(key) <= 1)
        # 各サイズの空きスロットは0以下にならない
        for key in ["over-slot1", "over-slot2", "over-slot3", "over-slot4"]:
            self.solver.Add(self._sum_rule(key) >= 0)
        # スキルとか空きスロットとかの条件追加
        for key, value in self.constraints.items():
            self.solver.Add(self._sum_rule(key) >= value)

    def execute(self):
        if not set(self.constraints.keys()).issubset(set(self.eq_list.keys())):
            return []

        results = []
        self._create_rule()
        for _ in range(self.create_answer_count):
            status = self.solver.Solve()

            is_optimal = status == pywraplp.Solver.OPTIMAL
            is_feasible = status == pywraplp.Solver.FEASIBLE

            if is_optimal or is_feasible:
                equipment_names, defence = self._get_optimize_result()
                self._add_not_duplicate_rule()
                results.append(
                    {"equipment_name": equipment_names, "defence": defence}
                )

            else:
                print("The problem does not have an optimal solution.")
                break

        return results

    def _get_optimize_result(self):
        used_indexes = [
            index
            for index in range(self.eq_count)
            if self.flags[index].solution_value()
        ]
        equipment_names = [
            self.eq_list["name"][index] for index in used_indexes
        ]
        defence = sum(self.eq_list["def"][index] for index in used_indexes)
        return equipment_names, defence

    def _add_not_duplicate_rule(self):
        # 条件追加
        # 一度解として利用した組合せは再度選択されない
        used_indexes = [
            index
            for index in range(self.eq_count)
            if self.flags[index].solution_value()
        ]
        used_items = [self.flags[index] for index in used_indexes]
        self.solver.Add(self.solver.Sum(used_items) <= len(used_indexes) - 1)


def optimize(
    equipments: pd.DataFrame,
    create_answer_count: int,
    constraints: dict = {},
):
    # nanがあるとsolver.Sumの計算がうまくいかないのでfillnaでnanを0に置き換える
    # 意味としては0であってるのでこれでいい
    equipments_list = equipments.fillna(0).to_dict("list")
    optimizer = EquipmentOptimizer(
        equipments_list,
        constraints=constraints,
        create_answer_count=create_answer_count,
    )
    result = optimizer.execute()
    print(result)
