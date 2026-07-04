# AgentDef — Microsoft Azure AI Ecosystem Mapping

## AgentDef ↔ Microsoft Copilot Studio ↔ Azure AI Foundry

This document describes how AgentDef concepts map to the main components of:

* Microsoft Copilot Studio
* Azure AI Foundry
* Azure AI Agents
* Semantic Kernel
* Prompt Flow
* Azure OpenAI

The goal is to decouple the semantic definition of the agent from the Microsoft-specific implementation.

**Note:** for Microsoft 365 Copilot declarative agents BOTH directions are implemented and round-trip tested: `agentdef adapt m365copilot` (adapter) and `agentdef import m365copilot` (importer). Copilot Studio has a working, validated importer (`agentdef import copilotstudio`, 94 real agent docs, 0 failures). The Azure AI Foundry, Semantic Kernel, and Prompt Flow mappings below remain conceptual/proposed; no adapter or importer exists for those yet.

---

## 1. High-Level Mapping

| AgentDef Concept | Copilot Studio                | Azure AI Foundry       | Semantic Kernel      | Prompt Flow     |
| ----------------- | ----------------------------- | ---------------------- | -------------------- | --------------- |
| `agent.md`        | Copilot Instructions          | Agent System Prompt    | Kernel Instructions  | Flow Context    |
| `manifest.yaml`   | Copilot Configuration         | Agent Definition       | Kernel Builder       | Flow Definition |
| `instructions/`   | Topics + Instructions         | Prompt Templates       | Prompt Functions     | Prompt Nodes    |
| `skills/`         | Actions                       | Tools / Functions      | Skills / Plugins     | Flow Components |
| `workflows/`      | Topics / Orchestration        | Agent Flows            | Planners             | Directed Flows  |
| `memory/`         | Conversation Memory           | Thread State           | Memory Connectors    | State Variables |
| `knowledge/`      | Dataverse / Knowledge Sources | RAG Indexes            | Memory Stores        | Retrieval Nodes |
| `tools/`          | Power Platform Connectors     | Azure Functions / APIs | Plugins              | Tool Nodes      |
| `runtime/`        | Environment Config            | Deployment Config      | Kernel Config        | Runtime Config  |
| `evals/`          | Test Chats                    | Evaluations            | Evaluation Pipelines | Batch Runs      |
| `telemetry/`      | Analytics                     | Azure Monitor          | Observability        | Traces          |
| `framework/`      | Export/Import                 | Deployment Templates   | Kernel Adapters      | Flow Export     |

---

## 2. Copilot Studio Mapping

### Conceptual Equivalent

Copilot Studio functions primarily as:

* orchestration layer
* conversational runtime
* business workflow interface

It is especially oriented toward:

* no-code / low-code
* enterprise copilots
* Power Platform integration
* conversational automation

---

### Suggested AgentDef Adapter

```text
framework/
└── microsoft-copilot-studio/
    ├── copilot-instructions.md
    ├── topics/
    ├── actions/
    ├── connectors/
    └── environment.yaml
```

---

### 2.1 `agent.md` → Copilot Instructions

The main content of:

* identity
* role
* behavior
* style

becomes:

* base instructions
* generative orchestration instructions

#### Example

```markdown
You are an editorial AI assistant specialized in summarizing weekly Twitter/X content into concise professional briefings.
```

---

### 2.2 `skills/` → Actions

#### AgentDef

```text
skills/
└── summarization/
```

#### Copilot Studio Equivalent

* Power Platform Actions
* AI Actions
* Prompt Actions
* Connector Actions

#### Example Actions

| AgentDef Skill | Copilot Action    |
| --------------- | ----------------- |
| summarization   | AI Builder Prompt |
| classification  | Topic Classifier  |
| prioritization  | Decision Flow     |
| retrieval       | Connector Action  |

---

### 2.3 `workflows/` → Topics

Copilot Studio organizes most logic as:

* Topics
* Trigger phrases
* Conversation branches

#### Example Mapping

| AgentDef Workflow Step | Copilot Topic         |
| ----------------------- | --------------------- |
| ingest links            | Input Topic           |
| summarize content       | AI Prompt Action      |
| group by topic          | Classification Branch |
| generate report         | Output Topic          |

---

### 2.4 `memory/` → Conversation State

#### Equivalent Components

* Variables
* Session state
* Dataverse records
* Conversation history

#### Example

```text
memory/
├── session.md
└── profile.json
```

could map to:

* conversation variables
* user profile tables
* persistent Dataverse entities

