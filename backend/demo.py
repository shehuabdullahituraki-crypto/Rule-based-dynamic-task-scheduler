"""
Standalone demo - proves the engine works. Run with: python demo.py
"""
from datetime import date, timedelta

from app.engine.models import Task, TaskCategory, SchedulingContext
from app.engine.engine import run_full_cycle, add_task_dynamically

today = date(2026, 8, 5)

tasks = [
    Task("T1", "Submit annual compliance report", TaskCategory.URGENT, today + timedelta(days=5),
         penalty_if_missed=5000, effort_hours=4, risk=5),
    Task("T2", "Update team documentation", TaskCategory.ROUTINE, today + timedelta(days=20),
         value=3000, effort_hours=2, risk=2),
    Task("T3", "Gather requirements for new feature", TaskCategory.PROJECT,
         today + timedelta(days=45), value=800, effort_hours=3, risk=1),
    Task("T4", "Server maintenance window", TaskCategory.MAINTENANCE,
         today + timedelta(days=60), value=4500, effort_hours=1, budget_required=2000, risk=1),
    Task("T5", "Renew software license", TaskCategory.ADMIN,
         today + timedelta(days=3), penalty_if_missed=2000, effort_hours=1, budget_required=1500, risk=4),
    Task("T6", "Deploy feature to production", TaskCategory.PROJECT,
         today + timedelta(days=10), value=1200, effort_hours=2, risk=3,
         dependencies=["T3"]),
]

context = SchedulingContext(today=today, available_hours=8, available_budget=2000)

print("=" * 70)
print("INITIAL CYCLE: score -> rules -> rank -> schedule")
print("=" * 70)
result = run_full_cycle(tasks, context)

for t in result["ranked"]:
    print("#" + str(t.rank) + " " + t.id + " " + t.name[:40] + " score=" + str(t.score) + " status=" + t.status.value)
    for log in t.rule_log:
        print("      -> " + log)

print("\nSCHEDULED:", [t.id for t in result["scheduled"]])
print("WAITLISTED:", [t.id for t in result["waitlisted"]])

print("\n" + "=" * 70)
print("DYNAMIC EVENT: a new urgent task arrives mid-cycle")
print("=" * 70)
new_task = Task("T7", "URGENT: critical security patch required",
                 TaskCategory.URGENT, today + timedelta(days=2),
                 penalty_if_missed=10000, effort_hours=3, risk=5)

report = add_task_dynamically(new_task, tasks, result["scheduled"], result["waitlisted"], context)
print("Report:", report)
print("\nSCHEDULED after reallocation:", [t.id for t in result["scheduled"]])
print("WAITLISTED after reallocation:", [t.id for t in result["waitlisted"]])