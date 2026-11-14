# Asset Model

## Evaluation Pack
Versioned task family definition: task, inputs, constraints, rubric, execution instructions, references and provenance.

## Method Asset
Reusable problem-solving approach with applicability, assumptions, inputs, procedure, decision points, outputs, dependencies, evidence and failure boundaries. A method may reference Skills and tools but does not own or duplicate them.

## Experiment Record
Append-only account of a run: conditions, asset versions, configurations, observations, outcomes, artifacts, deviations and reproducibility gaps.

## Capability Profile
Evidence-backed observations about a specific model/agent/host/tool combination under stated task conditions. Never a context-free model ranking.

## Relations
- Every experiment references an Evaluation Pack version.
- Method verification claims reference experiment records.
- Capability Profiles reference experiment records and disclose sample coverage.
- External resources record source, version and license.
