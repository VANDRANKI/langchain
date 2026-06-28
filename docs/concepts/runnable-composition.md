# Runnable Composition Patterns

LangChain Expression Language (LCEL) lets you build pipelines by composing
`Runnable` objects with the `|` operator. This guide covers the key patterns
and common pitfalls.

## The Pipe Operator

Any two `Runnable` objects can be piped together:

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser

prompt = ChatPromptTemplate.from_template("Tell me a joke about {topic}.")
model = ChatOpenAI(model="gpt-4.1")
parser = StrOutputParser()

# Build the chain — no calls are made yet
chain = prompt | model | parser

# Invoke
result: str = chain.invoke({"topic": "programmers"})
```

The `|` operator is equivalent to `RunnableSequence([prompt, model, parser])`.

## Branching with RunnableParallel

Run multiple branches in parallel and collect their results into a dict:

```python
from langchain_core.runnables import RunnableParallel

analysis_chain = RunnableParallel(
    sentiment=sentiment_chain,
    summary=summary_chain,
    keywords=keyword_chain,
)

# All three branches run concurrently
result = analysis_chain.invoke({"text": long_article})
# result == {"sentiment": ..., "summary": ..., "keywords": ...}
```

## Conditional Branching with RunnableBranch

```python
from langchain_core.runnables import RunnableBranch, RunnableLambda

router = RunnableBranch(
    (lambda x: x["language"] == "python", python_chain),
    (lambda x: x["language"] == "javascript", js_chain),
    default_chain,  # fallback
)
```

## Passing Through Fields with RunnablePassthrough

Keep upstream context alongside model output:

```python
from langchain_core.runnables import RunnablePassthrough

rag_chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt
    | model
    | parser
)
```

## Configurable Runnables

Make a chain configurable at call time without rebuilding it:

```python
from langchain_core.runnables import ConfigurableField

model = ChatOpenAI(model="gpt-4.1").configurable_fields(
    temperature=ConfigurableField(
        id="temperature",
        name="Temperature",
        description="Sampling temperature (0–2).",
    )
)

# Use the default temperature
chain = prompt | model | parser

# Override temperature at call time
result = chain.invoke(
    {"topic": "cats"},
    config={"configurable": {"temperature": 0.9}},
)
```

## Streaming

Every `Runnable` supports `.stream()` and `.astream()`. Parsers must
implement `transform` / `atransform` to propagate chunks:

```python
for chunk in chain.stream({"topic": "space"}):
    print(chunk, end="", flush=True)
```

For async streaming:

```python
async for chunk in chain.astream({"topic": "space"}):
    print(chunk, end="", flush=True)
```

## Retry and Fallback

```python
from langchain_core.runnables import RunnableWithFallbacks

robust_model = (
    ChatOpenAI(model="gpt-4.1")
    .with_retry(stop_after_attempt=3)
    .with_fallbacks([ChatOpenAI(model="gpt-4.1-mini")])
)
```

## Type Safety Tips

- Chain input type = first runnable's input type.
- Chain output type = last runnable's output type.
- Use `chain.input_schema` and `chain.output_schema` to inspect at runtime.
- `RunnableLambda` wraps any callable — annotate the function for IDE support:

```python
from langchain_core.runnables import RunnableLambda

def extract_query(state: dict) -> str:
    """Pull the user query string from the pipeline state dict."""
    return state["messages"][-1].content

extractor = RunnableLambda(extract_query)
```

## Common Pitfalls

| Pitfall | Symptom | Fix |
|---------|---------|-----|
| Calling `.invoke()` on an unbuilt chain | `AttributeError` | Make sure you used `|` before calling |
| Wrong input dict keys | `KeyError` in the prompt | Inspect `chain.input_schema.schema()` |
| Streaming a non-streaming parser | Chunks arrive as full strings | Implement `transform` on your parser |
| Config not propagated | Callbacks not firing | Pass `config=` to every `.invoke()` call |
