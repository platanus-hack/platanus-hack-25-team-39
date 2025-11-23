"""Text processing utilities with LLM using Map pattern.

This module implements a Map pattern for processing large volumes of text
using language models (LLM). It allows parallel text processing during the MAP phase.

Features:
- Parallel processing with configurable concurrency
- In-memory caching for repeated texts (avoids redundant LLM calls)
- Support for Pydantic structured output
"""

import hashlib
import logging
from typing import NamedTuple, TypeVar

from langchain_core.output_parsers import BaseOutputParser, StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable
from langchain_openai import ChatOpenAI
from pydantic import BaseModel

from django.conf import settings

logger = logging.getLogger(__name__)

# Type variable for Pydantic models
T = TypeVar("T", bound=BaseModel)

# In-memory cache for LLM responses: {(prompt_hash, text_hash): result}
_llm_cache: dict[tuple[str, str], str | BaseModel] = {}


def _get_cache_key(prompt_template: str, text: str) -> tuple[str, str]:
    """Generate a cache key from prompt template and text.

    Args:
        prompt_template: The prompt template string
        text: The input text

    Returns:
        Tuple of (prompt_hash, text_hash) for cache lookup
    """
    prompt_hash = hashlib.sha256(prompt_template.encode("utf-8")).hexdigest()[:16]
    text_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]
    return (prompt_hash, text_hash)


def clear_llm_cache() -> int:
    """Clear the LLM response cache.

    Returns:
        Number of entries cleared
    """
    global _llm_cache
    count = len(_llm_cache)
    _llm_cache = {}
    logger.info(f"LLM cache cleared: {count} entries removed")
    return count


class MapResult(NamedTuple):
    """Container for MAP results.

    Attributes:
        map_results: List of results processed in the MAP phase.

    """

    map_results: list[str] | list[BaseModel]


def _get_llm(model: str, temperature: float, api_key: str) -> Runnable:
    """Create and return a default LLM runnable (OpenAI) when none is provided.

    Args:
        model: Name of the OpenAI model to use.
        temperature: Temperature for text generation (0.0-1.0).
        api_key: OpenAI API key.

    Returns:
        Configured ChatOpenAI instance.

    """
    return ChatOpenAI(model=model, temperature=temperature, api_key=api_key)


def _llm_map(
    texts: list[str],
    map_prompt: ChatPromptTemplate,
    *,
    llm: Runnable,
    concurrency_limit: int,
    map_output_parser: BaseOutputParser | type[BaseModel],
    use_cache: bool = True,
) -> list[str] | list[BaseModel]:
    """Apply the MAP step over a list of texts in parallel with caching.

    Processes multiple texts simultaneously using the LLM and provided prompt.
    The MAP prompt must reference a single variable called "item" (e.g: {item}).

    Caching:
        - When use_cache=True, checks cache for previously processed texts
        - Only sends uncached texts to the LLM
        - Stores results in cache for future reuse
        - Cache key is based on prompt template + input text hash

    Args:
        texts: List of texts to process.
        map_prompt: Prompt template that must contain the {item} variable.
        llm: Language model to use.
        concurrency_limit: Limit of parallel requests.
        map_output_parser: Parser to process LLM responses.
        use_cache: Whether to use caching for repeated texts. Default True.

    Returns:
        List of processed results (strings or BaseModel instances).

    """
    global _llm_cache

    if not texts:
        return []

    # Get the prompt template string for cache key generation
    prompt_template_str = str(map_prompt)

    # Separate cached and uncached texts
    cached_results: dict[int, str | BaseModel] = {}
    uncached_texts: list[str] = []
    uncached_indices: list[int] = []

    if use_cache:
        for idx, text in enumerate(texts):
            cache_key = _get_cache_key(prompt_template_str, text)
            if cache_key in _llm_cache:
                cached_results[idx] = _llm_cache[cache_key]
            else:
                uncached_texts.append(text)
                uncached_indices.append(idx)

        cache_hits = len(cached_results)
        cache_misses = len(uncached_texts)
        if cache_hits > 0:
            logger.info(f"LLM cache: {cache_hits} hits, {cache_misses} misses")
    else:
        uncached_texts = texts
        uncached_indices = list(range(len(texts)))

    # Process uncached texts
    new_results: list[str | BaseModel] = []
    if uncached_texts:
        # Only use structured output if the parser is a Pydantic model
        if isinstance(map_output_parser, type) and issubclass(
            map_output_parser, BaseModel
        ):
            llm_with_parser = llm.with_structured_output(map_output_parser)
            chain = map_prompt | llm_with_parser
        else:
            chain = map_prompt | llm | map_output_parser

        new_results = chain.batch(
            [{"item": d} for d in uncached_texts],
            config={"max_concurrency": concurrency_limit},
        )

        # Store new results in cache
        if use_cache:
            for text, result in zip(uncached_texts, new_results):
                cache_key = _get_cache_key(prompt_template_str, text)
                _llm_cache[cache_key] = result

    # Reconstruct full results in original order
    if not use_cache:
        return new_results

    # Merge cached and new results
    outputs: list[str | BaseModel] = [None] * len(texts)  # type: ignore

    # Fill cached results
    for idx, result in cached_results.items():
        outputs[idx] = result

    # Fill new results
    for i, idx in enumerate(uncached_indices):
        outputs[idx] = new_results[i]

    return outputs


