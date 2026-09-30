---

title: Azure Cosmos DB | Microsoft Learn
Url: https://learn.microsoft.com/en-us/agent-framework/integrations/by-component/context-providers/azure-cosmos
description: Use Azure Cosmos DB for Agent Framework conversation history and long-term semantic memory.
author: eavanvalkenburg
ms.date: 2026-09-18T00:00:00.0000000Z

---

# Azure Cosmos DB | Microsoft Learn

Azure Cosmos DB supports two distinct context-provider patterns in Agent Framework. Choose the provider based on whether you need an exact transcript or extracted long-term knowledge.

| Pattern | Provider | Behavior |
| --- | --- | --- |
| Conversation history | `CosmosChatHistoryProvider` (.NET) or `CosmosHistoryProvider` (Python) | Persists complete messages so a session can resume after a restart or on another application instance. |
| Long-term memory | `CosmosMemoryContextProvider` (Python) | Extracts facts, procedural knowledge, episodic memories, and summaries, then retrieves relevant memories for later runs. |

## Persist conversation history

### Install the package

```bash
pip install agent-framework-azure-cosmos --pre
```

### Configure `CosmosHistoryProvider`

The Python provider accepts either an Azure credential or an account key. It uses `session_id` as the partition key. Provider instances that use the same account, database, container, nonempty `session_id`, and `source_id` access the same persisted history. The `source_id` filters history within the partition. These identifiers select stored history; they aren't authentication or authorization boundaries. Bind them to authenticated and authorized application context, and use distinct trusted namespaces when you need isolation.

```python
# 1. Create an Azure credential and a CosmosHistoryProvider for agent context
async with (
    AzureCliCredential() as credential,
    CosmosHistoryProvider(
        endpoint=cosmos_endpoint,
        database_name=cosmos_database_name,
        container_name=cosmos_container_name,
        credential=cosmos_key or credential,
    ) as history_provider,
    # 2. Create an agent that uses Cosmos for persisted conversation history.
    Agent(
        client=FoundryChatClient(
            project_endpoint=project_endpoint,
            model=model,
            credential=credential,
        ),
        name="CosmosHistoryAgent",
        instructions="You are a helpful assistant that remembers prior turns.",
        context_providers=[history_provider],
        default_options={"store": False},
    ) as agent,
):
    # 3. Create a session (session_id is used as the partition key).
    session = agent.create_session()

    # 4. Run a multi-turn conversation; history is persisted by CosmosHistoryProvider.
    response1 = await agent.run(
        "My name is Ada and I enjoy distributed systems.", session=session
    )
    print(f"Assistant: {response1.text}")

    response2 = await agent.run("What do you remember about me?", session=session)
    print(f"Assistant: {response2.text}")
    print(f"Container: {history_provider.container_name}")
```

Persist the serialized `AgentSession` in trusted application storage when clients need to recover the same session identifier later.

## Add long-term semantic memory

### Prerequisites

- An Azure Cosmos DB account and database.
- A Microsoft Foundry project with chat and embedding model deployments.
- Azure identity access to both resources.

### Install the packages

```bash
pip install agent-framework-azure-cosmos-memory agent-framework-foundry --pre
```

### Configure the memory provider

The same Foundry project can supply the chat model, embeddings, and memory extraction model. Attach the provider through `context_providers`.

```python
def _build_agent(
    provider: CosmosMemoryContextProvider, credential: DefaultAzureCredential
) -> Agent:
    """Build an agent that uses the memory provider and the same Foundry endpoint for chat."""
    return Agent(
        client=FoundryChatClient(
            project_endpoint=os.environ["FOUNDRY_ENDPOINT"],
            model=os.getenv("CHAT_MODEL", "gpt-4o-mini"),
            credential=credential,
        ),
        name="Memory Assistant",
        instructions="You are a helpful assistant with long-term memory about the user.",
        context_providers=[provider],
    )


async def user_scoped_memory() -> None:
    """Memory scoped to a stable user id, so it persists across sessions and threads."""
    credential = DefaultAzureCredential()
    provider = CosmosMemoryContextProvider(
        cosmos_endpoint=os.environ["COSMOS_ENDPOINT"],
        foundry_endpoint=os.environ["FOUNDRY_ENDPOINT"],
        embedding_model=os.getenv("EMBEDDING_MODEL", "text-embedding-3-large"),
        chat_model=os.getenv("CHAT_MODEL", "gpt-4o-mini"),
        credential=credential,
    )
    agent = _build_agent(provider, credential)

    async with provider:
        session = agent.create_session()
        # Provider state is scoped by source id; set a stable user id there so memory
        # persists across sessions rather than being limited to this one.
        session.state.setdefault(provider.source_id, {})["user_id"] = "alice"
        first = await agent.run(
            "I love hiking and I'm allergic to peanuts.", session=session
        )
        print("Assistant:", first.text)

        # A brand-new session for the same user still recalls the earlier facts.
        new_session = agent.create_session()
        new_session.state.setdefault(provider.source_id, {})["user_id"] = "alice"
        recall = await agent.run("What do you remember about me?", session=new_session)
        print("Assistant:", recall.text)

        # Let background extraction finish and persist before the client closes.
        await provider.flush()
```

A stable `user_id` keeps memory available across sessions and threads. Without one, the provider scopes memory to the current session ID.

### Memory processing

Memory extraction runs in the background after each turn. Use the provider as an async context manager or call `flush()` before shutdown so pending extraction completes before the clients close.

The provider also supports custom extraction prompts, processor cadence, confidence thresholds, memory types, and retrieval limits. Select facts, procedures, and episodes with `memory_types`. With Agent Memory Toolkit 0.3.0b2 or later, facts and selected episodes share the ranked `top_k` result limit. Selected procedures are compiled separately for the current task and don't consume that limit. Older supported Toolkit versions retain their generic retrieval behavior.

## Production considerations

- Derive user, tenant, and session identifiers from authenticated application identity.
- Choose partition keys that distribute traffic while enforcing tenant isolation.
- Keep Cosmos DB and model resources in approved regions and apply least-privilege RBAC.
- Configure time-to-live, backup, retention, and deletion policies for both transcripts and extracted memories.
- Filter or redact sensitive content before persistence, and don't use extracted memories directly for authorization decisions.