## ADDED Requirements

### Requirement: GPT Image 2.5 request support

The system SHALL accept `gpt-image-2.5-sunburst` and `gpt-image-2.5-flare` on image generation and edit routes. These models SHALL accept `low`, `medium`, `high`, `xhigh`, `max`, and `auto` quality. Custom dimensions SHALL follow the same numeric limits as GPT Image 2. Transparent backgrounds SHALL require PNG or WebP output. The adapter SHALL preserve the selected model, quality, size, and background at the dedicated Codex Images endpoint. Existing GPT Image 2 and legacy-model rules SHALL remain unchanged.

#### Scenario: Native transparent output

- **WHEN** either new model is requested with transparent PNG or WebP output and valid dimensions
- **THEN** validation accepts the request and the native Images request retains those settings

### Requirement: Native transport lifecycle

The new-model Images routes SHALL use the dedicated Codex `images/generations` and `images/edits` endpoints with existing account selection, token refresh, error handling, and image usage settlement. Conversational Responses requests SHALL remain unchanged. Native image bytes and usage SHALL be preserved. Explicit masks and positive partial preview counts SHALL return an invalid-request error until supported by this adapter.

#### Scenario: Editing with reference images

- **WHEN** an edit is requested with one or more uploaded images
- **THEN** the native edit endpoint receives the prompt and image data URLs and returns the generated image through the existing public response contract

#### Scenario: Streaming result

- **WHEN** an Images client requests streaming without partial previews
- **THEN** it receives the final image completion event and actual image usage

#### Scenario: Invalid transparent output format

- **WHEN** either new model is requested with a transparent JPEG background
- **THEN** the endpoint returns an invalid-request error identifying `output_format`

#### Scenario: Existing model restrictions remain

- **WHEN** GPT Image 2 is requested with transparency or max quality
- **THEN** its existing invalid-request response remains unchanged
