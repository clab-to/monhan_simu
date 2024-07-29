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


def optimize(equipments: pd.DataFrame, result_length):
    equipments_list = equipments.to_dict("list")

    solver = pywraplp.Solver.CreateSolver(
        Solver_Ids.SAT_INTEGER_PROGRAMMING.value,
    )
    row_number, _ = equipments.shape
    use_flag = {
        index: solver.BoolVar(f"rowindex_{index:04}")
        for index in range(row_number)
    }

    for key in ["over-slot1", "over-slot2", "over-slot3", "over-slot4"]:
        solver.Add(
            solver.Sum(
                [
                    use_flag[index] * equipments_list[key][index]
                    for index in range(row_number)
                ]
            )
            >= 0
        )
    for key in ["head", "torso", "arm", "wst", "leg"]:
        solver.Add(
            solver.Sum(
                [
                    use_flag[index] * equipments_list[key][index]
                    for index in range(row_number)
                ]
            )
            <= 1
        )

    solver.Maximize(
        solver.Sum(
            [
                use_flag[index] * equipments_list["def"][index]
                for index in range(row_number)
            ]
        )
    )

    for i in range(result_length):
        status = solver.Solve()

        if (
            status == pywraplp.Solver.OPTIMAL
            or status == pywraplp.Solver.FEASIBLE
        ):
            for index in range(row_number):
                if use_flag[index].solution_value():
                    print(equipments_list["name"][index])
            print(
                sum(
                    equipments_list["def"][index]
                    * use_flag[index].solution_value()
                    for index in range(row_number)
                )
            )

        else:
            print("The problem does not have an optimal solution.")
