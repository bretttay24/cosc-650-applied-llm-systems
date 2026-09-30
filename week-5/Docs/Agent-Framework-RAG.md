---

title: RAG | Microsoft Learn
Url: https://learn.microsoft.com/en-us/agent-framework/agents/rag
description: Learn how to use Retrieval Augmented Generation (RAG) with Agent Framework
author: westey-m
ms.date: 2026-09-09T00:00:00.0000000Z

---

# RAG | Microsoft Learn

Microsoft Agent Framework supports Retrieval Augmented Generation (RAG) through context providers that add retrieved content before model invocation and search tools that let the model retrieve grounding data on demand.

For conversation/session patterns alongside retrieval, see [Conversations & Memory overview](../concepts/agents/conversations/). For service-specific setup, see [Azure AI Search](../integrations/by-component/context-providers/azure-ai-search), [Microsoft Foundry](../integrations/by-component/context-providers/microsoft-foundry#use-file-search-rag), and [Neo4j](../integrations/by-component/context-providers/neo4j#graphrag-from-an-existing-knowledge-graph).

Agent Framework provides native vector-store contracts and `create_vector_search_tool()`. The helper turns any `SupportsVectorSearch` implementation into a function tool, so the model can retrieve grounding data before it answers.

### Create a native vector search tool

First, define your vector-store model, create a collection, and load its records. The following sample uses `InMemoryCollection` with `OpenAIEmbeddingClient`, but you can supply any native Agent Framework collection that implements `SupportsVectorSearch`. It then exposes optional category and rating filters to the model, maps each result to grounding text, and instructs the agent to search before it answers:

```python
import asyncio
import json
import os
from typing import Annotated, Any, Literal
from urllib.request import urlopen

from agent_framework import (
    Agent,
    Filter,
    FilterGroup,
    InMemoryCollection,
    Param,
    VectorStoreField,
    create_vector_search_tool,
    vectorstoremodel,
)
from agent_framework.openai import OpenAIChatClient, OpenAIEmbeddingClient
from dotenv import load_dotenv


async def main() -> None:
    """Create an in-memory hotel search tool and give it to an agent."""
    api_key = os.environ["OPENAI_API_KEY"]
    collection: InMemoryCollection[str, Hotel] = InMemoryCollection(
        Hotel,
        embedding_generator=OpenAIEmbeddingClient(
            model="text-embedding-3-small",
            api_key=api_key,
        ),
    )
    await collection.ensure_collection_exists()

    # 1. Load the hotel records.
    hotels = await asyncio.to_thread(load_hotels)
    await collection.upsert(hotels)

    # 2. Param values become optional model-visible filter arguments.
    # When the allowed values are known, use Literal so the tool schema exposes
    # them as an enum.
    category = Param(
        "category",
        Literal[
            "Boutique", "Budget", "Extended-Stay", "Luxury", "Resort and Spa", "Suite"
        ],
        description="Only return hotels in this category.",
    )
    min_rating = Param(
        "min_rating",
        float,
        description="The minimum guest rating.",
        minimum=0,
        maximum=5,
    )
    tool = create_vector_search_tool(
        collection,
        description="Search the hotel dataset, optionally filtering by category and minimum rating.",
        filter=FilterGroup(
            "and",
            (
                Filter("category", "eq", category),
                Filter("rating", "gte", min_rating),
            ),
        ),
        result_mapper=lambda result: (
            f"(hotel_id: {result['record'].hotel_id}) {result['record'].hotel_name} "
            f"(rating {result['record'].rating}) - {result['record'].description}. "
            f"Address: {result['record'].address.city}, {result['record'].address.country}."
        ),
    )

    # 3. The agent chooses whether to supply the exposed category and minimum-rating filters.
    async with Agent(
        client=OpenAIChatClient(
            model="gpt-5.4-nano",
            api_key=api_key,
        ),
        name="HotelAgent",
        instructions=(
            "Always use the search tool to answer hotel questions. "
            "Use category and minimum rating filters when the request provides them. "
            "Include the hotel_id in the answer."
        ),
        tools=[tool],
    ) as agent:
        result = await agent.run("Find a resort and spa with a rating of at least 4.")
        print(result)
```

The full sample defines the `Hotel` model and loads the source records before the shown collection setup. Set `OPENAI_API_KEY` before you run it.

### Customize search behavior

Configure `create_vector_search_tool()` with the following options:

| Option | Purpose |
| --- | --- |
| `name` | Sets the function name exposed to the model. Use a unique name when you add multiple search tools. |
| `description` | Explains when and why the model should use the tool. |
| `approval_mode` | Sets tool approval to `always_require` or `never_require`. |
| `search_type` | Selects `vector` or `keyword_hybrid` search. The collection must support the selected mode. |
| `top` and `skip` | Set fixed paging values or use typed `Param` values that the model supplies. |
| `filter` | Applies a portable `Filter` or `FilterGroup`. A filter can contain typed `Param` values exposed in the tool schema. |
| `result_mapper` | Converts each `SearchResponse` into text or multimodal `Content` for the model. |

The generated tool always includes a `query` string. Any `Param` values in the filter, `top`, or `skip` settings become additional validated tool arguments. Use `Literal` and numeric constraints to keep model-supplied values within the range your application accepts.

You can create multiple tools for different collections or search modes. Give each tool a distinct `name` and `description` so the model can select the appropriate knowledge source.

### Choose a native vector store

Native Python implementations are available for in-memory search, Azure AI Search, PostgreSQL with pgvector, Qdrant, and Redis. Their search modes, package lifecycle, installation commands, and limitations differ. See [Vector store integrations](../integrations/by-component/vector-stores/) to select and configure an implementation. That page also identifies databases that currently have only a separate Semantic Kernel connector.

## Graph RAG

For GraphRAG using graph traversal enriched search with Cypher queries, see the [Neo4j GraphRAG Provider](../integrations/by-component/context-providers/neo4j#graphrag-from-an-existing-knowledge-graph).