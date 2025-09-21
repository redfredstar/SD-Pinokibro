"""
P05-Test_SearchEngine.py - Test Suite for P05_SearchEngine

This test suite validates the functionality of the P05_SearchEngine module,
ensuring it correctly loads application data, performs intelligent searches
with weighted relevance ranking, and provides O(1) lookups for categories and tags.

Author: Pinokiobro Architect
Phase: P05 - The Librarian & Search Engine
"""

import unittest
import tempfile
import os
import json
import sys

# Add the App directory to the path to import our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Import the P05_SearchEngine module directly
import importlib.util

spec = importlib.util.spec_from_file_location(
    "P05_SearchEngine",
    os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "Core", "P05_SearchEngine.py"
    ),
)
P05_SearchEngine_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(P05_SearchEngine_module)

P05_SearchEngine = P05_SearchEngine_module.P05_SearchEngine
PinokioApp = P05_SearchEngine_module.PinokioApp
SearchFieldType = P05_SearchEngine_module.SearchFieldType


class TestP05SearchEngine(unittest.TestCase):
    """Test cases for the P05_SearchEngine class."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.temp_dir = tempfile.mkdtemp()
        self.data_file = os.path.join(self.temp_dir, "test_apps.json")

        # Create test data
        self.test_apps = [
            {
                "id": "app1",
                "name": "Python Image Editor",
                "description": "A powerful image editing tool built with Python",
                "category": "Graphics",
                "tags": ["python", "image", "editor"],
                "gpu_required": False,
                "size_mb": 150,
            },
            {
                "id": "app2",
                "name": "Neural Network Trainer",
                "description": "Train deep learning models with GPU acceleration",
                "category": "Machine Learning",
                "tags": ["python", "neural", "gpu", "training"],
                "gpu_required": True,
                "size_mb": 500,
            },
            {
                "id": "app3",
                "name": "Web Server Manager",
                "description": "Manage multiple web servers from a single interface",
                "category": "Development",
                "tags": ["web", "server", "management"],
                "gpu_required": False,
                "size_mb": 75,
            },
            {
                "id": "app4",
                "name": "Python Data Visualizer",
                "description": "Create beautiful data visualizations with Python",
                "category": "Data Science",
                "tags": ["python", "data", "visualization"],
                "gpu_required": False,
                "size_mb": 200,
            },
        ]

        # Write test data to file
        with open(self.data_file, "w") as f:
            json.dump(self.test_apps, f)

        # Initialize search engine with test data
        self.search_engine = P05_SearchEngine(self.data_file)
        self.search_engine.load_data()

    def tearDown(self):
        """Clean up test fixtures after each test method."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_initialization(self):
        """Test that SearchEngine initializes correctly."""
        engine = P05_SearchEngine()
        self.assertEqual(len(engine.apps), 0)
        self.assertEqual(len(engine.category_index), 0)
        self.assertEqual(len(engine.tag_index), 0)

    def test_load_data_success(self):
        """Test successful loading of application data."""
        self.assertEqual(len(self.search_engine.apps), 4)
        self.assertEqual(len(self.search_engine.category_index), 4)
        self.assertTrue(len(self.search_engine.tag_index) > 0)

    def test_load_data_file_not_found(self):
        """Test loading data from a non-existent file."""
        engine = P05_SearchEngine("/nonexistent/file.json")
        result = engine.load_data()
        self.assertFalse(result)

    def test_load_data_invalid_json(self):
        """Test loading data from an invalid JSON file."""
        invalid_file = os.path.join(self.temp_dir, "invalid.json")
        with open(invalid_file, "w") as f:
            f.write("invalid json content")

        engine = P05_SearchEngine(invalid_file)
        result = engine.load_data()
        self.assertFalse(result)

    def test_create_app_from_data(self):
        """Test creating a PinokioApp from raw data."""
        app_data = self.test_apps[0]
        app = self.search_engine._create_app_from_data(app_data)

        self.assertEqual(app.id, "app1")
        self.assertEqual(app.name, "Python Image Editor")
        self.assertEqual(app.category, "Graphics")
        self.assertEqual(app.tags, ["python", "image", "editor"])
        self.assertFalse(app.gpu_required)
        self.assertEqual(app.size_mb, 150)
        self.assertTrue(len(app.search_text) > 0)
        self.assertTrue(len(app.tag_set) > 0)

    def test_create_app_from_data_missing_required_field(self):
        """Test error handling when required fields are missing."""
        invalid_data = {
            "id": "test",
            "name": "Test App",
        }  # Missing description and category

        with self.assertRaises(ValueError):
            self.search_engine._create_app_from_data(invalid_data)

    def test_index_app(self):
        """Test that apps are correctly indexed by category and tags."""
        app = self.search_engine.apps[0]  # Python Image Editor

        # Check category index
        self.assertIn("graphics", self.search_engine.category_index)
        self.assertIn(app, self.search_engine.category_index["graphics"])

        # Check tag indexes
        self.assertIn("python", self.search_engine.tag_index)
        self.assertIn(app, self.search_engine.tag_index["python"])
        self.assertIn("image", self.search_engine.tag_index)
        self.assertIn(app, self.search_engine.tag_index["image"])

    def test_search_no_query(self):
        """Test searching with an empty query."""
        results = self.search_engine.search("")
        self.assertEqual(len(results), 0)

    def test_search_by_name(self):
        """Test searching by application name."""
        results = self.search_engine.search("Python Image Editor")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][0].id, "app1")
        self.assertGreater(results[0][1], 0)  # Should have a positive score

    def test_search_by_name_partial(self):
        """Test searching by partial application name."""
        results = self.search_engine.search("Image Editor")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][0].id, "app1")

    def test_search_by_description(self):
        """Test searching by description content."""
        results = self.search_engine.search("deep learning")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][0].id, "app2")

    def test_search_by_tag(self):
        """Test searching by tag."""
        results = self.search_engine.search("gpu")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][0].id, "app2")

    def test_search_multiple_results(self):
        """Test search that returns multiple results."""
        results = self.search_engine.search("python")
        self.assertGreaterEqual(len(results), 2)  # Should find at least 2 Python apps

        # Results should be sorted by score
        for i in range(len(results) - 1):
            self.assertGreaterEqual(results[i][1], results[i + 1][1])

    def test_search_with_category_filter(self):
        """Test searching with a category filter."""
        filters = {"category": "Graphics"}
        results = self.search_engine.search("python", filters=filters)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][0].id, "app1")

    def test_search_with_tag_filter(self):
        """Test searching with a tag filter."""
        filters = {"tags": ["gpu"]}
        results = self.search_engine.search("", filters=filters)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][0].id, "app2")

    def test_search_with_gpu_filter(self):
        """Test searching with GPU requirement filter."""
        filters = {"gpu_required": True}
        results = self.search_engine.search("", filters=filters)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][0].id, "app2")

    def test_search_with_size_filter(self):
        """Test searching with size filter."""
        filters = {"max_size_mb": 100}
        results = self.search_engine.search("", filters=filters)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][0].id, "app3")

    def test_search_with_multiple_filters(self):
        """Test searching with multiple filters."""
        filters = {"category": "Machine Learning", "gpu_required": True}
        results = self.search_engine.search("", filters=filters)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][0].id, "app2")

    def test_search_no_results_with_filters(self):
        """Test search with filters that return no results."""
        filters = {"category": "Nonexistent Category"}
        results = self.search_engine.search("python", filters=filters)
        self.assertEqual(len(results), 0)

    def test_search_limit_results(self):
        """Test limiting the number of search results."""
        results = self.search_engine.search("python", limit=1)
        self.assertEqual(len(results), 1)

    def test_calculate_relevance_score(self):
        """Test relevance score calculation."""
        app = self.search_engine.apps[0]  # Python Image Editor

        # Exact name match should have highest score
        score1 = self.search_engine._calculate_relevance_score(
            app, "python image editor"
        )
        # Partial name match should have lower score
        score2 = self.search_engine._calculate_relevance_score(app, "image editor")
        # Description match should have even lower score
        score3 = self.search_engine._calculate_relevance_score(app, "powerful")

        self.assertGreater(score1, score2)
        self.assertGreater(score2, score3)

    def test_get_categories(self):
        """Test getting all categories."""
        categories = self.search_engine.get_categories()
        self.assertIn("graphics", categories)
        self.assertIn("machine learning", categories)
        self.assertIn("development", categories)
        self.assertIn("data science", categories)

    def test_get_tags(self):
        """Test getting all tags."""
        tags = self.search_engine.get_tags()
        self.assertIn("python", tags)
        self.assertIn("gpu", tags)
        self.assertIn("image", tags)

    def test_get_app_by_id(self):
        """Test getting an app by its ID."""
        app = self.search_engine.get_app_by_id("app1")
        self.assertIsNotNone(app)
        self.assertEqual(app.id, "app1")

        # Test with non-existent ID
        app = self.search_engine.get_app_by_id("nonexistent")
        self.assertIsNone(app)

    def test_get_apps_by_category(self):
        """Test getting apps by category."""
        apps = self.search_engine.get_apps_by_category("Graphics")
        self.assertEqual(len(apps), 1)
        self.assertEqual(apps[0].id, "app1")

        # Test with non-existent category
        apps = self.search_engine.get_apps_by_category("Nonexistent")
        self.assertEqual(len(apps), 0)

    def test_get_apps_by_tag(self):
        """Test getting apps by tag."""
        apps = self.search_engine.get_apps_by_tag("python")
        self.assertGreaterEqual(len(apps), 2)  # Should find at least 2 Python apps

        # Test with non-existent tag
        apps = self.search_engine.get_apps_by_tag("nonexistent")
        self.assertEqual(len(apps), 0)

    def test_get_stats(self):
        """Test getting statistics about loaded apps."""
        stats = self.search_engine.get_stats()

        self.assertEqual(stats["total_apps"], 4)
        self.assertEqual(stats["total_categories"], 4)
        self.assertGreater(stats["total_tags"], 0)
        self.assertEqual(stats["gpu_required_count"], 1)
        self.assertGreater(stats["avg_size_mb"], 0)

    def test_get_stats_empty_database(self):
        """Test getting stats when no apps are loaded."""
        engine = P05_SearchEngine()
        stats = engine.get_stats()

        self.assertEqual(stats["total_apps"], 0)
        self.assertNotIn("total_categories", stats)
        self.assertNotIn("total_tags", stats)


