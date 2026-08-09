"""
Rule engine. Each rule has a condition and an effect. Every firing is
logged on task.rule_log for explainability.
"""

from dataclasses import dataclass
from typing import Callable, List

from .models import Task, SchedulingContext, TaskStatus


@dataclass
class Rule:
    id: str
    description: str
    condition: Callable
    effect: Callable


def _boost(amount):
    def effect(task, ctx):
        task.score = round(task.score + amount, 4)
    return effect


def _flag_missed(task, ctx):
    task.status = TaskStatus.MISSED
    task.score = 0.0


def _block_if_dependencies_incomplete(task, ctx):
    task.score = 0.0
    task.rule_log.append("blocked: unresolved dependencies")


DEFAULT_RULES = [
    Rule(
        id="R1_overdue_missed",
        description="If deadline has passed and task not completed, mark as MISSED.",
        condition=lambda t, ctx: t.deadline < ctx.today and t.status == TaskStatus.PENDING,
        effect=_flag_missed,
    ),
    Rule(
        id="R2_high_risk_boost",
        description="Tasks with severe risk (4-5) get a priority boost.",
        condition=lambda t, ctx: t.risk >= 4,
        effect=_boost(0.10),
    ),
    Rule(
        id="R3_deadline_within_7_days_boost",
        description="Anything due within 7 days gets an urgency boost.",
        condition=lambda t, ctx: 0 <= (t.deadline - ctx.today).days <= 7,
        effect=_boost(0.15),
    ),
    Rule(
        id="R4_high_value_boost",
        description="Very high-value tasks get an extra nudge to break ties fairly.",
        condition=lambda t, ctx: t.value > 0 and t.score_breakdown.get("value_impact", 0) > 0.75,
        effect=_boost(0.05),
    ),
    Rule(
        id="R5_unresolved_dependency_block",
        description="A task cannot be scheduled if a dependency is not yet COMPLETED.",
        condition=lambda t, ctx: len(t.dependencies) > 0,
        effect=_block_if_dependencies_incomplete,
    ),
]


def apply_rules(tasks: List[Task], context: SchedulingContext, rules: List[Rule] = None, task_map: dict = None) -> List[Task]:
    if rules is None:
        rules = DEFAULT_RULES
    if task_map is None:
        task_map = {}
        for t in tasks:
            task_map[t.id] = t

    for task in tasks:
        if task.status not in (TaskStatus.PENDING, TaskStatus.SCHEDULED):
            continue

        task.rule_log = []  # reset so re-running doesn't stack duplicate boosts

        for rule in rules:
            if rule.id == "R5_unresolved_dependency_block":
                incomplete = []
                for d in task.dependencies:
                    dep_task = task_map.get(d)
                    if dep_task and dep_task.status != TaskStatus.COMPLETED:
                        incomplete.append(d)
                if not incomplete:
                    continue
                rule.effect(task, context)
                task.rule_log.append(rule.id + ": " + rule.description)
                continue

            if rule.condition(task, context):
                rule.effect(task, context)
                task.rule_log.append(rule.id + ": " + rule.description)

    return tasks