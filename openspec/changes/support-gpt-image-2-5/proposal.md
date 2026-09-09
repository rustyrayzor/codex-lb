# Support GPT Image 2.5

## Why

CodexLB rejects Sunburst and Flare at its Images API model allowlist. OpenAI documents both models with native transparency and additional quality settings. Lumina also receives a transparency rejection through Responses; the source of that separate failure must be verified before claiming live support.

## What changes

- Accept the exact Sunburst and Flare IDs on image generation and edit routes.
- Validate their custom dimensions, quality settings, and transparent output format.
- Route the new models from the Images API to the dedicated Codex Images endpoints, retaining the existing account/retry/usage lifecycle.
- Adapt native image results to the internal Responses event contract; streaming clients receive a final image event.
- Keep GPT Image 2 and legacy-model validation unchanged.

## Scope

No account configuration, authentication, default-model, or production deployment changes. Native transport applies only to Images API requests, not arbitrary conversational Responses requests. Explicit masks and partial previews are outside this initial native transport contract and must be rejected for the new models. Upstream access is a separate verification gate.