class TestPinokioApp(unittest.TestCase):
    """Test cases for the PinokioApp dataclass."""

    def test_pinokio_app_creation(self):
        """Test creating a PinokioApp object."""
        app = PinokioApp(
            id="test",
            name="Test App",
            description="A test application",
            category="Test",
            tags=["test", "sample"],
            gpu_required=False,
            size_mb=100,
        )

        self.assertEqual(app.id, "test")
        self.assertEqual(app.name, "Test App")
        self.assertEqual(app.description, "A test application")
        self.assertEqual(app.category, "Test")
        self.assertEqual(app.tags, ["test", "sample"])
        self.assertFalse(app.gpu_required)
        self.assertEqual(app.size_mb, 100)
        self.assertTrue(len(app.search_text) > 0)
        self.assertEqual(len(app.tag_set), 2)

    def test_pinokio_app_post_init(self):
        """Test that post-initialization creates search fields correctly."""
        app = PinokioApp(
            id="test",
            name="Test App",
            description="A test application",
            category="Test",
            tags=["Test", "SAMPLE"],
        )

        # Check search_text is lowercase
        self.assertEqual(app.search_text, "test app a test application")

        # Check tag_set is lowercase
        self.assertEqual(app.tag_set, {"test", "sample"})


if __name__ == "__main__":
    # Configure logging to see debug output
    import logging

    logging.basicConfig(level=logging.DEBUG)

    # Run the tests
    unittest.main(verbosity=2)
