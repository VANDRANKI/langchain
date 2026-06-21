"""Custom exceptions for LangChain.

Exception hierarchy
-------------------
:class:`LangChainException`
    Base class for all LangChain exceptions.

    - :class:`TracerException` -- errors raised inside tracer/callback code.
    - :class:`OutputParserException` -- parsing failures from output parsers.
    - :class:`ContextOverflowError` -- input exceeds the model context window.

:class:`ErrorCode`
    An enumeration of machine-readable error codes embedded in exception
    messages to link users to targeted troubleshooting documentation.
"""

from enum import Enum
from typing import Any


class LangChainException(Exception):  # noqa: N818
    """Base class for all LangChain-specific exceptions.

    Catch this class to handle any error originating from LangChain without
    needing to enumerate every concrete subclass.  For more targeted handling,
    catch one of the specialised subclasses instead.
    """


class TracerException(LangChainException):
    """Base class for errors raised inside the tracing and callback subsystem."""


class OutputParserException(ValueError, LangChainException):  # noqa: N818
    """Raised by output parsers when they cannot parse the model's response.

    This exception exists to distinguish *parsing* failures from other
    runtime errors that might surface inside an output parser (e.g. network
    errors, import errors).  Callers—particularly agent executors—can catch
    :class:`OutputParserException` specifically and decide whether to retry,
    pass the error back to the model for self-correction, or propagate it.

    When *send_to_llm* is ``True``, the exception carries both the raw model
    output that could not be parsed (*llm_output*) and a human-readable
    explanation (*observation*) that an agent can include in a follow-up
    prompt to request a corrected response.
    """

    def __init__(
        self,
        error: Any,
        observation: str | None = None,
        llm_output: str | None = None,
        send_to_llm: bool = False,  # noqa: FBT001,FBT002
    ):
        """Create an OutputParserException.

        Args:
            error: The error being raised.  May be an existing exception
                instance or a plain error-message string.  If a string is
                given, it is automatically augmented with a link to the
                LangChain troubleshooting documentation.
            observation: A human-readable explanation of the parsing failure,
                intended to be passed back to the model so it can produce a
                corrected output.  Required when *send_to_llm* is ``True``.
            llm_output: The raw string produced by the model that triggered
                the parsing failure.  Required when *send_to_llm* is ``True``.
            send_to_llm: When ``True``, the agent executor will include
                *observation* and *llm_output* in the next prompt to give the
                model an opportunity to correct itself.  Both *observation* and
                *llm_output* must be provided when this flag is ``True``.

        Raises:
            ValueError: If *send_to_llm* is ``True`` but either *observation*
                or *llm_output* is ``None``.
        """
        if isinstance(error, str):
            error = create_message(
                message=error, error_code=ErrorCode.OUTPUT_PARSING_FAILURE
            )

        super().__init__(error)
        if send_to_llm and (observation is None or llm_output is None):
            msg = (
                "Arguments 'observation' & 'llm_output'"
                " are required if 'send_to_llm' is True"
            )
            raise ValueError(msg)
        self.observation = observation
        self.llm_output = llm_output
        self.send_to_llm = send_to_llm


class ContextOverflowError(LangChainException):
    """Raised when the input exceeds the model's maximum context window.

    Chat model wrappers raise this error when the tokenised input is longer
    than the context limit supported by the underlying model.  Callers can
    catch this exception to truncate the input, switch to a model with a
    larger context window, or surface an appropriate error to the end user.
    """


class ErrorCode(Enum):
    """Machine-readable error codes embedded in LangChain exception messages.

    Each code corresponds to a dedicated troubleshooting page in the
    LangChain documentation.  The URL is constructed by
    :func:`create_message`.
    """

    INVALID_PROMPT_INPUT = "INVALID_PROMPT_INPUT"
    INVALID_TOOL_RESULTS = "INVALID_TOOL_RESULTS"  # Used in JS; not Py (yet)
    MESSAGE_COERCION_FAILURE = "MESSAGE_COERCION_FAILURE"
    MODEL_AUTHENTICATION = "MODEL_AUTHENTICATION"  # Used in JS; not Py (yet)
    MODEL_NOT_FOUND = "MODEL_NOT_FOUND"  # Used in JS; not Py (yet)
    MODEL_RATE_LIMIT = "MODEL_RATE_LIMIT"  # Used in JS; not Py (yet)
    OUTPUT_PARSING_FAILURE = "OUTPUT_PARSING_FAILURE"


def create_message(*, message: str, error_code: ErrorCode) -> str:
    """Build an exception message that includes a troubleshooting link.

    Appends a URL pointing to the LangChain documentation page for the given
    *error_code* so that users can quickly find guidance on how to resolve
    the error.

    Args:
        message: The primary error description.
        error_code: The :class:`ErrorCode` value that identifies the
            troubleshooting page to link to.

    Returns:
        A multi-line string that combines *message* with the troubleshooting
        URL on a new line.

    Example:
        ```python
        create_message(
            message="Failed to parse output",
            error_code=ErrorCode.OUTPUT_PARSING_FAILURE,
        )
        # "Failed to parse output\nFor troubleshooting, visit: ..."
        ```
    """
    return (
        f"{message}\n"
        "For troubleshooting, visit: https://docs.langchain.com/oss/python/langchain"
        f"/errors/{error_code.value}"
    )
