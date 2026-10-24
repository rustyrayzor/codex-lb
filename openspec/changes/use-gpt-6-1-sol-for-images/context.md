# Images host model recovery

The hosted Lumina app submits native Images requests. Its `CODEXLB_DEFAULT_MODEL` setting does not control the gateway's internal Images host model. In deployed CodexLB 1.22.0, `app/modules/proxy/api.py` fixes that host model at `gpt-5.5`. The primary account now has an active `prolite` login and advertises `gpt-6.1-sol`, but its catalog omits `gpt-5.5`. This explains `no_plan_support_for_model` after reconnection.

For example, a request with public model `gpt-image-2.5-flare` must use `gpt-6.1-sol` for account selection while retaining `gpt-image-2.5-flare` in the native Images payload. This change does not establish which image model the upstream endpoint actually executes.

The repository source is 1.18.1 and the deployed native image is 1.22.0. Build the deployment layer from the existing native image, verify the deployed API module checksum, and change only its host constant and explanatory comment. Do not deploy the older root checkout over the service.

Keep the previous image available for rollback and preserve the existing data volume. The dedicated gateway remains `reauth_required`; changing a model cannot repair its login. Lumina's three-minute inactivity error is separate evidence and needs verification after the routing failure is corrected.

## Validation

The model regression failed against the original default. After the change, 157 image schema, translation, and route tests passed. The native transport cases cover generation and edits, both public image model IDs, and streaming and buffered responses. Ruff checks and formatting passed for the changed Python files. The change and all 21 main OpenSpec specs validated; existing main-spec style warnings remain.

The Oracle host contains the prepared image `codexlb-native-images:1.22.0-gpt61-20261023`, ID `sha256:185b6b2da50f5d1378e09fe54cd7eeba110c9b9fb4f30fd6d3579955dca3b6f4`. Its build verified the deployed API module checksum, applied the patch, and imported the resulting module to assert `gpt-6.1-sol`. The running services have not been switched to this image. No live generation success is claimed for the patch.
