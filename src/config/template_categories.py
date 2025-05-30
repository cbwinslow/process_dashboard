"""
Template categorization and search for Process Dashboard.

Provides organization and discovery features for configuration templates.
"""

from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass
from datetime import datetime
import logging
import yaml
from pathlib import Path
import re

logger = logging.getLogger("dashboard.config.categories")

@dataclass
class TemplateMetadata:
    """Template metadata."""
    name: str
    description: str
    categories: List[str]
    tags: List[str]
    author: Optional[str] = None
    created: datetime = None
    modified: datetime = None
    version: str = "1.0.0"
    compatibility: str = ">=1.0.0"

    def __post_init__(self):
        """Initialize timestamps."""
        if self.created is None:
            self.created = datetime.now()
        if self.modified is None:
            self.modified = datetime.now()

class TemplateCategoryManager:
    """Template category and search manager."""

    # Default categories
    DEFAULT_CATEGORIES = {
        "system": {
            "name": "System Monitoring",
            "description": "Templates focused on system resource monitoring",
            "icon": "📊"
        },
        "development": {
            "name": "Development",
            "description": "Templates for development environments",
            "icon": "💻"
        },
        "server": {
            "name": "Server Management",
            "description": "Templates for server monitoring and management",
            "icon": "🖥️"
        },
        "performance": {
            "name": "Performance",
            "description": "Templates optimized for performance monitoring",
            "icon": "⚡"
        },
        "minimal": {
            "name": "Minimal",
            "description": "Lightweight configurations with essential features",
            "icon": "🔽"
        },
        "full": {
            "name": "Full Featured",
            "description": "Complete configurations with all features enabled",
            "icon": "🔼"
        },
        "custom": {
            "name": "Custom",
            "description": "User-created custom templates",
            "icon": "🔧"
        }
    }

    def __init__(self, config_dir: Path):
        """Initialize category manager.
        
        Args:
            config_dir: Configuration directory path
        """
        self.config_dir = config_dir
        self.categories_file = config_dir / "categories.yaml"
        self.categories = self.DEFAULT_CATEGORIES.copy()
        self.load_categories()

    def load_categories(self) -> None:
        """Load custom categories from file."""
        try:
            if self.categories_file.exists():
                with open(self.categories_file) as f:
                    custom_categories = yaml.safe_load(f) or {}
                self.categories.update(custom_categories)
        except Exception as e:
            logger.error(f"Failed to load categories: {e}")

    def save_categories(self) -> None:
        """Save custom categories to file."""
        try:
            # Only save non-default categories
            custom_categories = {
                k: v for k, v in self.categories.items()
                if k not in self.DEFAULT_CATEGORIES
            }
            
            with open(self.categories_file, 'w') as f:
                yaml.safe_dump(custom_categories, f, default_flow_style=False)
        except Exception as e:
            logger.error(f"Failed to save categories: {e}")

    def add_category(
        self,
        category_id: str,
        name: str,
        description: str,
        icon: str = "📁"
    ) -> bool:
        """Add new category.
        
        Args:
            category_id: Category identifier
            name: Category name
            description: Category description
            icon: Category icon
            
        Returns:
            True if successful
        """
        try:
            if category_id in self.categories:
                return False
            
            self.categories[category_id] = {
                "name": name,
                "description": description,
                "icon": icon
            }
            
            self.save_categories()
            return True
        except Exception as e:
            logger.error(f"Failed to add category: {e}")
            return False

    def remove_category(self, category_id: str) -> bool:
        """Remove custom category.
        
        Args:
            category_id: Category identifier
            
        Returns:
            True if successful
        """
        try:
            if category_id in self.DEFAULT_CATEGORIES:
                return False
            
            if category_id in self.categories:
                del self.categories[category_id]
                self.save_categories()
                return True
            
            return False
        except Exception as e:
            logger.error(f"Failed to remove category: {e}")
            return False

    def get_category_info(self, category_id: str) -> Optional[Dict[str, str]]:
        """Get category information.
        
        Args:
            category_id: Category identifier
            
        Returns:
            Category information if found
        """
        return self.categories.get(category_id)

    def get_all_categories(self) -> Dict[str, Dict[str, str]]:
        """Get all categories.
        
        Returns:
            Dictionary of categories
        """
        return self.categories.copy()

