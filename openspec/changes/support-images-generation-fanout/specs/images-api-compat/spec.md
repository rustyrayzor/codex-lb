## MODIFIED Requirements

### Requirement: OpenAI-compatible image generation endpoint

The system SHALL expose `POST /v1/images/generations` and accept the OpenAI Images API request shape (`model`, `prompt`, `n`, `size`, `quality`, `background`, `output_format`, `output_compression`, `moderation`, `partial_images`, `stream`, `user`). The endpoint MUST require `model` to start with `gpt-image-` and MUST treat `gpt-image-2` as the default if unspecified. The endpoint MUST NOT expose the internal "host" Responses model used to invoke the built-in `image_generation` tool.

#### Scenario: Compatible image generation request returns a JSON envelope

- **WHEN** a client sends `POST /v1/images/generations` with `model=gpt-image-2`, a non-empty `prompt`, and no `stream`
- **THEN** the service returns 200 with a JSON body of shape `{created, data: [{b64_json, revised_prompt}], usage}` containing exactly `n` (or 1 by default) entries

#### Scenario: Multi-image generations fan out into ordered child responses

- **WHEN** a client sends `/v1/images/generations` with `n > 1` and `n <= images_max_n`
- **THEN** the service dispatches one internal Responses `image_generation` tool call per requested image
- **AND** each child tool call omits `n`
- **AND** the returned public `data[]` entries are ordered by the original requested output index, not child completion order

#### Scenario: Multi-image generations are bounded by operator settings

- **WHEN** concurrent child image generations are running
- **THEN** the service MUST enforce the configured image request parallelism, global image in-flight limit, and per-account image in-flight limit

#### Scenario: Multi-image generation count is capped

- **WHEN** a client sends `/v1/images/generations` with `n < 1` or `n > images_max_n`
- **THEN** the service returns 400 with OpenAI `invalid_request_error` and `param: n`

### Requirement: OpenAI-compatible image edit endpoint

The system SHALL expose `POST /v1/images/edits` and accept the OpenAI Images Edits multipart shape (`image` repeatable file part, optional `mask`, plus `model`, `prompt`, `n`, `size`, `quality`, `background`, `output_format`, `output_compression`, `partial_images`, `stream`, `user`). The endpoint MUST apply the same model gating and parameter rules as `/v1/images/generations`, except edits MUST reject `n > 1` until edit fan-out is implemented.

#### Scenario: Multi-image edits remain unsupported

- **WHEN** a client sends `/v1/images/edits` with `n > 1`
- **THEN** the service returns 400 with OpenAI `invalid_request_error` and `param: n`
