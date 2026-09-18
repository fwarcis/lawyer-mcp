AGENTS.md

## Project purpose

This repository contains a temporary demonstration MCP server for the current Teable base "Досье".

The server exists to demonstrate to one lawyer what an AI agent with structured access to legal-work data can do. The current Teable schema and domain model are prototypes and are not assumed to represent the lawyer's eventual requirements.

Optimize for:

1. correctness and data integrity;
2. safety;
3. ease of understanding;
4. fast iteration during the demonstration;
5. reliable use of the official Teable API and MCP stack.

Do not optimize for reuse across arbitrary Teable bases, long-term extensibility, or speculative future requirements.

## Authoritative domain specification

`docs/teable-domain-contract.md` is the authoritative specification of the current domain model and known safety requirements.

Read it before designing or changing any domain operation.

Preserve its distinction between:

* `[S]` — enforced by the current schema;
* `[A]` — behavior of the current application;
* `[O]` — observed convention only;
* `[G]` — required access-layer guardrail;
* `[U]` — undefined business semantics.

Never silently promote `[A]` or `[O]` into a domain invariant.

Treat `[U]` as fail-closed for writes. If correctness of a mutation depends on an unresolved `[U]` rule, reject or postpone the mutation rather than guessing a policy.

If runtime Teable metadata conflicts with the domain contract, stop the affected work, document the discrepancy, and report it to the project owner. Do not work around the discrepancy.

Do not modify the domain contract without explicit approval from the project owner.

## Sources

Technical claims and implementation decisions must be based strictly on official primary sources.

For each dependency or platform:

1. Start with its official GitHub repository.
2. Read the repository README and documentation stored in that repository.
3. Follow external documentation only when the official repository or README links to it.
4. Do not use forums, Stack Overflow, Reddit, Medium, blogs, aggregators, search-result summaries, unofficial tutorials, or other third-party material as technical authority.

Before implementing Teable integration, verify from the current official sources:

* authentication;
* relevant API endpoints;
* request and response contracts;
* rate limits;
* capabilities and limitations of the currently used free plan;
* documented mutation semantics.

Before selecting an MCP framework or SDK, inspect its current official repository and documentation.

If documented behavior and observed behavior disagree, treat the discrepancy as blocking for the affected feature. Record it and ask the project owner before proceeding. Do not invent or silently adopt an undocumented workaround.

## Technology selection

Use Python.

Do not pin a Python version before selecting the actual stack. Select a current stable Python version supported well by the chosen dependencies.

Prefer mature, actively maintained, widely adopted frameworks and libraries.

Libraries, frameworks, validation systems, type systems, retry libraries, test tooling, code generators, and other established tools are strongly preferred when they:

* eliminate boilerplate;
* prevent invalid states or common mistakes;
* make behavior easier to understand;
* provide stronger validation or typing;
* implement difficult protocol behavior correctly;
* reduce custom infrastructure.

Do not reinvent functionality that a mature dependency already implements well.

Record consequential technology choices in `DECISIONS.md`.

## Code design

This is demonstration code intended to be read and understood, not a framework intended for years of extension.

Prefer linear and explicit execution flow.

A reader unfamiliar with MCP, the selected MCP framework, and the selected Teable client library should be able to locate the domain operation and understand its behavior quickly.

Ideally, infrastructure should recede from view and the reader should spend most of their attention on domain logic.

Avoid:

* speculative abstractions;
* unnecessary architectural layers;
* generic repository/service/factory patterns without a concrete need;
* wrappers that merely forward one or two obvious lines;
* premature generalization for other Teable bases;
* large functions containing several independent responsibilities.

Extract a small operation when doing so gives it meaningful domain semantics, isolates substantial complexity, improves validation or error handling, or hides an otherwise difficult call with non-obvious arguments.

Comments are strongly discouraged when naming and structure can express the same information.

Use comments only when the reason for code cannot reasonably be expressed by the code itself, such as:

* an unavoidable technology-specific workaround;
* a subtle external API constraint;
* unusual domain behavior whose reason would otherwise be lost.

## Quality requirements

Use defensive engineering practices that materially reduce defects.

At minimum:

* comprehensive Python type annotations;
* strict static type checking;
* automated formatting;
* linting;
* explicit error handling;
* structured validation at trust boundaries;
* deterministic tests;
* dependency version management;
* automated test execution;
* protection against accidental secret leakage.

Prefer tools that make invalid states difficult or impossible to represent.

Do not suppress type-checker, linter, validation, or runtime errors merely to make checks pass. Any unavoidable suppression must have a concrete technical justification.

Formatting matters, but correctness, safety, typing, validation, and readability take precedence over cosmetic formatting.

Propose the concrete testing strategy to the project owner before considering it final.

## Scope of MCP capabilities

Expose domain-oriented MCP tools only.

Good examples are concepts such as:

* finding a client;
* retrieving a client's dossier;
* creating a matter;
* recording an interaction;
* updating a task;
* attaching a document;
* preparing and confirming deletion.

Do not expose generic primitives such as unrestricted SQL execution, arbitrary record mutation, arbitrary Teable API calls, or generic schema mutation merely because they are easy to implement.

