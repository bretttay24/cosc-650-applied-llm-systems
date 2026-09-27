---

title: Microsoft Agent Framework Overview | Microsoft Learn
Url: https://learn.microsoft.com/en-us/agent-framework/overview/
description: Build AI agents and multi-agent workflows in .NET, Python, and Go with Microsoft Agent Framework.
author: moonbox3
ms.date: 2026-07-29T00:00:00.0000000Z

---

# Microsoft Agent Framework Overview | Microsoft Learn

Agent Framework brings together four primary areas:

| - | Description |
| --- | --- |
| **[Agents](../concepts/agents/)** | Individual agents that use LLMs to process inputs, call [tools](../agents/tools/) and [MCP servers](../agents/tools/hosted-mcp-tools), and generate responses. Supports Microsoft Foundry, Anthropic, Azure OpenAI, OpenAI, Ollama, and [more](../integrations/by-component/model-providers/). |
| **[Harness Agent](../concepts/harness)** | An opinionated agent with batteries-included capabilities for long, multi-step tasks — planning and todo tracking, context compaction, file access and memory, don't-ask-again tool approval, and observability. |
| **[Workflows](../concepts/workflows/)** | Functional and graph-based workflows that connect agents and functions through explicit execution paths. |
| **[Integrations](../integrations/)** | Connections to model providers, agent services, tools, context providers, middleware, evaluation services, and UI frameworks, organized by provider and component. |

The framework also provides foundational building blocks, including model clients (chat completions and responses), an agent session for state management, context providers for agent memory, middleware for intercepting agent actions, and MCP clients for tool integration. Together, these components give you the flexibility and power to build interactive, robust, and safe AI applications.

## Get started

```bash
pip install agent-framework
```

```python
from agent_framework import Agent
from agent_framework.foundry import FoundryChatClient
from azure.identity import AzureCliCredential

agent = Agent(
    client=FoundryChatClient(
        project_endpoint="https://your-foundry-service.services.ai.azure.com/api/projects/your-foundry-project",
        model="gpt-5.4-mini",
        credential=AzureCliCredential(),
    ),
    name="HelloAgent",
    instructions="You are a friendly assistant. Keep your answers brief.",
)
```

```python
# Non-streaming: get the complete response at once
result = await agent.run("What is the largest city in France?")
print(f"Agent: {result}")
```

That's it — an agent that calls an LLM and returns a response. From here you can [add tools](../agents/tools/), [multi-turn conversations](../concepts/agents/conversations/session), [middleware](../concepts/agents/middleware/), and workflows to build production applications.


Note
Agent Framework does **not** automatically load `.env` files. To use a `.env` file, call `load_dotenv()` at the start of your application, or set environment variables directly in your shell or IDE.


## When to use agents vs workflows

| Use an agent when… | Use a workflow when… |
| --- | --- |
| The task is open-ended or conversational | The process has well-defined steps |
| You need autonomous tool use and planning | You need explicit control over execution order |
| A single LLM call (possibly with tools) suffices | Multiple agents or functions must coordinate |

*If you can write a function to handle the task, do that instead of using an AI agent.*

## Why Agent Framework?

Agent Framework combines AutoGen's simple agent abstractions with Semantic Kernel's enterprise features — session-based state management, type safety, middleware, telemetry — and adds graph-based workflows for explicit multi-agent orchestration.

[Semantic Kernel](https://github.com/microsoft/semantic-kernel) and [AutoGen](https://github.com/microsoft/autogen) pioneered the concepts of AI agents and multi-agent orchestration. The Agent Framework is the direct successor, created by the same teams. It combines AutoGen's simple abstractions for single- and multi-agent patterns with Semantic Kernel's enterprise-grade features such as session-based state management, type safety, filters, telemetry, and extensive model and embedding support. Beyond merging the two, Agent Framework introduces workflows that give developers explicit control over multi-agent execution paths, plus a robust state management system for long-running and human-in-the-loop scenarios. In short, Agent Framework is the next generation of both Semantic Kernel and AutoGen.

To learn more about migrating from either Semantic Kernel or AutoGen, see the [Migration Guide from Semantic Kernel](../migration-guide/from-semantic-kernel/) and [Migration Guide from AutoGen](../migration-guide/from-autogen/).

Both Semantic Kernel and AutoGen have benefited significantly from the open-source community, and the same is expected for Agent Framework. Microsoft Agent Framework welcomes contributions and will keep improving with new features and capabilities.

Important

If you use Microsoft Agent Framework to build applications that operate with any third-party servers, agents, code, or non-Azure Direct models ("Third-Party Systems"), you do so at your own risk. Third-Party Systems are Non-Microsoft Products under the Microsoft Product Terms and are governed by their own third-party license terms. You are responsible for any usage and associated costs.

We recommend reviewing all data being shared with and received from Third-Party Systems and being cognizant of third-party practices for handling, sharing, retention and location of data. It is your responsibility to manage whether your data will flow outside of your organization's Azure compliance and geographic boundaries and any related implications, and that appropriate permissions, boundaries and approvals are provisioned.

You are responsible for carefully reviewing and testing applications you build using Microsoft Agent Framework in the context of your specific use cases, and making all appropriate decisions and customizations. This includes implementing your own responsible AI mitigations such as metaprompt, content filters, or other safety systems, and ensuring your applications meet appropriate quality, reliability, security, and trustworthiness standards. See also: [Transparency FAQ](https://github.com/microsoft/agent-framework/blob/main/TRANSPARENCY_FAQS.md)