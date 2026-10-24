## ADDED Requirements

### Requirement: Images routing uses GPT 6.1 Sol

The system SHALL use `gpt-6.1-sol` as the default internal host model for image generation and image edits. Native image requests MUST retain the publicly requested image model and existing generation options.

#### Scenario: An account supports GPT 6.1 Sol without GPT 5.5

- **GIVEN** an active account whose plan supports `gpt-6.1-sol` and does not support `gpt-5.5`
- **WHEN** a client requests image generation or an image edit
- **THEN** the system selects the account using `gpt-6.1-sol`
- **AND** forwards the requested public image model through the existing image transport
- **AND** does not reject the request for lack of `gpt-5.5` support
