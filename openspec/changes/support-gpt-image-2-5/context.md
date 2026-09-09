# Investigation and implementation evidence

Date: September 8, 2026. Initial investigation was read-only; the user subsequently authorized push, deployment, and testing. No account or credential changes were performed.

## Production rollout

Both Oracle services were updated through Coolify to `codexlb-native-images:1.22.0-20260908` with `pull_policy: never`, image `sha256:efd8c8d039621809dcdcc17990ec24c0808ec976c27156ad2449d28cd9f4a13e`. Build this local image on a replacement host with `docker build -t codexlb-native-images:1.22.0-20260908 openspec/changes/support-gpt-image-2-5`; the Dockerfile verifies the four upstream source checksums before applying the patch over the pinned official 1.22.0 digest. The older root Dockerfile is not the rollout artifact.

Both databases passed integrity checks after restart and retained their accounts and migration heads. Existing volumes remained attached. Each data volume contains a pre-patch backup under `backups/native-images-20260908`; original service definitions are saved in the approved host secret backup directory. Restoring those definitions through Coolify provides rollback without schema changes.

The shared deployed gateway generated a PNG through Lumina's configured production connection with alpha extrema 0–255. The dedicated account still requires reauthentication; its successful model listing does not prove generation capacity. An isolated container of the deployed Lumina image also generated and served a transparent PNG through the live gateway. Its first Flare edit returned an opaque RGB checkerboard despite the transparency request. A second edit requesting Sunburst and explicitly prohibiting a checkerboard also failed alpha validation. Record both as output failures, not passing transparency tests; generation/edit request fields and byte preservation are covered separately by adapter tests. Exact model, quality, and size control remain unverified.

The Images API allowlist rejected the two GPT Image 2.5 IDs locally. The Responses adapter preserved tool model and background fields, but OpenAI's configured `/backend-api/codex/responses` endpoint directly returned HTTP 400, `Transparent background is not supported for this model`, for both IDs. This reproduced with CodexLB validation bypassed.

The current official Codex client implements a dedicated Images transport:
- https://github.com/openai/codex/blob/main/codex-rs/codex-api/src/endpoint/images.rs
- https://github.com/openai/codex/blob/main/codex-rs/codex-api/src/images.rs
- https://developers.openai.com/api/docs/guides/image-generation

Direct requests to `/backend-api/codex/images/generations` and `/images/edits` succeeded for both requested IDs using the shared service's existing active account. Full model, quality, size, background, output format, compression, and moderation fields were supplied. The returned PNG headers indicated RGBA. Credentials were decrypted and used only inside the existing container process; the account database was opened read-only.

The local implementation adds exact model allowlists and uses the native transport only for requests created by the Images adapter. A Pydantic private attribute carries the native request through the existing account/retry service. Arbitrary public Responses calls retain their existing behavior. Image results are converted to the internal completion events, preserving bytes and `tool_usage.image_gen` accounting. Explicit masks and positive partial-preview counts are rejected for the new models in this initial adapter. Streaming requests receive a completion event without previews.

The local checkout is version 1.18.1, while the shared and dedicated deployed gateways are 1.22.0. `deployed-1.22.patch` contains the corresponding changes against files read from the deployed container, preserving its newer egress route and client metadata handling. A temporary local overlay is under `.local/native-images-1.22`; it is not the running deployment. Do not deploy the older checkout over the newer service.

An isolated Python process loaded the patched deployed modules in memory and exercised generation and editing against OpenAI. It returned native Images responses through the actual adapter/transport/collector code. Diagnostic artifacts are in `D:\Rayzor Studios\MerchBulkImageGen\output-native-codexlb`. Both PNGs have four channels and alpha extrema 0–255. The probe requested 1024×1024 but received 1278×1230; original bytes and actual dimensions were preserved.

## Upstream limitations and release verification

The user subsequently chose to work with native transparency and proposed `xhigh` as a discriminator. A live comparison requested Sunburst, transparent PNG, 1024×1024, and either `quality: "xhigh"` or `quality: "invalid-quality-probe"`. Both returned HTTP 200 with one image, `quality: "medium"`, and `background: "transparent"`. Returned sizes were 1271×1238 and 1261×1247. This demonstrates that accepting xhigh is not proof of honoring it or identifying the model. Native transparency is a usable practical outcome; distinct model and quality selection remain unverified capabilities, not prerequisites for using that outcome. No production configuration was changed.

### Built-in imagegen comparison

The built-in `image_gen` tool was also exercised on September 8 with a red-circle transparent-PNG prompt. Its result exposed only `image_url` and a save-path hint, with no effective-model field and no model-selection argument. The original PNG was copied to `D:\Rayzor Studios\MerchBulkImageGen\output-native-codexlb\built-in-imagegen.png`. It is 1254×1254 RGBA with alpha extrema 0–255 and the same `gpt-image` / `version 2.0` provenance label as the gateway samples. This is a comparison, not a known-Sunburst control; the label does not settle which backend model served either request.

OpenAI's September 8 launch announcement explicitly says Images 2.5 is rolling out to Codex across all tiers, while naming Sunburst and Flare as the two API models: https://openai.com/index/introducing-chatgpt-images-2-5/ . Therefore claiming that Images 2.5 inherently requires separate API billing is too strong. Product-level rollout is confirmed; exact account/request rollout and distinct Sunburst/Flare selection remain unverified. The current public Codex native-tool source still uses the `gpt-image-2` request label with automatic quality and size. This may be a stable alias, but that mapping is not exposed by the responses inspected.

The local imagegen skill's CLI fallback permits explicit model requests but no `OPENAI_API_KEY` is configured in the checked local environment, so an independent explicitly selected Sunburst API control was not run. Do not infer model identity from visual quality or from a prompt asking the generator to identify itself.

A negative control with `model: invalid-image-model-probe` also returned HTTP 200 and an image. The endpoint omitted an effective-model field. Therefore successful Sunburst/Flare requests do **not** establish which model executed or that the endpoint distinguishes these IDs. Exact size honoring is also unproven. Native transparent generation/editing is verified; the complete model migration must not be claimed as verified or archived yet.

The dedicated Lumina gateway separately returned `No available accounts`. Its account state was not changed. Verify every intended origin before release, and test the version-specific routed transport in the deployment environment. The isolated live probe used explicit direct egress and does not establish routed-egress behavior.

## Local validation

The image schema/translation/public route suite passed 222 tests, including negative cases for invalid native result counts, external attempts to select the internal transport, and unsupported masks. Eight native HTTP integration scenarios exercise both model IDs, generation/editing, and streaming/non-streaming through account selection and a local upstream server, checking upload bytes, exact result bytes, and usage. Ruff and scoped ty checks passed. The change and all 21 main OpenSpec specs validated. Lumina's focused client tests, TypeScript, lint, and production build passed.
