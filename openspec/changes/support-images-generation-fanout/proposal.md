# Proposal: support-images-generation-fanout

## Why

Lumina needs to request multiple image variants in one OpenAI-compatible
`/v1/images/generations` call without serializing all work in the application
layer. The upstream `image_generation` tool still accepts one image per
Responses call, so codex-lb must fan out a public `n > 1` request into bounded
single-image internal calls and aggregate the result.

## What Changes

- Allow `/v1/images/generations` to accept `n` from 1 through the configured
  `images_max_n` value.
- Split multi-image generation requests into one internal Responses request per
  requested image, each with the upstream tool count fixed to one.
- Run child requests with configurable image fan-out parallelism while using
  image-specific global and per-account admission gates.
- Aggregate child results into ordered public `data[]` entries and aggregate
  image token usage into one public usage block.
- Keep `/v1/images/edits` single-image until a separate edit fan-out design is
  added.

## Impact

- Adds image generation concurrency settings for operators.
- Changes the public Images generation contract for `n > 1` from rejection to
  bounded fan-out.
- Keeps the existing single-image path intact for lower-risk compatibility.
