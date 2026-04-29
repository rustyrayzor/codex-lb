# Tasks: support-images-generation-fanout

## 1. Contract and Validation

- [x] 1.1 Add settings for `images_max_n`, image request parallelism, global image in-flight, and per-account image in-flight.
- [x] 1.2 Allow `/v1/images/generations` `n=1..images_max_n`; reject values outside that range with `param: n`.
- [x] 1.3 Keep `/v1/images/edits` capped at `n=1`.

## 2. Fan-Out Adapter

- [x] 2.1 Build one child Responses request per requested output and keep each child tool config free of `n`.
- [x] 2.2 Assign child output indexes and unique prompt cache keys so account affinity does not collapse all children onto one cache key.
- [x] 2.3 Aggregate non-streaming child results into ordered `data[]`.
- [x] 2.4 Aggregate image token usage across children.
- [x] 2.5 Release API-key usage reservations and admission leases on success, failure, and cancellation.

## 3. Admission

- [x] 3.1 Add image-specific global in-flight admission.
- [x] 3.2 Add image-specific per-account admission.
- [x] 3.3 Wire image admission only for internal image-generation tool calls.

## 4. Release

- [x] 4.1 Add a GitHub Actions workflow that builds and publishes `ghcr.io/rustyrayzor/codex-lb-lumnius:<sha>`.
- [x] 4.2 Validate unit and integration coverage for image fan-out.
