from django.test import TestCase
from .models import Recipe, Topic
from .views import Food_Recipe
from unittest.mock import patch

class TopicModelTest(TestCase):
    def setUp(self):
        self.topic = Topic.objects.create(title="Test Topic")

    def test_topic_creation(self):
        self.assertEqual(self.topic.title, "Test Topic")
        self.assertEqual(self.topic.slug, "test-topic")

    def test_topic_str(self):
        self.assertEqual(str(self.topic), "Test Topic")


class RecipeModelTest(TestCase):
    def setUp(self):
        self.topic = Topic.objects.create(title="Test Topic")
        self.recipe = Recipe.objects.create(
            topic=self.topic,
            title="Test Recipe",
            description="A test recipe description.",
            ingredients="Ingredient 1, Ingredient 2",
            directions="Step 1, Step 2",
        )

    def test_recipe_creation(self):
        self.assertEqual(self.recipe.title, "Test Recipe")
        self.assertEqual(self.recipe.slug, "test-recipe")
        self.assertEqual(self.recipe.topic.title, "Test Topic")

    def test_recipe_str(self):
        self.assertEqual(str(self.recipe), "Test Recipe")

    def test_get_url(self):
        expected_url = f"/detail/{self.recipe.slug}/"
        self.assertEqual(self.recipe.get_url(), expected_url)


class ViewTests(TestCase):
    def setUp(self):
        self.topic = Topic.objects.create(title="Breakfast")
        self.recipe = Recipe.objects.create(
            topic=self.topic,
            title="Pancakes",
            description="Fluffy pancakes.",
            ingredients="Flour, eggs, milk",
            directions="Mix and cook.",
        )

    def test_home_view(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "home.html")
        self.assertIn("total_recipes", response.context)

    def test_detail_view(self):
        response = self.client.get(self.recipe.get_url())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "detail.html")
        self.assertEqual(response.context["recipe"], self.recipe)


class FoodRecipeModelTest(TestCase):
    def setUp(self):
        self.data = {
            "label": "Test Food",
            "image": "test.jpg",
            "healthLabels": ["Vegetarian", "Peanut-Free"],
            "url": "http://test.com",
            "totalTime": 60,
            "calories": 500,
            "totalNutrients": {
                "FAT": {"quantity": 20},
                "PROCNT": {"quantity": 30},
                "CHOCDF": {"quantity": 50},
            },
            "cuisineType": ["american"],
        }
        self.food_recipe = Food_Recipe(self.data)

    def test_food_recipe_creation(self):
        self.assertEqual(self.food_recipe.title, "Test Food")
        self.assertEqual(self.food_recipe.image, "test.jpg")
        self.assertEqual(self.food_recipe.description, ["Vegetarian", "Peanut-Free"])
        self.assertEqual(self.food_recipe.url, "http://test.com")
        self.assertEqual(self.food_recipe.time, 60)
        self.assertEqual(self.food_recipe.calories, 500)
        self.assertEqual(self.food_recipe.fat, 20)
        self.assertEqual(self.food_recipe.protein, 30)
        self.assertEqual(self.food_recipe.carbs, 50)
        self.assertEqual(self.food_recipe.cusine, ["american"])

    def test_describe_method(self):
        self.assertEqual(self.food_recipe.describe(), "Vegetarian * Peanut-Free")

    def test_save_method(self):
        # The save method is a no-op, so this test just ensures it runs without error
        self.food_recipe.save()


class APITests(TestCase):
    @patch("main.views.ed_handler.search_recipe")
    def test_search_with_api_view(self, mock_search_recipe):
        # Mock the API response
        mock_response = {
            "count": 1,
            "hits": [
                {
                    "recipe": {
                        "label": "Chicken Vesuvio",
                        "image": "http://example.com/image.jpg",
                        "healthLabels": ["Low-Carb"],
                        "url": "http://example.com/recipe",
                        "totalTime": 60,
                        "calories": 500,
                        "totalNutrients": {
                            "FAT": {"quantity": 20},
                            "PROCNT": {"quantity": 30},
                            "CHOCDF": {"quantity": 50},
                        },
                        "cuisineType": ["italian"],
                    }
                }
            ],
        }
        mock_search_recipe.return_value = mock_response

        # Use the same client for both requests to maintain the session
        client = self.client

        # Make a request to the view
        response = client.get("/search/?search=chicken")

        # Check that the API was called
        mock_search_recipe.assert_called_once_with("chicken")

        # Check the response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "search.html")
        self.assertIn("results", response.context)
        self.assertEqual(len(response.context["results"]), 1)
        self.assertEqual(response.context["results"][0].title, "Chicken Vesuvio")

        # Make a second request with the same query to test session caching
        response = client.get("/search/?search=chicken")

        # The mock should still have been called only once
        mock_search_recipe.assert_called_once_with("chicken")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["results"]), 1)