---

### 2.5 `tools/` → Power Platform Connectors

#### Examples

| AgentDef Tool | Copilot Connector |
| -------------- | ----------------- |
| twitter api    | Custom Connector  |
| sharepoint     | Native Connector  |
| jira           | Connector         |
| outlook        | Connector         |
| teams          | Connector         |

---

## 3. Azure AI Foundry Mapping

### Conceptual Equivalent

Azure AI Foundry acts more like:

* agent engineering platform
* orchestration environment
* AI infrastructure layer

Compared to Copilot Studio:

* lower-level
* more programmable
* more composable
* more suitable for advanced agents

---

### Suggested AgentDef Adapter

```text
framework/
└── azure-foundry/
    ├── agent.yaml
    ├── prompts/
    ├── tools/
    ├── flows/
    ├── evals/
    └── deployments/
```

---

### 3.1 `agent.md` → Agent Definition

Maps into:

* Azure AI Agent instructions
* system prompts
* orchestration directives

---

### 3.2 `skills/` → Agent Tools

#### Azure Foundry Equivalents

| AgentDef Skill | Azure Equivalent |
| --------------- | ---------------- |
| summarization   | Prompt Tool      |
| clustering      | Python Tool      |
| retrieval       | RAG Tool         |
| classification  | Function Tool    |
| reasoning       | Agent Planner    |

---

### 3.3 `workflows/` → Prompt Flow

Prompt Flow is conceptually very close to AgentDef workflows.

#### Example

```text
workflows/
└── weekly_digest.md
```

maps to:

```text
promptflow/
├── ingest_node
├── extraction_node
├── clustering_node
├── ranking_node
└── report_node
```

---

### 3.4 `knowledge/` → Azure AI Search / RAG

#### Equivalent Services

| AgentDef Knowledge | Azure Service      |
| ------------------- | ------------------ |
| documents           | Azure Blob Storage |
| ontology            | CosmosDB / Graph   |
| embeddings          | Azure AI Search    |
| retrieval           | RAG pipeline       |

---

### 3.5 `memory/` → Thread State

#### Equivalent Components

* Agent Thread Memory
* CosmosDB
* Redis
* Stateful orchestration

---

### 3.6 `runtime/` → Deployment Configuration

#### Example Mapping

```yaml
model: gpt-4.1
temperature: 0.2
max_tokens: 4000
```

becomes:

* Azure OpenAI deployment config
* model routing policy
* inference profile

---

### 3.7 `evals/` → Azure Evaluations

#### Equivalent Components

| AgentDef Eval       | Azure Equivalent     |
| -------------------- | -------------------- |
| hallucination tests  | AI Evaluations       |
| regressions          | Batch Evaluations    |
| golden outputs       | Benchmark datasets   |
| quality metrics      | Evaluation pipelines |

---

## 4. Semantic Kernel Mapping

Semantic Kernel is a particularly good fit for AgentDef concepts.

---

### Suggested Structure

```text
framework/
└── semantic-kernel/
    ├── plugins/
    ├── planners/
    ├── memory/
    └── kernel.yaml
```

---

### Mapping Table

| AgentDef     | Semantic Kernel    |
| ------------- | ------------------ |
| skills        | plugins            |
| workflows     | planners           |
| memory        | memory connectors  |
| tools         | native functions   |
| instructions  | semantic functions |
| orchestration | kernel execution   |

---

## 5. Recommended Architecture Strategy

### Important Principle

Do NOT build agents directly around:

* Copilot Studio
* Foundry
* LangGraph
* OpenAI SDK

Instead:

```text
AgentDef Canonical Definition
            ↓
   Microsoft Adapter Layer
            ↓
Copilot Studio / Foundry / SK
```

This allows:

* migration
* portability
* multi-runtime deployment
* framework independence

---

## 6. Recommended Enterprise Layout

```text
enterprise-agent/
│
├── agent.md
├── manifest.yaml
│
├── instructions/
├── skills/
├── workflows/
├── memory/
├── knowledge/
├── evals/
│
└── framework/
    ├── copilotstudio/
    │   └── agent-doc.md        # agentdef adapt copilotstudio (planned)
    └── m365copilot/
        └── declarativeAgent.json   # agentdef adapt m365copilot
```

Keep the canonical definition as the single source of truth and treat
everything under `framework/` as generated output: declare the targets in
a `sync:` block and let `agentdef sync --check` fail CI whenever a
generated Microsoft-side file drifts from the definition.
