"""
P05_SearchEngine.py - The Librarian & Search Engine (Intelligent App Discovery)

This module implements a fast, in-memory search system for intelligent application
discovery with weighted relevance ranking. It provides O(1) lookups for categories
and tags, and a scoring algorithm to rank search results by relevance.

Author: Pinokiobro Architect
Phase: P05 - The Librarian & Search Engine
"""

import json
import os
import re
from typing import List, Dict, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging


class SearchFieldType(Enum):
    """Enum for different types of searchable fields."""

    NAME = "name"
    TAG = "tag"
    DESCRIPTION = "description"
    CATEGORY = "category"


@dataclass
class PinokioApp:
    """
    Dataclass representing a Pinokio application with type-safe attributes.

    This class provides a structured representation of application data
    loaded from the JSON database.
    """

    id: str
    name: str
    description: str
    category: str
    tags: List[str] = field(default_factory=list)
    gpu_required: bool = False
    size_mb: Optional[int] = None
    installer_path: Optional[str] = None
    # Pre-computed search fields for performance
    search_text: str = ""
    tag_set: Set[str] = field(default_factory=set)

    def __post_init__(self):
        """Initialize pre-computed search fields after object creation."""
        # Create lowercase search text for case-insensitive matching
        self.search_text = f"{self.name} {self.description}".lower()

        # Create a set of lowercase tags for O(1) lookups
        self.tag_set = {tag.lower() for tag in self.tags}


