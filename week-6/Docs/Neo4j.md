---

title: Neo4j | Microsoft Learn
Url: https://learn.microsoft.com/en-us/agent-framework/integrations/by-component/context-providers/neo4j
description: Use Neo4j context providers for GraphRAG over existing knowledge graphs and persistent agent memory.
author: retroryan
ms.date: 2026-07-28T00:00:00.0000000Z

---

# Neo4j | Microsoft Learn

Neo4j supports two distinct Agent Framework context-provider patterns. They share a graph database but use separate packages and data flows.

| Pattern | Behavior |
| --- | --- |
| GraphRAG | Searches an existing indexed knowledge graph with vector, full-text, or hybrid retrieval and can traverse related entities with Cypher. |
| Persistent memory | Extracts entities, facts, preferences, and reasoning from conversations and builds a knowledge graph that can be recalled across sessions. |

## GraphRAG from an existing knowledge graph

The Neo4j GraphRAG Context Provider adds Retrieval Augmented Generation (RAG) capabilities to Agent Framework agents using a Neo4j knowledge graph. It supports vector, fulltext, and hybrid search modes, with optional graph traversal to enrich results with related entities via custom Cypher queries.

For other managed retrieval services, see [Azure AI Search](azure-ai-search) and [Microsoft Foundry](microsoft-foundry).

For knowledge graph scenarios where relationships between entities matter, this provider retrieves relevant subgraphs rather than isolated text chunks, giving agents richer context for generating responses.

### Why use Neo4j for GraphRAG?

- **Graph enhanced retrieval**: Standard vector search returns isolated chunks; graph traversal follows connections to surface related entities, giving agents richer context.
- **Flexible search modes**: Combine vector similarity, keyword/BM25, and graph traversal in a single query.
- **Custom retrieval queries**: Cypher queries let you control exactly which relationships to traverse and what context to return.


### Prerequisites

