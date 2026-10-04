---

title: Azure AI Search | Microsoft Learn
Url: https://learn.microsoft.com/en-us/agent-framework/integrations/by-component/context-providers/azure-ai-search
description: Ground Agent Framework agents with documents retrieved from Azure AI Search.
author: eavanvalkenburg
ms.date: 2026-08-31T00:00:00.0000000Z

---

# Azure AI Search | Microsoft Learn

Azure AI Search grounds Agent Framework agents with content from a search index. In Python, `AzureAISearchContextProvider` supports semantic and agentic retrieval. In .NET, connect an Azure AI Search client to `TextSearchProvider`.

This integration uses the RAG pattern: it retrieves relevant external content before model invocation without treating that content as conversational memory.

## Install the packages

```bash
pip install agent-framework-azure-ai-search agent-framework-foundry --pre
```

## Use semantic retrieval

Semantic mode performs search against an existing index and can combine keyword and vector retrieval.

```python
credential = AzureCliCredential()

# Get configuration from environment
search_endpoint = os.environ["AZURE_SEARCH_ENDPOINT"]
search_key = os.environ.get("AZURE_SEARCH_API_KEY")
index_name = os.environ["AZURE_SEARCH_INDEX_NAME"]
project_endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
model_deployment = os.environ.get("FOUNDRY_MODEL", "gpt-4o")
openai_endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
embedding_deployment = os.environ.get("AZURE_OPENAI_EMBEDDING_MODEL")

embedding_client = None
if openai_endpoint and embedding_deployment:
    embedding_client = OpenAIEmbeddingClient(
        azure_endpoint=openai_endpoint,
        model=embedding_deployment,
        credential=credential,
    )

# Create Azure AI Search context provider with semantic mode (recommended, fast)
print("Using SEMANTIC mode (hybrid search + semantic ranking, fast)\n")
search_provider = AzureAISearchContextProvider(
    source_id="search_provider",
    endpoint=search_endpoint,
    index_name=index_name,
    api_key=search_key,  # Use api_key for API key auth, or credential for managed identity
    credential=credential if not search_key else None,
    mode="semantic",  # Default mode
    top_k=3,  # Retrieve top 3 most relevant documents
    embedding_function=embedding_client,  # Provide embedding function for hybrid search
    vector_field_name="DescriptionVector"
    if embedding_client
    else None,  # Set vector field for hybrid search if using embeddings
)

# Create agent with search context provider
async with (
    search_provider,
    Agent(
        client=FoundryChatClient(
            project_endpoint=project_endpoint,
            model=model_deployment,
            credential=credential,
        ),
        name="SearchAgent",
        instructions=(
            "You are a helpful assistant. Use the provided context from the "
            "knowledge base to answer questions accurately."
        ),
        context_providers=[search_provider],
    ) as agent,
):
    print("=== Azure AI Agent with Search Context (Semantic Mode) ===\n")

    for user_input in USER_INPUTS:
        print(f"User: {user_input}")
        print("Agent: ", end="", flush=True)

        # Stream response
        async for chunk in agent.run(user_input, stream=True):
            if chunk.text:
                print(chunk.text, end="", flush=True)

        print("\n")
```

## Use agentic retrieval

Agentic mode uses an Azure AI Search Knowledge Base for query planning and multi-hop retrieval.

