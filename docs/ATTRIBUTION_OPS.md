# Attribution Evaluation Job — Operations

Attribution does not exist if it never runs. This job evaluates past decisions at T+7, T+30, and T+90 days and writes agent performance records. It is **observe-only**: it does not affect orchestrator behavior.

## Schedule (minimum viable)

- **Command:** `python -m core.attribution`
- **Frequency:** Once per day is enough.
- **No dashboards, alerts, or UI.** The system learns quietly in the background.

## How to run

From the project root (Alpha-Omega System):

```bash
python -m core.attribution
```

## Cron example (Linux / macOS)

```cron
0 2 * * * cd /path/to/Alpha-Omega-System && python -m core.attribution
```

Runs at 02:00 every day.

## Windows Task Scheduler

Create a daily task that runs:

- Program: `python`
- Arguments: `-m core.attribution`
- Start in: project root directory

## What it does

1. Finds decisions that are 7, 30, or 90+ days old and still missing that horizon’s outcome.
2. Fetches realized price return (and max drawdown) for the decision symbol over that horizon.
3. Updates the decision ledger with `outcome_7d` / `outcome_30d` / `outcome_90d`.
4. Computes per-agent attribution scores (directional, risk, calibration) and writes rows to `agent_attribution`.

No weighting, no user-facing output. Just: *is the system quietly learning in the background?*
