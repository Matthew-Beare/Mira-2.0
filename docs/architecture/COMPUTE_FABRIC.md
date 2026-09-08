# MIRA compute fabric architecture

## Status

This document defines the accepted architecture direction and the boundary implemented by `M2-M1-021`. It is not evidence that any private worker, GPU, wake/shutdown path, local model, self-hosted CI runner, telemetry collector or control-plane service is deployed.

## Core rule

Local compute is an **optional execution substrate** behind MIRA's existing provider-neutral capability/policy routing. It is not a second MIRA, not a second MIRROR, not a hard dependency for Standard users, and not a place for feature code to hard-code particular GPUs, model names, hostnames or private network topology.

The durable product seam is:

`feature intent -> semantic task requirements -> policy/capability routing -> selected runtime lane -> bounded execution adapter -> evidence/result -> canonical MIRA/MIRROR reconciliation`

`mira.runtime_router` remains the read-only policy/evidence selection boundary. Later worker-registry and scheduler packets feed runtime candidates into that boundary. They do not replace it.

## Public versus private configuration

Public/community source may define:

- generic runtime kinds such as local or hosted;
- generic capabilities such as coding, inference, Python, build, Git, container, deterministic analytics or provider interaction;
- generic health/availability/load states;
- policy modes and routing semantics;
- queue/task/checkpoint/provenance schemas;
- worker and telemetry protocols;
- benchmark schemas and model-profile contracts.

Private deployment configuration may bind those contracts to real infrastructure, including always-on control-plane machines, burst GPU workstations, laptops, LAN/VPN addresses, credentials, model installations, power controls and sensor mappings.

Private values do not enter the public repository. A sanitized public/community feature can require `gpu_inference` or `python_compute`; it cannot require a specific private machine.

## Standard and Advanced users

Standard MIRA remains functional with no local infrastructure. Hosted/native provider lanes continue to satisfy supported tasks.

Advanced onboarding extends the existing canonical onboarding/MIRROR configuration. It may record that optional infrastructure exists and which generic capabilities/policies the user wants enabled. It must not create a parallel setup wizard or make local compute mandatory.

## Compute modes

MIRA exposes three policy states:

- `off` — local candidates are ineligible. Merely detecting a worker must never override this.
- `normal` — local and hosted candidates may both be eligible. Deterministic policy, capability, health, availability, explicit provider preference, lane priority, load and cost ranking decide among them.
- `aggressive` — eligible local candidates are preferred over hosted candidates when no stronger explicit provider requirement/preference applies. This still does not override privacy policy, authorization, missing capability, health/fault state, availability, or interactive locks.

A private HOME-mode rule or phrase such as “I’m home. Hammer the local workers.” may set the user's current compute policy to aggressive through a later canonical policy/configuration path. Presence of HOME context alone is not authority to consume local compute.

## Runtime candidate contract

The M2-M1-021 router foundation treats a runtime lane as secret-free decision material containing, at minimum:

- stable lane/runtime identifiers;
- provider/service capability evidence already supported by MIRA;
- local versus hosted kind;
- generic runtime capabilities;
- availability state;
- health state;
- interactive/do-not-use lock;
- deterministic priority/load/cost ranks;
- explicit data-classification/approval policy;
- local compute mode.

The router does not wake machines, execute jobs, inspect thermal sensors, call models or mutate MIRROR. It only selects or blocks one lane with machine-readable reasons.

## Worker agent direction

A later worker agent advertises secret-free, freshness-bounded evidence such as:

- worker identity and agent version;
- operating system/runtime family;
- CPU and memory class/capacity;
- accelerator class, memory capacity and supported execution profiles;
- generic model profiles;
- Python/build/Git/container capabilities;
- allowed task classes and privacy policy;
- availability/load/health;
- heartbeat/freshness;
- telemetry endpoint capability, not public credentials.

The agent must use a restricted worker identity. Registration should prefer authenticated outbound registration or scoped LAN/VPN communication. No raw public shell, Python REPL or inference endpoint is part of the product contract.

## Durable control plane direction

A later control-plane packet owns durable execution state, not the runtime router. Its responsibilities include:

- queued/running/succeeded/failed/cancelled/blocked task lifecycle;
- priority and policy material;
- idempotency and leases;
- worker assignment;
- retry and cancellation;
- pause/preempt/resume;
- durable checkpoint metadata including packet/branch/SHA/log/test/runtime/model provenance where relevant;
- human-action blockers;
- exact result/readback evidence.

