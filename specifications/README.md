# Field Specifications (v0.1)

The files in this directory are **human-readable YAML field examples and draft conventions**, not formal JSON Schema documents and not yet guaranteed to be directly machine-validatable.

Current first-phase policy:

1. Keep the field names and nesting consistent between each specification example and its corresponding template.
2. Use the same required concepts and status vocabulary across examples.
3. Avoid introducing a validator or a large schema toolchain before repeated usage demonstrates the need.
4. When a field model changes, update its template and documentation in the same change.
5. A future formal JSON Schema/OpenAPI/JSON Type Definition should be introduced as a separately versioned compatibility contract, not silently implied by these YAML files.

For Method Card, compare `method-card.schema.yaml` with `../templates/method-card/method.yaml`; their top-level keys and nested field structure should match.
