"""Cross Encoder interface.

Cross encoders score the relevance between a query and a set of candidate
documents by processing both texts jointly rather than independently. This
joint processing generally produces more accurate relevance scores than
bi-encoder models that embed each text separately.
"""

from abc import ABC, abstractmethod


class BaseCrossEncoder(ABC):
    """Abstract base class for cross encoder models.

    Cross encoders take a pair of texts (typically a query and a candidate
    document) and return a relevance score indicating how well they match.
    Unlike bi-encoders, which encode each text independently and then compare
    embeddings, cross encoders process both texts together. This makes cross
    encoders slower but generally more accurate for ranking tasks.

    Subclasses must implement the :meth:`score` method.

    Example:
        ```python
        from langchain_core.cross_encoders import BaseCrossEncoder


        class MyCrossEncoder(BaseCrossEncoder):
            def score(self, text_pairs: list[tuple[str, str]]) -> list[float]:
                # Call your cross encoder model here
                return [0.9, 0.2]


        encoder = MyCrossEncoder()
        scores = encoder.score(
            [("What is AI?", "Artificial intelligence overview"),
             ("What is AI?", "Banana recipes")]
        )
        # scores -> [0.9, 0.2]
        ```
    """

    @abstractmethod
    def score(self, text_pairs: list[tuple[str, str]]) -> list[float]:
        """Score the relevance of each text pair.

        Each pair consists of a query and a candidate document. The returned
        score reflects how relevant the document is to the query; higher
        values indicate greater relevance. The exact range and scale of the
        scores depend on the underlying model implementation.

        Args:
            text_pairs: A list of ``(query, document)`` string tuples to score.

        Returns:
            A list of relevance scores, one per input pair, in the same order
            as the input.
        """
