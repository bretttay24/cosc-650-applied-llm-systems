---

title: Microsoft Foundry evaluation | Microsoft Learn
Url: https://learn.microsoft.com/en-us/agent-framework/integrations/by-component/evaluation/microsoft-foundry
description: Evaluate Agent Framework agents, workflows, traces, and responses with Microsoft Foundry.
author: eavanvalkenburg
ms.date: 2026-07-28T00:00:00.0000000Z

---

# Microsoft Foundry evaluation | Microsoft Learn

`FoundryEvals` connects the Agent Framework evaluation APIs to Microsoft Foundry's managed evaluation service. It provides quality, safety, tool-use, agent-behavior, and rubric evaluators, with stored reports available in the Foundry portal.

For `EvalItem`, local checks, custom evaluators, and conversation split strategies, see [Agent evaluation](../../../agents/evaluation).

## Prerequisites

- A Microsoft Foundry project and model deployment.
- A project-scoped Foundry endpoint.
- Permission to submit evaluations and read reports.

## Evaluate an agent

Pass existing responses or test queries to `evaluate_agent()`. Results include pass/fail counts and the Foundry report URL.

```python
async def main() -> None:
    # 1. Set up the FoundryChatClient
    chat_client = FoundryChatClient(
        project_endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"],
        model=os.environ.get("FOUNDRY_MODEL", "gpt-4o"),
        credential=AzureCliCredential(),
    )

    # 2. Create an agent with tools
    agent = Agent(
        client=chat_client,
        name="travel-assistant",
        instructions=(
            "You are a helpful travel assistant. Use your tools to answer questions about weather and flights."
        ),
        tools=[get_weather, get_flight_price],
    )

    # 3. Create the evaluator — provider config goes here, once
    evals = FoundryEvals(client=chat_client)

    # =========================================================================
    # Pattern 1: evaluate_agent(responses=...) — evaluate a response you already have
    # =========================================================================
    print("=" * 60)
    print("Pattern 1: evaluate_agent(responses=...) — evaluate existing response")
    print("=" * 60)

    query = "How much does a flight from Seattle to Paris cost?"
    response = await agent.run(query)
    print(f"Agent said: {response.text[:100]}...")

    # Pass agent= so tool definitions are extracted, queries= for the eval item context
    results = await evaluate_agent(
        agent=agent,
        responses=response,
        queries=[query],
        evaluators=FoundryEvals(
            client=chat_client,
            evaluators=[FoundryEvals.RELEVANCE, FoundryEvals.TOOL_CALL_ACCURACY],
        ),
    )

    for r in results:
        print(f"Status: {r.status}")
        print(f"Results: {r.passed}/{r.total} passed")
        print(f"Portal: {r.report_url}")
        if r.all_passed:
            print("[PASS] All passed")
        else:
            print(f"[FAIL] {r.failed} failed")
```

Additional samples cover trace evaluation, tool-call evaluation, multi-turn evaluation, workflow evaluation, mixed providers, and custom Foundry rubrics.


## Quality gates

Pin datasets, model deployments, evaluator versions, and rubric versions when results must be comparable across runs. Use result assertion helpers to fail CI when required metrics regress.