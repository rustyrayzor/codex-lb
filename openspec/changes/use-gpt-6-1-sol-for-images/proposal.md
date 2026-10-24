## Why

The deployed 1.22.0 Images API selects `gpt-5.5` for account routing. The active primary account's model catalog includes `gpt-6.1-sol` and excludes `gpt-5.5`, so valid image requests can fail with `no_plan_support_for_model` before reaching native image generation.

## What changes

- Use `gpt-6.1-sol` as the internal Images host model.
- Preserve the requested public image model, native transport, generation settings, and account policies.
- Provide a checksum-verified image layer over the existing deployed native Images image, preserving its 1.22.0 implementation.

## Capabilities

### Modified capabilities

- `images-api-compat`: internal host model selection for image generation and edits.

## Scope

No account changes, schema changes, timeout changes, or unrelated proxy behavior. Production deployment requires authorization. The expired dedicated account is a separate operational blocker.