class TemplateSearch:
    """Template search functionality."""

    def __init__(self):
        """Initialize template search."""
        self.search_index: Dict[str, Set[str]] = {
            "name": set(),
            "description": set(),
            "categories": set(),
            "tags": set()
        }

    def index_template(self, template_id: str, metadata: TemplateMetadata) -> None:
        """Index template for searching.
        
        Args:
            template_id: Template identifier
            metadata: Template metadata
        """
        try:
            # Index searchable fields
            self._add_to_index("name", template_id, metadata.name)
            self._add_to_index("description", template_id, metadata.description)
            
            for category in metadata.categories:
                self._add_to_index("categories", template_id, category)
            
            for tag in metadata.tags:
                self._add_to_index("tags", template_id, tag)
            
        except Exception as e:
            logger.error(f"Failed to index template: {e}")

    def _add_to_index(self, field: str, template_id: str, value: str) -> None:
        """Add value to search index.
        
        Args:
            field: Field name
            template_id: Template identifier
            value: Value to index
        """
        # Create tokens from value
        tokens = set(
            token.lower()
            for token in re.findall(r'\w+', value)
        )
        
        # Add to index
        for token in tokens:
            if token not in self.search_index:
                self.search_index[token] = set()
            self.search_index[token].add(template_id)

    def search(
        self,
        query: str,
        categories: Optional[List[str]] = None,
        tags: Optional[List[str]] = None
    ) -> Set[str]:
        """Search for templates.
        
        Args:
            query: Search query
            categories: Optional category filter
            tags: Optional tag filter
            
        Returns:
            Set of matching template IDs
        """
        try:
            # Tokenize query
            query_tokens = set(
                token.lower()
                for token in re.findall(r'\w+', query)
            )
            
            # Find matches
            matches = set()
            for token in query_tokens:
                if token in self.search_index:
                    if not matches:
                        matches = self.search_index[token].copy()
                    else:
                        matches &= self.search_index[token]
            
            # Apply category filter
            if categories:
                category_matches = set()
                for category in categories:
                    if category in self.search_index:
                        category_matches |= self.search_index[category]
                if category_matches:
                    matches &= category_matches
            
            # Apply tag filter
            if tags:
                tag_matches = set()
                for tag in tags:
                    if tag in self.search_index:
                        tag_matches |= self.search_index[tag]
                if tag_matches:
                    matches &= tag_matches
            
            return matches
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return set()

class TemplateRecommender:
    """Template recommendation system."""

    def __init__(self):
        """Initialize recommender."""
        self.usage_stats: Dict[str, int] = {}
        self.similar_templates: Dict[str, Set[str]] = {}

    def record_usage(self, template_id: str) -> None:
        """Record template usage.
        
        Args:
            template_id: Template identifier
        """
        if template_id not in self.usage_stats:
            self.usage_stats[template_id] = 0
        self.usage_stats[template_id] += 1

    def update_similarities(
        self,
        template_id: str,
        metadata: TemplateMetadata,
        all_templates: Dict[str, TemplateMetadata]
    ) -> None:
        """Update template similarities.
        
        Args:
            template_id: Template identifier
            metadata: Template metadata
            all_templates: All available templates
        """
        try:
            similar = set()
            
            # Find templates with similar categories or tags
            for other_id, other_meta in all_templates.items():
                if other_id == template_id:
                    continue
                
                # Calculate similarity score
                category_overlap = set(metadata.categories) & set(other_meta.categories)
                tag_overlap = set(metadata.tags) & set(other_meta.tags)
                
                score = len(category_overlap) + len(tag_overlap)
                if score > 0:
                    similar.add(other_id)
            
            self.similar_templates[template_id] = similar
            
        except Exception as e:
            logger.error(f"Failed to update similarities: {e}")

    def get_recommendations(
        self,
        template_id: str,
        limit: int = 5
    ) -> List[str]:
        """Get template recommendations.
        
        Args:
            template_id: Template identifier
            limit: Maximum number of recommendations
            
        Returns:
            List of recommended template IDs
        """
        try:
            recommendations = []
            
            # Get similar templates
            similar = self.similar_templates.get(template_id, set())
            
            # Sort by usage
            sorted_similar = sorted(
                similar,
                key=lambda x: self.usage_stats.get(x, 0),
                reverse=True
            )
            
            return sorted_similar[:limit]
            
        except Exception as e:
            logger.error(f"Failed to get recommendations: {e}")
            return []