An always-on private node may host this control plane, but the public architecture describes the role rather than a particular server.

## Preemption and interactive protection

GPU and other burst jobs must be preemptible when practical. A worker can advertise an interactive/do-not-use lock that immediately makes it ineligible for new routed work. Later scheduler semantics must support drain and safe checkpoint/resume rather than assuming a running job owns the device forever.

Wake-on-LAN, safe shutdown, do-not-wake, do-not-shutdown, gaming/interactive and maintenance/fault states are separate later controls. The router must never infer permission to wake or shut down a machine from simple availability.

## Model profiles

Features request capabilities, not model brands. A private model profile may map a capability to an installed model/version/runtime and benchmark evidence. Initial evaluation can include current suitable gpt-oss and Qwen coding profiles, but those names are deployment candidates rather than public feature dependencies.

Every model-produced result that may influence canonical reality must preserve model/profile/version and provenance. Model-generated MIRROR material normally enters proposed/staged reconciliation state unless deterministic policy explicitly permits acceptance.

## Competitive Studio development

MIRA Studio may later support execution modes such as fast, normal, competitive and high-assurance.

Competitive/high-assurance development must isolate candidate implementations in separate Git branches/worktrees from a recorded base SHA, run deterministic tests/CI, preserve model/runtime provenance, permit cross-critique, and integrate only through reviewed work. A clean Git merge is not semantic verification.

## Trusted CI boundary

Trusted private runners must not execute arbitrary untrusted public-fork/PR code unrestricted on private machines. Later self-hosted CI work must validate repository/origin/trust state and isolate untrusted work from credentials, LAN resources and privileged identities.

## Deterministic computation and scenarios

Numerical and algorithmic work should use deterministic code where practical. Scenario inputs must be provenance-classified as one of:

1. MIRROR fact;
2. current external fact;
3. data-derived estimate;
4. explicit assumption.

Scenario evidence must preserve source, as-of time, confidence/uncertainty where applicable and calculation version. Unsourced LLM guesses must not be presented as precise probabilities or canonical scenario inputs.

## Observability and hardware safety

Later telemetry is Prometheus/Grafana-compatible and should cover worker/task health, utilization, queue state, local-versus-hosted execution, CI/tests, failures, duration and available compute/cooling sensors.

Hardware protection is deterministic. Sensor identifiers and warning/critical thresholds are configured from device evidence/user policy. MIRA must not invent a safe temperature, pump-speed, fan-speed, flow or power threshold. Critical configured faults stop affected workloads, fault the worker and may request safe shutdown according to explicit policy. Missing/stale critical sensors are handled as deterministic fault states according to configuration, not LLM judgment.

## Hosted escalation

Hosted execution remains valid when local quality is insufficient, urgency requires it, provider interaction requires a hosted/native lane, or a higher-authority review adds value. MIRA tracks local-versus-hosted evidence/cost where available. It must not automate consumer ChatGPT UI usage to evade plan or rate limits.

## Human-only blockers

Login, OAuth, CAPTCHA, 2FA, billing, provider approval and physical-device actions are human-only walls. Later durable task state must record `requires-human-action`, preserve the exact checkpoint and minimum action, immediately present the manual route, verify resulting state, then resume. Repeated blind retries are prohibited.

## Sheets and MIRROR

Google Sheets may project/control/reconcile worker and job state later, but MIRROR remains canonical. A MIRA Ops dashboard is a projection and safe control surface, not an independent worker/task database.

## Explicitly deferred from M2-M1-021

- worker daemon/agent implementation;
- durable queue and scheduler;
- local model runtime deployment;
- private hardware binding;
- WOL/shutdown;
- sensor readers or safety thresholds;
- Prometheus exporters/Grafana dashboards;
- self-hosted CI runner configuration;
- Studio branch orchestration;
- Advanced onboarding changes;
- GitHub escalation automation;
- deterministic analytics engine;
- human-blocker persistence;
- Sheets projection/control implementation;
- Job Search, People Discovery, Finance, Vehicle and Inventory domain implementations.

Those are preserved as child outcomes in `docs/work-packets/M2-M1-021.md` and should receive separate packet IDs as they become active.
