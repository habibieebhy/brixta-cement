from __future__ import annotations

from dataclasses import dataclass

import pyomo.environ as pyo

from .chemistry import alumina_modulus, lime_saturation_factor, silica_modulus
from .model import RawMixProblem, RawMixSolution


@dataclass(frozen=True)
class BuiltRawMixModel:
    model: pyo.ConcreteModel
    material_names: tuple[str, ...]
    oxide_names: tuple[str, ...]
    oxide_expr: dict[str, object]


def build_pyomo_model(problem: RawMixProblem) -> BuiltRawMixModel:
    model = pyo.ConcreteModel(name="brixta_raw_mix_lp_v1")
    material_names = tuple(material.name for material in problem.materials)
    oxide_names = tuple(problem.materials[0].composition.as_dict())
    by_name = {material.name: material for material in problem.materials}

    model.MATERIALS = pyo.Set(initialize=material_names, ordered=True)
    model.fraction = pyo.Var(
        model.MATERIALS,
        domain=pyo.NonNegativeReals,
        bounds=lambda _m, name: (by_name[name].min_fraction, by_name[name].max_fraction),
    )
    model.total_fraction = pyo.Constraint(
        expr=sum(model.fraction[n] for n in model.MATERIALS) == 1.0
    )

    oxide_expr = {
        oxide: sum(
            by_name[n].composition.as_dict()[oxide] * model.fraction[n]
            for n in model.MATERIALS
        )
        for oxide in oxide_names
    }

    lsf_den = 2.8 * oxide_expr["SiO2"] + 1.18 * oxide_expr["Al2O3"] + 0.65 * oxide_expr["Fe2O3"]
    sm_den = oxide_expr["Al2O3"] + oxide_expr["Fe2O3"]
    am_den = oxide_expr["Fe2O3"]

    model.lsf_min = pyo.Constraint(expr=oxide_expr["CaO"] >= problem.lsf.minimum * lsf_den)
    model.lsf_max = pyo.Constraint(expr=oxide_expr["CaO"] <= problem.lsf.maximum * lsf_den)
    model.sm_min = pyo.Constraint(expr=oxide_expr["SiO2"] >= problem.sm.minimum * sm_den)
    model.sm_max = pyo.Constraint(expr=oxide_expr["SiO2"] <= problem.sm.maximum * sm_den)
    model.am_min = pyo.Constraint(expr=oxide_expr["Al2O3"] >= problem.am.minimum * am_den)
    model.am_max = pyo.Constraint(expr=oxide_expr["Al2O3"] <= problem.am.maximum * am_den)

    model.oxide_bounds = pyo.ConstraintList()
    for target in problem.oxide_targets:
        expr = oxide_expr[target.oxide]
        if target.minimum is not None:
            model.oxide_bounds.add(expr >= target.minimum)
        if target.maximum is not None:
            model.oxide_bounds.add(expr <= target.maximum)

    model.lsf_dev_pos = pyo.Var(domain=pyo.NonNegativeReals)
    model.lsf_dev_neg = pyo.Var(domain=pyo.NonNegativeReals)
    model.sm_dev_pos = pyo.Var(domain=pyo.NonNegativeReals)
    model.sm_dev_neg = pyo.Var(domain=pyo.NonNegativeReals)
    model.am_dev_pos = pyo.Var(domain=pyo.NonNegativeReals)
    model.am_dev_neg = pyo.Var(domain=pyo.NonNegativeReals)

    model.lsf_target = pyo.Constraint(
        expr=oxide_expr["CaO"] - problem.lsf.target * lsf_den
        == model.lsf_dev_pos - model.lsf_dev_neg
    )
    model.sm_target = pyo.Constraint(
        expr=oxide_expr["SiO2"] - problem.sm.target * sm_den
        == model.sm_dev_pos - model.sm_dev_neg
    )
    model.am_target = pyo.Constraint(
        expr=oxide_expr["Al2O3"] - problem.am.target * am_den
        == model.am_dev_pos - model.am_dev_neg
    )

    deviation = (
        problem.lsf.weight * (model.lsf_dev_pos + model.lsf_dev_neg)
        + problem.sm.weight * (model.sm_dev_pos + model.sm_dev_neg)
        + problem.am.weight * (model.am_dev_pos + model.am_dev_neg)
    )
    cost = sum((by_name[n].cost_per_tonne or 0.0) * model.fraction[n] for n in model.MATERIALS)
    model.objective = pyo.Objective(expr=deviation + problem.cost_weight * cost, sense=pyo.minimize)

    return BuiltRawMixModel(model, material_names, oxide_names, oxide_expr)


def solve_raw_mix(problem: RawMixProblem, *, solver_name: str = "appsi_highs") -> RawMixSolution:
    built = build_pyomo_model(problem)
    model = built.model
    solver = pyo.SolverFactory(solver_name)
    if not solver.available(exception_flag=False):
        raise RuntimeError(f"Pyomo solver {solver_name!r} is unavailable")

    results = solver.solve(model)
    status = str(results.solver.status)
    termination = str(results.solver.termination_condition)
    if termination not in {"optimal", "feasible"}:
        raise RuntimeError(
            f"raw-mix optimization failed: status={status}, termination={termination}"
        )

    fractions = {name: float(pyo.value(model.fraction[name])) for name in built.material_names}
    oxides = {oxide: float(pyo.value(expr)) for oxide, expr in built.oxide_expr.items()}

    return RawMixSolution(
        material_fractions=fractions,
        oxide_composition=oxides,
        lsf=lime_saturation_factor(oxides),
        sm=silica_modulus(oxides),
        am=alumina_modulus(oxides),
        objective_value=float(pyo.value(model.objective)),
        solver=solver_name,
        solver_status=status,
        termination_condition=termination,
    )
