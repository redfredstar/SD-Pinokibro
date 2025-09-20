"""
app/core/P05_SearchEngine.py
Application Discovery Intelligence Engine

Provides fast, weighted search across the Pinokio applications database with
support for text queries, category filters, and tag filters.
"""

import json
import traceback
from pathlib import Path
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass, field

@dataclass
class PinokioApp:
    """
    Structured representation of a Pinokio application.
    
    Includes pre-computed search fields for performance optimization.
    """
    id: str
    name: str
    description: str
    category: str
    tags: List[str]
    author: str
    install_size_mb: Optional[int]
    gpu_required: bool
    install_url: str
    thumbnail_url: Optional[str]
    
    # Pre-computed search fields for performance
    search_text: str = field(init=False)
    tag_set: Set[str] = field(init=False)
    
    def __post_init__(self):
        """Pre-compute search optimization fields."""
        # Concatenate searchable text in lowercase
        self.search_text = f"{self.name} {self.description} {' '.join(self.tags)}".lower()
        
        # Convert tags to set for O(1) membership testing
        self.tag_set = set(tag.lower() for tag in self.tags)

class P05_SearchEngine:
    """
    Intelligent application discovery engine with weighted relevance ranking.
    
    Features:
    - Fast in-memory search across application metadata
    - Weighted relevance scoring algorithm
    - Support for category and tag filtering
    - Pre-computed indices for performance
    """
    
    def __init__(self, db_path: str = "data/cleaned_pinokio_apps.json"):
        """
        Initialize the search engine and load the applications database.
        
        Args:
            db_path: Path to the cleaned Pinokio apps JSON database
        """
        self.db_path = db_path
        self.apps: List[PinokioApp] = []
        self.category_index: Dict[str, List[PinokioApp]] = {}
        self.tag_index: Dict[str, List[PinokioApp]] = {}
        
        # Load database and build indices
        self._load_apps_database(db_path)
        self._build_search_indices()
    
    def _load_apps_database(self, db_path: str) -> None:
        """
        Load applications from JSON database into dataclass objects.
        
        Args:
            db_path: Path to the JSON database file
        """
        try:
            db_file = Path(db_path)
            if not db_file.exists():
                print(f"[ERROR] Database file not found: {db_path}")
                return
            
            with open(db_file, 'r', encoding='utf-8') as f:
                raw_apps_data = json.load(f)
            
            # Convert raw dictionaries to dataclass objects
            for app_data in raw_apps_data:
                try:
                    app = PinokioApp(
                        id=app_data.get('id', ''),
                        name=app_data.get('name', 'Unknown'),
                        description=app_data.get('description', ''),
                        category=app_data.get('category', 'Other'),
                        tags=app_data.get('tags', []),
                        author=app_data.get('author', 'Unknown'),
                        install_size_mb=app_data.get('install_size_mb'),
                        gpu_required=app_data.get('gpu_required', False),
                        install_url=app_data.get('install_url', ''),
                        thumbnail_url=app_data.get('thumbnail_url')
                    )
                    self.apps.append(app)
                    
                except Exception as e:
                    print(f"[WARNING] Skipped malformed app data: {e}")
                    print(traceback.format_exc())
                    continue
            
            print(f"[INFO] Loaded {len(self.apps)} applications from database")
            
        except FileNotFoundError as e:
            print(f"[ERROR] Failed to load database file: {e}")
            print(traceback.format_exc())
        except json.JSONDecodeError as e:
            print(f"[ERROR] Invalid JSON in database file: {e}")
            print(traceback.format_exc())
        except Exception as e:
            print(f"[ERROR] Unexpected error loading database: {e}")
            print(traceback.format_exc())
    
    def _build_search_indices(self) -> None:
        """Build category and tag indices for O(1) filtering performance."""
        # Build category index
        self.category_index = {}
        for app in self.apps:
            category_lower = app.category.lower()
            if category_lower not in self.category_index:
                self.category_index[category_lower] = []
            self.category_index[category_lower].append(app)
        
        # Build tag index
        self.tag_index = {}
        for app in self.apps:
            for tag in app.tags:
                tag_lower = tag.lower()
                if tag_lower not in self.tag_index:
                    self.tag_index[tag_lower] = []
                self.tag_index[tag_lower].append(app)
    
    def _calculate_score(self, app: PinokioApp, query: str) -> float:
        """
        Calculate weighted relevance score for an app against a query.
        
        Scoring weights:
        - Name match: 50 points + position bonus
        - Tag exact match: 30 points per tag
        - Description match: 10 points per occurrence
        
        Args:
            app: Application to score
            query: Search query string
            
        Returns:
            Relevance score as float
        """
        if not query or not query.strip():
            return 1.0  # Default score for empty query
        
        query_lower = query.lower().strip()
        score = 0.0
        
        # Name scoring (50 points + position bonus)
        name_lower = app.name.lower()
        if query_lower in name_lower:
            score += 50.0
            
            # Bonus for exact match
            if name_lower == query_lower:
                score += 50.0  # Total 100 for exact match
            # Bonus for match at beginning
            elif name_lower.startswith(query_lower):
                score += 25.0  # Total 75 for prefix match
            # Position bonus (earlier = better)
            else:
                position = name_lower.find(query_lower)
                position_bonus = max(0, 20 - position)
                score += position_bonus
        
        # Tag scoring (30 points per exact match)
        for tag in app.tags:
            tag_lower = tag.lower()
            if tag_lower == query_lower:
                score += 30.0
            elif query_lower in tag_lower:
                score += 15.0  # Partial tag match
        
        # Description scoring (10 points per occurrence)
        description_lower = app.description.lower()
        occurrence_count = description_lower.count(query_lower)
        score += occurrence_count * 10.0
        
        return score
    
    def _filter_by_category(self, apps: List[PinokioApp], category: str) -> List[PinokioApp]:
        """
        Filter apps by category using pre-built index.
        
        Args:
            apps: List of apps to filter
            category: Category to filter by
            
        Returns:
            Filtered list of apps
        """
        category_lower = category.lower()
        
        # Use pre-built index for O(1) lookup
        if category_lower in self.category_index:
            category_apps = set(self.category_index[category_lower])
            # Return intersection with input apps
            return [app for app in apps if app in category_apps]
        else:
            return []  # No apps in this category
    
    def _filter_by_tags(self, apps: List[PinokioApp], tags: List[str]) -> List[PinokioApp]:
        """
        Filter apps by tags (OR logic - app matches ANY tag).
        
        Args:
            apps: List of apps to filter
            tags: List of tags to filter by
            
        Returns:
            Filtered list of apps
        """
        if not tags:
            return apps
        
        tags_lower = [tag.lower() for tag in tags]
        matching_apps = set()
        
        # Use tag index for efficient lookup
        for tag in tags_lower:
            if tag in self.tag_index:
                matching_apps.update(self.tag_index[tag])
        
        # Return intersection with input apps
        return [app for app in apps if app in matching_apps]
    
    def search(self, query: str = "", filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Search for applications with optional filtering and relevance ranking.
        
        Pipeline:
        1. Apply filters to reduce search space
        2. Calculate relevance scores for remaining apps
        3. Sort by score and return formatted results
        
        Args:
            query: Search query string
            filters: Optional filters dict with 'category', 'tags', 'gpu_required', etc.
            
        Returns:
            List of app dictionaries sorted by relevance score
        """
        if not self.apps:
            return []
        
        # Step 1: Apply filters to get candidate apps
        candidate_apps = self.apps.copy()
        
        if filters:
            # Category filter
            if 'category' in filters and filters['category']:
                candidate_apps = self._filter_by_category(candidate_apps, filters['category'])
            
            # Tags filter (OR logic)
            if 'tags' in filters and filters['tags']:
                candidate_apps = self._filter_by_tags(candidate_apps, filters['tags'])
            
            # GPU filter
            if 'gpu_required' in filters:
                gpu_required = filters['gpu_required']
                candidate_apps = [app for app in candidate_apps if app.gpu_required == gpu_required]
            
            # Size filter (max install size)
            if 'max_size_mb' in filters and filters['max_size_mb']:
                max_size = filters['max_size_mb']
                candidate_apps = [
                    app for app in candidate_apps
                    if app.install_size_mb is None or app.install_size_mb <= max_size
                ]
        
        # Step 2: Score and rank results
        scored_results = []
        
        for app in candidate_apps:
            score = self._calculate_score(app, query)
            
            # Only include apps with positive scores
            if score > 0:
                result = {
                    'id': app.id,
                    'name': app.name,
                    'description': app.description,
                    'category': app.category,
                    'tags': app.tags,
                    'author': app.author,
                    'install_size_mb': app.install_size_mb,
                    'gpu_required': app.gpu_required,
                    'install_url': app.install_url,
                    'thumbnail_url': app.thumbnail_url,
                    'relevance_score': score
                }
                scored_results.append(result)
        
        # Step 3: Sort by relevance score (descending)
        scored_results.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        # Limit to top 50 results for performance
        return scored_results[:50]
    
    def get_categories(self) -> List[str]:
        """
        Get list of all available categories.
        
        Returns:
            Sorted list of category names
        """
        return sorted(list(self.category_index.keys()))
    
    def get_all_tags(self) -> List[str]:
        """
        Get list of all available tags.
        
        Returns:
            Sorted list of tag names
        """
        return sorted(list(self.tag_index.keys()))
    
    def get_app_by_id(self, app_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific app by its ID.
        
        Args:
            app_id: Application ID to search for
            
        Returns:
            App dictionary or None if not found
        """
        for app in self.apps:
            if app.id == app_id:
                return {
                    'id': app.id,
                    'name': app.name,
                    'description': app.description,
                    'category': app.category,
                    'tags': app.tags,
                    'author': app.author,
                    'install_size_mb': app.install_size_mb,
                    'gpu_required': app.gpu_required,
                    'install_url': app.install_url,
                    'thumbnail_url': app.thumbnail_url
                }
        return None
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the loaded database.
        
        Returns:
            Dictionary with database statistics
        """
        total_apps = len(self.apps)
        gpu_apps = sum(1 for app in self.apps if app.gpu_required)
        
        category_counts = {}
        for category, apps in self.category_index.items():
            category_counts[category] = len(apps)
        
        return {
            'total_apps': total_apps,
            'gpu_apps': gpu_apps,
            'non_gpu_apps': total_apps - gpu_apps,
            'categories': len(self.category_index),
            'unique_tags': len(self.tag_index),
            'category_distribution': category_counts
        }