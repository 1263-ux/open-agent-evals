# Evaluation Protocol v0.1

## Purpose
Evaluate real task outcomes and inform method/model/workflow decisions. Do not optimize for a detached aggregate score.

## Before a run
Record the task objective, user context, deliverables, hard constraints, failure conditions, quality dimensions, budget, available tools, reference artifacts and evaluator.

## Evaluation types
| Type | Use | Interpretation |
|---|---|---|
| Controlled comparison | Compare methods/models while controlling conditions | Strongest comparative evidence; disclose residual confounders |
| Production observation | Observe a real production task | Realistic evidence, not automatically causal |
| Exploratory run | Explore a new model or method | Hypothesis generation only |
| Regression evaluation | Check known tasks after a change | Requires versioned inputs and rubric |

## Record conditions
Record model and version, host and version, agent configuration, skills/tools/MCP versions, input revision, environment, permissions, time/token/cost budgets, retries and human interventions.

If multiple variables change, label the run as multi-variable. Do not attribute the outcome to one factor without evidence.

## Report
Report goal attainment, hard gates, dimension-level evidence, artifacts, time-to-first-usable-result, end-to-end time, retries, human corrections, available resource costs, failures and missing data.

Do not force unlike domain qualities into one score. Compare operational metrics across domains; evaluate domain quality using domain-specific rubrics.

## Evaluator integrity
Use independent evaluation for high-impact or subjective outcomes. Record evaluator identity/type, version, model/prompt for automated judges, calibration status and disagreement. An agent's self-evaluation alone is not independent evidence.

## Reproducibility
A replayable run needs versioned inputs, environment, instructions, budget, rubric and evidence paths. If any are unavailable, list the gaps explicitly.
