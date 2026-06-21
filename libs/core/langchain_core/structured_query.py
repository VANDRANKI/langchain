"""Internal representation of a structured query language.

This module defines the abstract syntax tree (AST) used to represent
structured filter queries that can be translated into native query
expressions for various vector store backends.

The design follows the Visitor pattern: :class:`Expr` nodes form the AST,
and :class:`Visitor` implementations translate those nodes into
backend-specific query objects (e.g., Pinecone filters, Chroma metadata
filters, Weaviate ``where`` clauses).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel

if TYPE_CHECKING:
    from collections.abc import Sequence


class Visitor(ABC):
    """Abstract base for translating a structured query AST into a backend query.

    Subclasses implement one visit method per concrete :class:`Expr` node type.
    Before dispatching, :meth:`_validate_func` checks that the operator or
    comparator being used is in the set allowed by this visitor; if not, a
    :exc:`ValueError` is raised so that unsupported query constructs surface
    early with a clear message.

    Attributes:
        allowed_comparators: When set, only these :class:`Comparator` values
            are accepted.  ``None`` means all comparators are allowed.
        allowed_operators: When set, only these :class:`Operator` values are
            accepted.  ``None`` means all operators are allowed.
    """

    allowed_comparators: Sequence[Comparator] | None = None
    """Allowed comparators for the visitor."""

    allowed_operators: Sequence[Operator] | None = None
    """Allowed operators for the visitor."""

    def _validate_func(self, func: Operator | Comparator) -> None:
        """Validate that an operator or comparator is permitted by this visitor.

        Raises :exc:`ValueError` if ``func`` is an :class:`Operator` that is
        not in :attr:`allowed_operators`, or a :class:`Comparator` that is not
        in :attr:`allowed_comparators`.  When the corresponding allow-list is
        ``None`` the function is accepted unconditionally.

        Args:
            func: The operator or comparator to validate.

        Raises:
            ValueError: If ``func`` is not in the allow-list for its type.
        """
        if (
            isinstance(func, Operator)
            and self.allowed_operators is not None
            and func not in self.allowed_operators
        ):
            msg = (
                f"Received disallowed operator {func}. Allowed "
                f"comparators are {self.allowed_operators}"
            )
            raise ValueError(msg)
        if (
            isinstance(func, Comparator)
            and self.allowed_comparators is not None
            and func not in self.allowed_comparators
        ):
            msg = (
                f"Received disallowed comparator {func}. Allowed "
                f"comparators are {self.allowed_comparators}"
            )
            raise ValueError(msg)

    @abstractmethod
    def visit_operation(self, operation: Operation) -> Any:
        """Translate an :class:`Operation` node into a backend query fragment.

        Args:
            operation: The logical operation node to translate.

        Returns:
            A backend-specific query object or fragment.
        """

    @abstractmethod
    def visit_comparison(self, comparison: Comparison) -> Any:
        """Translate a :class:`Comparison` node into a backend query fragment.

        Args:
            comparison: The comparison node to translate.

        Returns:
            A backend-specific query object or fragment.
        """

    @abstractmethod
    def visit_structured_query(self, structured_query: StructuredQuery) -> Any:
        """Translate a top-level :class:`StructuredQuery` into a backend query.

        Args:
            structured_query: The root structured query node to translate.

        Returns:
            A backend-specific query object or a ``(query, kwargs)`` tuple,
            depending on the visitor convention.
        """


def _to_snake_case(name: str) -> str:
    """Convert a ``PascalCase`` class name to ``snake_case``.

    Used internally to derive the ``visit_*`` method name that should be
    called on a :class:`Visitor` for a given :class:`Expr` subclass.

    Args:
        name: A ``PascalCase`` string (typically ``cls.__name__``).

    Returns:
        The ``snake_case`` equivalent of *name*.

    Examples:
        >>> _to_snake_case("StructuredQuery")
        'structured_query'
        >>> _to_snake_case("Operation")
        'operation'
    """
    snake_case = ""
    for i, char in enumerate(name):
        if char.isupper() and i != 0:
            snake_case += "_" + char.lower()
        else:
            snake_case += char.lower()
    return snake_case


class Expr(BaseModel):
    """Base class for all AST expression nodes.

    Every concrete expression type (e.g. :class:`Comparison`,
    :class:`Operation`, :class:`StructuredQuery`) extends this class and
    gains the :meth:`accept` method for double-dispatch via the Visitor
    pattern.
    """

    def accept(self, visitor: Visitor) -> Any:
        """Dispatch this node to the matching ``visit_*`` method on *visitor*.

        The method name is derived by converting this instance's class name
        from ``PascalCase`` to ``snake_case`` and prepending ``visit_``.
        For example, a :class:`StructuredQuery` node calls
        ``visitor.visit_structured_query(self)``.

        Args:
            visitor: The visitor that should process this node.

        Returns:
            Whatever the corresponding ``visit_*`` method on *visitor* returns.
        """
        return getattr(visitor, f"visit_{_to_snake_case(self.__class__.__name__)}")(
            self
        )


class Operator(str, Enum):
    """Logical operators for combining filter directives."""

    AND = "and"
    OR = "or"
    NOT = "not"


class Comparator(str, Enum):
    """Comparison operators for attribute-value comparisons."""

    EQ = "eq"
    NE = "ne"
    GT = "gt"
    GTE = "gte"
    LT = "lt"
    LTE = "lte"
    CONTAIN = "contain"
    LIKE = "like"
    IN = "in"
    NIN = "nin"


class FilterDirective(Expr, ABC):
    """Abstract base for all filtering expression nodes.

    Concrete subclasses are :class:`Comparison` (leaf nodes that compare a
    single attribute to a value) and :class:`Operation` (internal nodes that
    combine other :class:`FilterDirective` nodes with a logical operator).
    """


class Comparison(FilterDirective):
    """A leaf filter node that compares a document attribute to a value.

    Attributes:
        comparator: The comparison operator to apply.
        attribute: The name of the document attribute to compare.
        value: The value to compare the attribute against.
    """

    comparator: Comparator
    """The comparator to use."""

    attribute: str
    """The attribute to compare."""

    value: Any
    """The value to compare to."""

    def __init__(
        self, comparator: Comparator, attribute: str, value: Any, **kwargs: Any
    ) -> None:
        """Create a Comparison filter node.

        Args:
            comparator: The comparison operator (e.g. ``Comparator.EQ``).
            attribute: The document attribute name to compare.
            value: The value to compare the attribute against.
            **kwargs: Additional keyword arguments forwarded to Pydantic's
                ``BaseModel.__init__``.
        """
        super().__init__(
            comparator=comparator, attribute=attribute, value=value, **kwargs
        )


class Operation(FilterDirective):
    """An internal filter node that applies a logical operator to sub-filters.

    Attributes:
        operator: The logical operator to apply (``AND``, ``OR``, or ``NOT``).
        arguments: The :class:`FilterDirective` nodes to combine.
    """

    operator: Operator
    """The operator to use."""

    arguments: list[FilterDirective]
    """The arguments to the operator."""

    def __init__(
        self, operator: Operator, arguments: list[FilterDirective], **kwargs: Any
    ) -> None:
        """Create an Operation filter node.

        Args:
            operator: The logical operator to apply.
            arguments: The child filter directives to combine.
            **kwargs: Additional keyword arguments forwarded to Pydantic's
                ``BaseModel.__init__``.
        """
        super().__init__(operator=operator, arguments=arguments, **kwargs)


class StructuredQuery(Expr):
    """The root node of a structured query AST.

    Encapsulates a free-text query string together with an optional metadata
    filter expression and an optional result-count limit.

    Attributes:
        query: The natural-language (or keyword) query string.
        filter: An optional :class:`FilterDirective` subtree that restricts
            which documents are eligible.
        limit: An optional maximum number of results to return.
    """

    query: str
    """Query string."""

    filter: FilterDirective | None
    """Filtering expression."""

    limit: int | None
    """Limit on the number of results."""

    def __init__(
        self,
        query: str,
        filter: FilterDirective | None,  # noqa: A002
        limit: int | None = None,
        **kwargs: Any,
    ) -> None:
        """Create a StructuredQuery.

        Args:
            query: The free-text query string.
            filter: An optional filter expression that restricts candidate
                documents.  Pass ``None`` to apply no metadata filter.
            limit: Maximum number of documents to return.  ``None`` means no
                limit is imposed at the structured-query level (the backend may
                still apply its own default).
            **kwargs: Additional keyword arguments forwarded to Pydantic's
                ``BaseModel.__init__``.
        """
        super().__init__(query=query, filter=filter, limit=limit, **kwargs)