class P05_SearchEngine:
    """
    A fast, in-memory search engine for Pinokio applications.

    This class provides intelligent application discovery with weighted relevance
    ranking, O(1) lookups for categories and tags, and resilient error handling.
    """

    def __init__(self, data_file_path: Optional[str] = None):
        """
        Initialize the search engine with optional data file path.

        Args:
            data_file_path: Path to the JSON file containing app data.
                           If None, uses the default path.
        """
        self.apps: List[PinokioApp] = []
        self.category_index: Dict[str, List[PinokioApp]] = {}
        self.tag_index: Dict[str, List[PinokioApp]] = {}

        # Set default data file path if not provided
        if data_file_path is None:
            # Default path relative to this file
            current_dir = os.path.dirname(os.path.abspath(__file__))
            data_file_path = os.path.join(
                current_dir, "..", "Data", "cleaned_pinokio_apps.json"
            )

        self.data_file_path = data_file_path

    def load_data(self) -> bool:
        """
        Load application data from the JSON file.

        Returns:
            True if data was loaded successfully, False otherwise.
        """
        try:
            if not os.path.exists(self.data_file_path):
                logging.error(f"Data file not found: {self.data_file_path}")
                return False

            with open(self.data_file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Clear existing data
            self.apps.clear()
            self.category_index.clear()
            self.tag_index.clear()

            # Process each app entry
            for app_data in data:
                try:
                    app = self._create_app_from_data(app_data)
                    self.apps.append(app)
                    self._index_app(app)
                except Exception as e:
                    logging.warning(
                        f"Failed to process app entry: {app_data}. Error: {str(e)}"
                    )
                    continue

            logging.info(f"Successfully loaded {len(self.apps)} applications")
            return True

        except json.JSONDecodeError as e:
            logging.error(f"Invalid JSON in data file: {str(e)}", exc_info=True)
            return False
        except Exception as e:
            logging.error(f"Failed to load data: {str(e)}", exc_info=True)
            return False

    def _create_app_from_data(self, app_data: Dict[str, Any]) -> PinokioApp:
        """
        Create a PinokioApp object from raw JSON data.

        Args:
            app_data: Raw dictionary data from JSON.

        Returns:
            A PinokioApp object.

        Raises:
            ValueError: If required fields are missing.
        """
        # Validate required fields
        required_fields = ["id", "name", "description", "category"]
        for field in required_fields:
            if field not in app_data:
                raise ValueError(f"Missing required field: {field}")

        # Create the app object
        app = PinokioApp(
            id=str(app_data["id"]),
            name=str(app_data["name"]),
            description=str(app_data["description"]),
            category=str(app_data["category"]),
            tags=app_data.get("tags", []),
            gpu_required=bool(app_data.get("gpu_required", False)),
            size_mb=app_data.get("size_mb"),
            installer_path=app_data.get("installer_path"),
        )

        return app

    def _index_app(self, app: PinokioApp) -> None:
        """
        Add an app to the category and tag indexes.

        Args:
            app: The PinokioApp to index.
        """
        # Index by category
        category = app.category.lower()
        if category not in self.category_index:
            self.category_index[category] = []
        self.category_index[category].append(app)

        # Index by tags
        for tag in app.tag_set:
            if tag not in self.tag_index:
                self.tag_index[tag] = []
            self.tag_index[tag].append(app)

    def search(
        self, query: str, filters: Optional[Dict[str, Any]] = None, limit: int = 20
    ) -> List[Tuple[PinokioApp, float]]:
        """
        Search for applications with optional filters and relevance scoring.

        Args:
            query: The search query string.
            filters: Optional dictionary of filters (category, tags, gpu, size).
            limit: Maximum number of results to return.

        Returns:
            A list of (app, score) tuples, sorted by score in descending order.
        """
        if not self.apps:
            return []

        # Handle case where there's no query but filters are provided
        if not query and filters:
            candidate_apps = self._apply_filters(filters)
            # Return all filtered apps with a default score of 1.0
            return [(app, 1.0) for app in candidate_apps[:limit]]

        # If no query and no filters, return empty results
        if not query and not filters:
            return []

        # Apply filters first to reduce search space
        candidate_apps = self._apply_filters(filters) if filters else self.apps

        if not candidate_apps:
            return []

        # Score and rank candidates
        results = []
        query_lower = query.lower()

        for app in candidate_apps:
            score = self._calculate_relevance_score(app, query_lower)
            if score > 0:
                results.append((app, score))

        # Sort by score (descending) and limit results
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:limit]

    def _apply_filters(self, filters: Dict[str, Any]) -> List[PinokioApp]:
        """
        Apply filters to reduce the search space.

        Args:
            filters: Dictionary of filter criteria.

        Returns:
            List of apps that pass all filters.
        """
        filtered_apps = self.apps

        # Category filter (O(1) lookup)
        if "category" in filters:
            category = filters["category"].lower()
            if category in self.category_index:
                filtered_apps = self.category_index[category]
            else:
                return []  # No apps in this category

        # Tag filter (O(1) lookup per tag)
        if "tags" in filters:
            tags = [tag.lower() for tag in filters["tags"]]
            if tags:
                # Start with apps that have the first tag
                if tags[0] in self.tag_index:
                    tag_filtered_ids = {app.id for app in self.tag_index[tags[0]]}
                else:
                    return []  # No apps with this tag

                # Intersect with apps that have remaining tags
                for tag in tags[1:]:
                    if tag in self.tag_index:
                        tag_filtered_ids.intersection_update(
                            {app.id for app in self.tag_index[tag]}
                        )
                    else:
                        return []  # No apps with this tag

                # Convert back to list and intersect with current filtered_apps
                filtered_apps = [
                    app for app in filtered_apps if app.id in tag_filtered_ids
                ]

        # GPU requirement filter
        if "gpu_required" in filters:
            gpu_required = bool(filters["gpu_required"])
            filtered_apps = [
                app for app in filtered_apps if app.gpu_required == gpu_required
            ]

        # Size filter
        if "max_size_mb" in filters:
            max_size = filters["max_size_mb"]
            filtered_apps = [
                app for app in filtered_apps if app.size_mb and app.size_mb <= max_size
            ]
            filtered_apps = [
                app
                for app in filtered_apps
                if app.size_mb is None or app.size_mb <= max_size
            ]

        return filtered_apps

    def _calculate_relevance_score(self, app: PinokioApp, query: str) -> float:
        """
        Calculate a relevance score for an app against a query.

        Args:
            app: The PinokioApp to score.
            query: The lowercase search query.

        Returns:
            A relevance score (higher is more relevant).
        """
        score = 0.0

        # Weight for different match types
        weights = {
            SearchFieldType.NAME: 3.0,  # Name matches are most important
            SearchFieldType.TAG: 2.0,  # Tag matches are important
            SearchFieldType.DESCRIPTION: 1.0,  # Description matches are least important
        }

        # Check for exact name match (highest score)
        if query == app.name.lower():
            score += weights[SearchFieldType.NAME] * 10
        # Check for name substring match
        elif query in app.name.lower():
            score += weights[SearchFieldType.NAME] * 5

        # Check for tag matches
        for tag in app.tag_set:
            if query == tag:
                score += weights[SearchFieldType.TAG] * 5
            elif query in tag:
                score += weights[SearchFieldType.TAG] * 2

        # Check for description matches
        if query in app.search_text:
            # Count occurrences for partial matches
            occurrences = len(
                re.findall(r"\b" + re.escape(query) + r"\b", app.search_text)
            )
            score += weights[SearchFieldType.DESCRIPTION] * occurrences

        return score

    def get_categories(self) -> List[str]:
        """
        Get all unique categories in the database.

        Returns:
            List of category names.
        """
        return list(self.category_index.keys())

    def get_tags(self) -> List[str]:
        """
        Get all unique tags in the database.

        Returns:
            List of tag names.
        """
        return list(self.tag_index.keys())

    def get_app_by_id(self, app_id: str) -> Optional[PinokioApp]:
        """
        Get an application by its ID.

        Args:
            app_id: The ID of the application to retrieve.

        Returns:
            The PinokioApp object if found, None otherwise.
        """
        for app in self.apps:
            if app.id == app_id:
                return app
        return None

    def get_apps_by_category(self, category: str) -> List[PinokioApp]:
        """
        Get all applications in a specific category.

        Args:
            category: The category name.

        Returns:
            List of PinokioApp objects in the category.
        """
        category_lower = category.lower()
        return self.category_index.get(category_lower, []).copy()

    def get_apps_by_tag(self, tag: str) -> List[PinokioApp]:
        """
        Get all applications with a specific tag.

        Args:
            tag: The tag name.

        Returns:
            List of PinokioApp objects with the tag.
        """
        tag_lower = tag.lower()
        return self.tag_index.get(tag_lower, []).copy()

    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the loaded applications.

        Returns:
            Dictionary with various statistics.
        """
        if not self.apps:
            return {"total_apps": 0}

        stats = {
            "total_apps": len(self.apps),
            "total_categories": len(self.category_index),
            "total_tags": len(self.tag_index),
            "gpu_required_count": sum(1 for app in self.apps if app.gpu_required),
            "avg_size_mb": sum(
                app.size_mb for app in self.apps if app.size_mb is not None
            )
            / sum(1 for app in self.apps if app.size_mb is not None),
        }

        return stats