The tool contract itself should make unsafe operations difficult.

The MCP may perform CRUD operations on business records.

It must not expose or perform mutations of:

* tables;
* fields;
* field types;
* select choices as schema;
* relationships as schema;
* Views;
* View configuration;
* other Teable schema or presentation metadata.

If a schema or View change appears useful or necessary, explain the proposed change and wait for explicit approval before applying it.

## Data integrity

Data integrity is a primary requirement, including for this prototype.

Design domain mutations so that invalid data cannot be written merely because the caller or language model supplied an invalid combination.

Every mutation must validate all relevant:

* field types;
* current select choices;
* writable/read-only status;
* link targets;
* user targets;
* cardinality;
* required domain fields;
* established invariants;
* operation preconditions.

Do not rely solely on the language model to provide correct arguments.

Use the smallest practical set of required fields for creation. Codex should derive and propose this minimum from the current domain contract and schema, prioritizing both usability and data integrity. The project owner will review the proposal.

Do not require users to specify information that is unnecessary for establishing a valid initial entity.

Do not write computed, system-managed, reverse-derived, or otherwise read-only fields as independent values.

Use canonical Teable IDs internally rather than display names wherever the API permits it.

Runtime schema metadata has priority over stale assumptions in code.

## Consistency and logical transactions

Domain operations must preserve consistency as a complete operation, not merely perform a sequence of successful HTTP requests.

Where Teable provides an adequately documented atomic operation, use it.

Where one logical operation requires multiple upstream mutations and no documented cross-resource transaction exists, design explicit failure semantics. Use an established transactional, saga, compensation, or equivalent mechanism when necessary rather than reporting partial success as success.

Prefer existing libraries or framework facilities over implementing transaction machinery manually.

Mutations that logically belong together must either complete consistently or produce an explicit recoverable failure state.

Do not claim atomicity that the official Teable API does not document and that tests do not establish.

## Undefined domain rules

Never invent legal or business policy.

If a write would require deciding an unresolved `[U]` rule, fail closed and explain which policy must be decided.

Do not infer policy from:

* current sample data;
* a View configuration;
* a UI behavior;
* a field name;
* an observed correlation;
* what appears conventional for legal work.

The current database contains demonstration data and is not evidence of the lawyer's eventual business requirements.

## Create and update operations

Create and ordinary update operations do not require an additional user confirmation after the user has requested them, provided that:

* the operation is authorized;
* all required inputs are available;
* validation succeeds;
* all applicable domain invariants are preserved;
* no unresolved policy is required;
* the operation is not classified as destructive.

Updates should be partial where appropriate. Omitted values and explicit null/clear operations must remain semantically distinct.

## Deletion

Deletion requires explicit confirmation.

Use a two-stage operation:

1. inspect and present the impact;
2. execute only after explicit confirmation of that specific planned deletion.

Where dependencies exist, do not guess whether the desired behavior is restrict, unlink, reassign, cascade, archive, or another policy.

A confirmation must correspond to the impact that was actually inspected. Do not treat a generic `confirm=true` detached from the inspected operation as sufficient for destructive changes.

## Concurrency and idempotency

This is a single-user demonstration project, so avoid complex distributed infrastructure whose only purpose is extreme concurrent throughput.

Still provide reasonable protection against:

* accidental duplicate creation after retries;
* stale updates;
* lost updates where practical;
* repeated destructive commands;
* partial logical operations.

Use established framework/library mechanisms when available.

Correctness matters more than maximizing concurrency.

## Teable schema at runtime

Do not treat the snapshot in the domain contract as permanent runtime truth.

Load or verify the current Teable metadata required to validate operations.

At minimum account for:

* table IDs;
* field IDs;
* types;
* select choices;
* writable/computed state;
* link configuration and targets;
* relevant dependency information.

A rename must not break an integration that can operate by stable ID.

A deleted and recreated field is a different field even if it has the same display name.

If schema drift makes a requested mutation unsafe, reject the mutation rather than guessing a conversion.

## Credentials and secrets

Read credentials from environment variables or an appropriate secret mechanism selected for the environment.

Never place credentials in:

* source code;
* prompts;
* `AGENTS.md`;
* `README.md`;
* `DECISIONS.md`;
* test fixtures;
* committed configuration;
* logs;
* exception messages.

Codex may use a Teable credential supplied through its environment during development and integration testing.

Use only the permissions necessary for the current task when the platform supports such restriction.

## Development and demo isolation

The project must support at least two operational modes:

* `development`;
* `demo`.

The mode switch must be convenient and technically enforced. Do not rely on an instruction to the language model such as "do not access the data."

### Development mode

The developer's Codex may:

* run the MCP server;
* use the development MCP tools;
* access the current test Teable data as necessary for development;
* run integration tests against the test base.

All current data is synthetic/test data during this phase.

### Demo mode

The lawyer uses a separately configured Codex environment with the MCP server.

The developer's Codex must have no access to:

* the lawyer's MCP endpoint or process;
* Teable credentials used by the demo;
* record contents created during the lawyer's testing;
* MCP request or response payloads;
* files or other runtime artifacts containing those contents.