- A Neo4j instance (self-hosted or [Neo4j AuraDB](https://neo4j.com/cloud/aura/)) with a vector or fulltext index configured
- An Azure AI Foundry project with a deployed chat model and an embedding model (e.g. `text-embedding-ada-002`)
- Environment variables set: `NEO4J_URI`, `NEO4J_USERNAME`, `NEO4J_PASSWORD`, `FOUNDRY_PROJECT_ENDPOINT`, `FOUNDRY_MODEL`, `AZURE_AI_EMBEDDING_NAME`
- Azure CLI credentials configured (`az login`)
- Python 3.10 or later

### Installation

```bash
pip install agent-framework-neo4j
```

### Usage

```python
import os

from agent_framework import Agent
from agent_framework.foundry import FoundryChatClient
from agent_framework_neo4j import (
    Neo4jContextProvider,
    Neo4jSettings,
    AzureAISettings,
    AzureAIEmbedder,
)
from azure.identity import DefaultAzureCredential
from azure.identity.aio import AzureCliCredential

# Reads NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD from environment variables
neo4j_settings = Neo4jSettings()

# Reads FOUNDRY_PROJECT_ENDPOINT, AZURE_AI_EMBEDDING_NAME from environment variables
azure_settings = AzureAISettings()

sync_credential = DefaultAzureCredential()
embedder = AzureAIEmbedder(
    endpoint=azure_settings.inference_endpoint,
    credential=sync_credential,
    model=azure_settings.embedding_model,
)

neo4j_provider = Neo4jContextProvider(
    uri=neo4j_settings.uri,
    username=neo4j_settings.username,
    password=neo4j_settings.get_password(),
    index_name=neo4j_settings.vector_index_name,
    index_type="vector",
    embedder=embedder,
    top_k=5,
    retrieval_query="""
        MATCH (node)-[:FROM_DOCUMENT]->(doc:Document)
        OPTIONAL MATCH (doc)<-[:FILED]-(company:Company)
        RETURN node.text AS text, score, doc.title AS title, company.name AS company
        ORDER BY score DESC
    """,
)

async with (
    neo4j_provider,
    AzureCliCredential() as credential,
    Agent(
        client=FoundryChatClient(
            credential=credential,
            project_endpoint=azure_settings.project_endpoint,
            model=os.environ["FOUNDRY_MODEL"],
        ),
        instructions="You are a financial analyst assistant.",
        context_providers=[neo4j_provider],
    ) as agent,
):
    session = agent.create_session()
    response = await agent.run("What risks does Acme Corp face?", session=session)
```

### Key features

- **Index-driven**: Works with any Neo4j vector or fulltext index
- **Graph traversal**: Custom Cypher queries enrich search results with related entities
- **Search modes**: Vector (semantic similarity), fulltext (keyword/BM25), or hybrid (both combined)

### Resources

- [Neo4j Context Provider repository](https://github.com/neo4j-labs/neo4j-maf-provider)
- [PyPI package page](https://pypi.org/project/agent-framework-neo4j/)
- [Workshop: Neo4j Context Providers for Agent Framework](https://github.com/neo4j-partners/maf-context-providers-lab)


## Persistent agent memory

The Neo4j memory integrations store and recall agent interactions, automatically extracting entities and building a knowledge graph over time.

The providers manage:

- **Short-term memory**: Conversation history and recent context.
- **Long-term memory**: Entities, preferences, and facts extracted from interactions.
- **Reasoning memory**: Past reasoning traces and tool usage patterns.

### Why use Neo4j for agent memory?

- **Knowledge graph persistence**: Memories are stored as connected entities, not flat records, so the agent can reason about relationships between remembered information.
- **Automatic entity extraction**: Conversations are parsed into structured entities and relationships without a manually defined schema.
- **Cross-session recall**: Preferences, facts, and reasoning traces persist across sessions and surface through context providers.


### Prerequisites

- A Neo4j instance (self-hosted or [Neo4j AuraDB](https://neo4j.com/cloud/aura/)).
- A Microsoft Foundry project with a deployed chat model.
- An OpenAI API key or Azure OpenAI deployment for embeddings and entity extraction.
- Environment variables set: `NEO4J_URI`, `NEO4J_PASSWORD`, `FOUNDRY_PROJECT_ENDPOINT`, `FOUNDRY_MODEL`, `OPENAI_API_KEY`.
- Azure CLI credentials configured (`az login`).
- Python 3.10 or later.

### Installation

```bash
pip install neo4j-agent-memory[microsoft-agent]
```

### Usage

```python
import os
from pydantic import SecretStr
from agent_framework import Agent
from agent_framework.foundry import FoundryChatClient
from azure.identity.aio import AzureCliCredential
from neo4j_agent_memory import MemoryClient, MemorySettings
from neo4j_agent_memory.integrations.microsoft_agent import (
    Neo4jMicrosoftMemory,
    create_memory_tools,
)

# Pass Neo4j and embedding configuration directly via constructor arguments.
# MemorySettings also supports loading from environment variables or .env files
# using the NAM_ prefix (e.g. NAM_NEO4J__URI, NAM_EMBEDDING__MODEL).
settings = MemorySettings(
    neo4j={
        "uri": os.environ["NEO4J_URI"],
        "username": os.environ.get("NEO4J_USERNAME", "neo4j"),
        "password": SecretStr(os.environ["NEO4J_PASSWORD"]),
    },
    embedding={
        "provider": "openai",
        "model": "text-embedding-3-small",
    },
)

memory_client = MemoryClient(settings)

async with memory_client:
    memory = Neo4jMicrosoftMemory.from_memory_client(
        memory_client=memory_client,
        session_id="user-123",
    )
    tools = create_memory_tools(memory)

    async with (
        AzureCliCredential() as credential,
        Agent(
            client=FoundryChatClient(
                credential=credential,
                project_endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"],
                model=os.environ["FOUNDRY_MODEL"],
            ),
            instructions="You are a helpful assistant with persistent memory.",
            tools=tools,
            context_providers=[memory.context_provider],
        ) as agent,
    ):
        session = agent.create_session()
        response = await agent.run(
            "Remember that I prefer window seats on flights.", session=session
        )
```

### Key features

- **Bidirectional**: Retrieves relevant context before invocation and saves new memories after responses.
- **Entity extraction**: Builds a knowledge graph from conversations with a multi-stage extraction pipeline.
- **Preference learning**: Infers and stores user preferences across sessions.
- **Memory tools**: Lets agents explicitly search memory, remember preferences, and find entity connections.

### Resources

- [Neo4j Agent Memory repository](https://github.com/neo4j-labs/agent-memory)
- [PyPI package page](https://pypi.org/project/neo4j-agent-memory/)
- [Sample: Retail Assistant with Neo4j Agent Memory](https://github.com/neo4j-labs/agent-memory/tree/main/examples/microsoft_agent_retail_assistant)
- [Workshop: Neo4j Context Providers for Agent Framework](https://github.com/neo4j-partners/maf-context-providers-lab)