```python
# Agentic mode requires exactly ONE of: knowledge_base_name OR index_name
# Option 1: Use existing Knowledge Base (recommended)
knowledge_base_name = os.environ.get("AZURE_SEARCH_KNOWLEDGE_BASE_NAME")
# Option 2: Auto-create KB from index (requires azure_openai_resource_url)
index_name = os.environ.get("AZURE_SEARCH_INDEX_NAME")
azure_openai_resource_url = os.environ.get("AZURE_OPENAI_RESOURCE_URL")

# Create Azure AI Search context provider with agentic mode (recommended for accuracy)
print("Using AGENTIC mode (Knowledge Bases with query planning, recommended)\n")
print("This mode is slightly slower but provides more accurate results.\n")

# Configure based on whether using existing KB or auto-creating from index
if knowledge_base_name:
    # Use existing Knowledge Base - simplest approach
    search_provider = AzureAISearchContextProvider(
        source_id="search_provider",
        endpoint=search_endpoint,
        api_key=search_key,
        credential=AzureCliCredential() if not search_key else None,
        mode="agentic",
        knowledge_base_name=knowledge_base_name,
        # Optional: Configure retrieval behavior. "answer_synthesis" output mode and
        # "medium"/"low" reasoning effort require the preview build of azure-search-documents
        # (`pip install --pre azure-search-documents`); the provider auto-detects the build.
        knowledge_base_output_mode="extractive_data",  # or "answer_synthesis" (preview build only)
        retrieval_reasoning_effort="minimal",  # or "medium", "low" (preview build only)
    )
else:
    # Auto-create Knowledge Base from index
    if not index_name:
        raise ValueError(
            "Set AZURE_SEARCH_KNOWLEDGE_BASE_NAME or AZURE_SEARCH_INDEX_NAME"
        )
    if not azure_openai_resource_url:
        raise ValueError("AZURE_OPENAI_RESOURCE_URL required when using index_name")
    search_provider = AzureAISearchContextProvider(
        source_id="search_provider",
        endpoint=search_endpoint,
        index_name=index_name,
        api_key=search_key,
        credential=AzureCliCredential() if not search_key else None,
        mode="agentic",
        azure_openai_resource_url=azure_openai_resource_url,
        model=model_deployment,
        # Optional: Configure retrieval behavior. "answer_synthesis" output mode and
        # "medium"/"low" reasoning effort require the preview build of azure-search-documents
        # (`pip install --pre azure-search-documents`); the provider auto-detects the build.
        knowledge_base_output_mode="extractive_data",  # or "answer_synthesis" (preview build only)
        retrieval_reasoning_effort="minimal",  # or "medium", "low" (preview build only)
        top_k=3,
    )

# Create agent with search context provider
async with (
    search_provider,
    Agent(
        client=FoundryChatClient(
            project_endpoint=project_endpoint,
            model=model_deployment,
            credential=AzureCliCredential(),
        ),
        name="SearchAgent",
        instructions=(
            "You are a helpful assistant with advanced reasoning capabilities. "
            "Use the provided context from the knowledge base to answer complex "
            "questions that may require synthesizing information from multiple sources."
        ),
        context_providers=[search_provider],
    ) as agent,
):
    print("=== Azure AI Agent with Search Context (Agentic Mode) ===\n")

    for user_input in USER_INPUTS:
        print(f"User: {user_input}")
        print("Agent: ", end="", flush=True)

        # Stream response
        async for chunk in agent.run(user_input, stream=True):
            if chunk.text:
                print(chunk.text, end="", flush=True)
            for content in chunk.contents:
                if content.annotations:
                    print(f"\n[Sources: {content.annotations}]", end="", flush=True)

        print("\n")
```

Some agentic output and reasoning options require the preview `azure-search-documents` package.

### Forward caller identity for permission-aware retrieval

Set `query_source_credential=caller_credential` when a knowledge source uses [document-level permissions](/en-us/azure/search/search-query-access-control-rbac-enforcement) and retrieval results must be security trimmed for each caller. Pass the signed-in caller's sync or async Azure token credential separately from the application credential that connects to Azure AI Search.

For each agentic retrieval, the provider requests a token for `https://search.azure.com/.default`. It forwards the caller's Microsoft Entra identity in the `x-ms-query-source-authorization` header so Azure AI Search can enforce the indexed permissions.

This option requires a preview `azure-search-documents` build, version `12.1.0b1` or later within the supported 12.x range:

```bash
pip install --pre "azure-search-documents>=12.1.0b1,<13"
```

Agent Framework fails closed if the installed SDK doesn't support query-source authorization. It raises a `ValueError` before sending a retrieval request. Token acquisition failures also stop retrieval; the provider doesn't retry without the caller's identity.


## Production considerations

- Prefer Microsoft Entra authentication or managed identity over search keys.
- Apply tenant-aware filters and index isolation.
- Treat retrieved content as untrusted input and mitigate indirect prompt injection.
- Preserve source metadata when the agent should cite documents.