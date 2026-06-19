"""Chat loaders — base class for loading historical conversation data."""

from abc import ABC, abstractmethod
from collections.abc import Iterator
from typing import final

from langchain_core.chat_sessions import ChatSession


class BaseChatLoader(ABC):
    """Abstract base class for chat loaders.

    Chat loaders are responsible for reading conversation history from an
    external source (e.g. a file, a database, or an API) and exposing it
    as a sequence of :class:`~langchain_core.chat_sessions.ChatSession`
    objects that can be used for fine-tuning or evaluation.

    Sub-classes **must** implement :meth:`lazy_load`.  The default
    :meth:`load` implementation eagerly materialises the iterator into a
    list, which is convenient for small datasets but may exhaust memory for
    large ones — override it when streaming is required.

    Example:
        .. code-block:: python

            class MyLoader(BaseChatLoader):
                def lazy_load(self) -> Iterator[ChatSession]:
                    for raw in fetch_raw_sessions():
                        yield parse_session(raw)

            sessions = MyLoader().load()
    """

    @abstractmethod
    def lazy_load(self) -> Iterator[ChatSession]:
        """Lazily yield chat sessions one at a time.

        Implementations should yield one :class:`ChatSession` per logical
        conversation.  Using a generator keeps memory consumption low when
        the underlying data source is large.

        Yields:
            ChatSession: The next conversation in the source.
        """

    def load(self) -> list[ChatSession]:
        """Eagerly load all chat sessions into memory.

        Calls :meth:`lazy_load` and collects the results into a list.  Use
        this method when the full dataset fits comfortably in memory and
        you need random access to individual sessions.

        Returns:
            A list of all :class:`ChatSession` objects produced by the
            loader.  The list may be empty if no sessions are available.
        """
        return list(self.lazy_load())