def llm_map(
    texts: list[str],
    map_prompt: ChatPromptTemplate | list[ChatPromptTemplate],
    map_output_parser: type[BaseModel] | None | list[type[BaseModel] | None] = None,
    *,
    llm: Runnable | None = None,
    llm_model: str = "gpt-4o-mini",
    llm_temperature: float = 0.1,
    openai_api_key: str = settings.PROJECT_OPENAI_API_KEY,
    concurrency_limit: int = 16,
    use_cache: bool = True,
) -> MapResult:
    """Execute a Map pipeline with support for single or sequential multi-step processing.

    This is the main entry point for Map-Reduce processing with LLM.
    Supports both single-step and multi-step sequential processing where each step
    processes the output of the previous one.

    Design:
      - Minimal convention over configuration: MAP uses {item}.
      - Parallelism in MAP controlled by `concurrency_limit`.
      - Accepts any LangChain `Runnable` as `llm`. If not provided,
        initializes a default OpenAI client via `ChatOpenAI`.
      - Support for Pydantic structured parsers in the MAP phase.
      - Sequential processing: output of step N becomes input of step N+1.
      - In-memory caching for repeated texts (avoids redundant LLM calls).

    Args:
        texts: Raw texts to process.
        map_prompt: Single prompt OR list of prompts for sequential processing.
        map_output_parser: Parser for MAP results. If None, uses StrOutputParser().
                          Can be a Pydantic BaseModel subclass for structured output.
        llm: Any Runnable; if None, a ChatOpenAI is created by default.
        llm_model: Model used if `llm` is not provided.
        llm_temperature: Temperature used if `llm` is not provided.
        openai_api_key: API key used if `llm` is not provided.
        concurrency_limit: Maximum parallel requests during each MAP step.
        use_cache: Whether to cache responses for repeated texts. Default True.

    Returns:
        MapResult: List with (`map_results`).

    Examples:
        >>> # Single-step processing
        >>> result = llm_map(
        ...     texts=["text1", "text2"],
        ...     map_prompt=ChatPromptTemplate.from_template("Summarize: {item}"),
        ... )

        >>> # Multi-step sequential processing
        >>> result = llm_map(
        ...     texts=["text1", "text2"],
        ...     map_prompt=[extract_prompt, validate_prompt, structure_prompt],
        ...     map_output_parser=[None, None, MyPydanticModel],
        ... )

    """
    # Input validation
    if not texts:
        return MapResult(map_results=[])

    if map_prompt is None:
        raise ValueError("map_prompt cannot be None")

    # Normalize inputs to list format for unified processing
    map_prompts = map_prompt if isinstance(map_prompt, list) else [map_prompt]

    # Validate and normalize parsers
    if map_output_parser is None:
        map_parsers = [None] * len(map_prompts)
    elif isinstance(map_output_parser, list):
        if len(map_output_parser) != len(map_prompts):
            raise ValueError(
                f"Number of parsers ({len(map_output_parser)}) must match "
                f"number of prompts ({len(map_prompts)})"
            )
        map_parsers = map_output_parser
    else:
        map_parsers = [map_output_parser] * len(map_prompts)

    # Initialize LLM
    _llm = llm or _get_llm(llm_model, llm_temperature, settings.PROJECT_OPENAI_API_KEY)
    current_results = texts

    # Execute pipeline steps
    for i, (prompt, parser) in enumerate(zip(map_prompts, map_parsers, strict=True)):
        # Prepare parser for current step
        step_parser = (
            parser
            if (isinstance(parser, type) and issubclass(parser, BaseModel))
            else (parser or StrOutputParser())
        )

        # Execute current step
        step_results = _llm_map(
            texts=current_results,
            map_prompt=prompt,
            llm=_llm,
            concurrency_limit=concurrency_limit,
            map_output_parser=step_parser,
            use_cache=use_cache,
        )

        # Prepare results for next step (convert to strings except for final step)
        current_results = (
            [str(result) for result in step_results]
            if i < len(map_prompts) - 1
            else step_results
        )

    return MapResult(map_results=current_results)
