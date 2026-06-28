# Testing LCEL Chains

This guide explains how to write reliable unit and integration tests for
LangChain Expression Language (LCEL) chains without making real API calls.

## 1. Fake LLMs for unit tests

Use `FakeListChatModel` or `FakeChatModel` to produce deterministic outputs.

```python
from langchain_core.language_models.fake import FakeListChatModel
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

def build_chain(llm):
    prompt = ChatPromptTemplate.from_template("Answer: {question}")
    return prompt | llm | StrOutputParser()

def test_chain_output():
    fake_llm = FakeListChatModel(responses=["42"])
    chain = build_chain(fake_llm)
    result = chain.invoke({"question": "What is 6 * 7?"})
    assert result == "42"
```

## 2. Testing streaming output

```python
def test_chain_streaming():
    fake_llm = FakeListChatModel(responses=["Hello world"])
    chain = build_chain(fake_llm)
    chunks = list(chain.stream({"question": "Say hello"}))
    assert "".join(chunks) == "Hello world"
```

## 3. Testing RunnableParallel branches

```python
from langchain_core.runnables import RunnableParallel, RunnableLambda

def test_parallel_branch():
    double = RunnableLambda(lambda x: x * 2)
    triple = RunnableLambda(lambda x: x * 3)
    parallel = RunnableParallel(doubled=double, tripled=triple)
    result = parallel.invoke(5)
    assert result == {"doubled": 10, "tripled": 15}
```

## 4. Testing fallback chains

```python
def test_fallback_invoked_on_error():
    from langchain_core.runnables import RunnableLambda

    def always_fails(x):
        raise ValueError("primary failed")

    primary = RunnableLambda(always_fails)
    fallback = RunnableLambda(lambda x: "fallback result")
    chain = primary.with_fallbacks([fallback])
    result = chain.invoke("input")
    assert result == "fallback result"
```

## 5. Testing async chains

```python
import asyncio

async def test_async_chain():
    fake_llm = FakeListChatModel(responses=["async answer"])
    chain = build_chain(fake_llm)
    result = await chain.ainvoke({"question": "test"})
    assert result == "async answer"

def test_async_chain_wrapper():
    asyncio.run(test_async_chain())
```

## 6. Asserting on intermediate values with callbacks

```python
from langchain_core.callbacks import BaseCallbackHandler

class CapturingHandler(BaseCallbackHandler):
    def __init__(self):
        self.llm_inputs = []

    def on_llm_start(self, serialized, prompts, **kwargs):
        self.llm_inputs.extend(prompts)

def test_prompt_content():
    handler = CapturingHandler()
    fake_llm = FakeListChatModel(responses=["ok"])
    chain = build_chain(fake_llm)
    chain.invoke({"question": "ping"}, config={"callbacks": [handler]})
    assert any("ping" in p for p in handler.llm_inputs)
```

## Common pitfalls

| Pitfall | Fix |
|---|---|
| Real API calls in unit tests | Use `FakeListChatModel` |
| Non-deterministic LLM output | Always stub in tests |
| Testing only `invoke`, not `stream` | Add streaming variant |
| Missing `ainvoke` test for async chains | Test both sync and async |
