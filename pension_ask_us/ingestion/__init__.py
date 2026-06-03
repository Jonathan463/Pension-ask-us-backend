"""Article collection -> cleaning -> chunking pipeline."""
from .pipeline import IngestionPipeline
from .sources import ArticleSource, StaticUrlSource
from .fetcher import ArticleFetcher, HttpArticleFetcher
from .cleaner import HtmlCleaner
from .chunker import TextChunker

__all__ = [
    "IngestionPipeline",
    "ArticleSource",
    "StaticUrlSource",
    "ArticleFetcher",
    "HttpArticleFetcher",
    "HtmlCleaner",
    "TextChunker",
]