This restriction must be enforced by credentials, process/environment separation, filesystem permissions, MCP configuration, or other technical controls appropriate to the selected deployment.

The developer's Codex may receive sanitized operational telemetry from the demo environment only when that telemetry cannot disclose or reconstruct business or personal data.

Design the mode-switch mechanism and isolation approach before demo deployment and record the decision in `DECISIONS.md`.

## Lawyer's Codex environment

The lawyer should receive a convenient preconfigured Codex environment with:

* the MCP domain tools;
* ordinary capabilities needed for document and general knowledge work;
* deliberately constrained access to the host computer.

Host filesystem, shell, process, network, and other computer access must be explicitly scoped as narrowly as practical.

The lawyer's Codex must not be able to read or modify:

* MCP source code;
* MCP server configuration;
* MCP credentials;
* administrative secrets;
* infrastructure configuration that would expand its own access.

Do not assume prompt instructions are a sufficient security boundary.

Some MCP operations may eventually be restricted to the project owner. Do not invent those administrative capabilities in advance. Define them explicitly if and when a concrete need appears.

## Logging and observability

Maintain both operational/debug logging and an audit trail.

### Runtime/debug logs

Log enough technical information to diagnose:

* MCP lifecycle failures;
* Teable HTTP failures;
* retries;
* validation failures;
* rate limiting;
* latency;
* dependency failures.

Do not log secrets or business payloads.

### Audit log

For mutations, record appropriate non-sensitive metadata such as:

* operation/tool;
* actor or session identifier where available;
* correlation ID;
* target table/record IDs;
* outcome;
* error category;
* relevant revision/schema metadata;
* duration.

Do not store sensitive field values merely to make debugging easier.

In demo mode, anything made available to the developer's Codex must be sanitized so that record contents cannot be reconstructed.

## Error handling

Errors exposed through MCP should be structured enough for the agent to distinguish at least:

* invalid user input;
* missing required information;
* undefined domain policy;
* stale schema;
* stale record/concurrent modification;
* missing linked target;
* authorization failure;
* destructive confirmation required;
* retryable upstream failure;
* rate limiting;
* partial logical-operation failure;
* unexpected upstream Teable behavior.

Do not turn upstream failures into successful-looking empty results.

Do not expose secrets or sensitive payloads through errors.

## Testing

Codex should propose the detailed testing strategy for review by the project owner.

The resulting suite should prioritize properties that prevent incorrect writes, including:

* domain validation;
* invalid enum rejection;
* invalid/missing links;
* computed/read-only field rejection;
* required-field validation;
* undefined-policy rejection;
* idempotency;
* partial-operation behavior;
* deletion planning and confirmation;
* schema drift;
* relevant concurrency behavior;
* error mapping;
* secret and sensitive-data leakage.

Use integration tests against the test Teable environment where behavior cannot be established adequately by unit tests.

Do not claim an upstream guarantee merely because a mock behaves that way.

## Decision log

Maintain `DECISIONS.md`.

Record consequential decisions briefly, including:

* context/problem;
* chosen approach;
* why it was chosen;
* important alternatives rejected;
* relevant limitations or assumptions;
* authoritative source when the decision depends on external behavior.

Do not use `DECISIONS.md` as a chronological diary. Record decisions that help a future reader understand why the implementation has its current shape.

Do not record hidden model reasoning or chain-of-thought. Record concise engineering rationale and observable evidence.

## README

Maintain a concise `README.md` for a developer unfamiliar with the project.

It should contain only practical information needed to:

* install dependencies;
* configure non-secret environment variables and required secret names;
* run the MCP server;
* run checks/tests;
* connect it to Codex;
* switch supported operational modes when that mechanism exists.

Verify commands before documenting them.

Do not turn the README into an architecture document; use `DECISIONS.md` for consequential rationale and the domain contract for domain semantics.

## Git

Codex may create commits independently after completing coherent, tested units of work.

Use concise commit messages that describe the completed change.

Do not commit:

* secrets;
* generated sensitive data;
* runtime logs containing user data;
* temporary credentials;
* local environment files containing secrets.

Do not rewrite or discard unrelated user changes.

## Working method

Codex may make technical and architectural implementation decisions autonomously within this document's boundaries.

For substantial work:

1. inspect the relevant repository state;
2. read the relevant domain-contract sections;
3. inspect authoritative upstream documentation when external behavior matters;
4. identify unresolved assumptions;
5. choose the simplest safe implementation;
6. record consequential decisions;
7. implement;
8. run appropriate static checks and tests;
9. verify behavior against the real test integration when necessary;
10. update concise project documentation where behavior or commands changed;
11. commit a coherent completed change when appropriate.

Do not require approval for ordinary technical decisions that satisfy these rules.

Stop and ask the project owner when:

* a `[U]` domain rule must be decided;
* the domain contract appears incorrect or stale;
* Teable schema or Views need modification;
* official documentation conflicts with observed behavior;
* an operation cannot be made safely within the current requirements;
* a security boundary would need to be weakened;
* a destructive behavior has no approved policy;
* requirements materially conflict.

When asking, describe the concrete decision required rather than presenting speculative redesigns.

