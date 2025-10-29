import os
import json
import logging
from typing import List, Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import google.generativeai as genai
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="AI Diet Plan & Nutrition API",
    description="Generate personalized diet plans and nutritional breakdown using Google Gemini AI",
    version="1.0.0"
)

# Configure Google Gemini API
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    logger.error("GOOGLE_API_KEY not found in environment variables")
    raise ValueError("GOOGLE_API_KEY environment variable is required")

genai.configure(api_key=GOOGLE_API_KEY)

# Initialize Gemini model
try:
    model = genai.GenerativeModel('gemini-2.5-flash')
    logger.info("Google Gemini API configured successfully")
except Exception as e:
    logger.error(f"Failed to initialize Gemini model: {str(e)}")
    raise


# ==================== Pydantic Models ====================
logger.info("Pydantic Models initialized.....")

class MealItems(BaseModel):
    """Model for meal items and calories"""
    items: List[str] = Field(..., description="List of food items for the meal")
    calories: int = Field(..., description="Total calories for the meal")


class Meals(BaseModel):
    """Model for all meals in a day"""
    breakfast: MealItems
    lunch: MealItems
    dinner: MealItems


class DailyPlan(BaseModel):
    """Model for daily diet plan"""
    total_calories: int = Field(..., description="Total daily calories")
    meals: Meals
    snacks: List[str] = Field(..., description="List of recommended snacks")


class DietPlanResponse(BaseModel):
    """Response model for diet plan generation"""
    daily_plan: DailyPlan


class FoodItem(BaseModel):
    """Model for individual food item with quantity"""
    item: str = Field(..., description="Name of the food item")
    quantity: str = Field(..., description="Quantity of the food item (e.g., '200 gms', '4 pieces')")


class MacroNutrients(BaseModel):
    """Model for macronutrients"""
    protein: float = Field(..., description="Protein in grams")
    carbs: float = Field(..., description="Carbohydrates in grams")
    fat: float = Field(..., description="Fat in grams")


class NutritionBreakdown(BaseModel):
    """Model for individual food nutritional breakdown"""
    item: str = Field(..., description="Food item with quantity")
    calories: int = Field(..., description="Calories")
    protein: float = Field(..., description="Protein in grams")
    carbs: float = Field(..., description="Carbohydrates in grams")
    fat: float = Field(..., description="Fat in grams")


class MealNutrition(BaseModel):
    """Model for complete meal nutrition"""
    total_calories: int = Field(..., description="Total calories")
    macros: MacroNutrients
    breakdown: List[NutritionBreakdown]


class NutritionBreakdownResponse(BaseModel):
    """Response model for nutrition breakdown"""
    meal_nutrition: MealNutrition


class DietPlanRequest(BaseModel):
    """Request model for diet plan generation"""
    name: str = Field(..., description="User's name")
    age: int = Field(..., description="User's age")
    goal: str = Field(..., description="Fitness goal (e.g., Weight Loss, Muscle Gain)")
    height: int = Field(..., description="Height in cm")
    current_weight: float = Field(..., description="Current weight in kg")
    target_weight: float = Field(..., description="Target weight in kg")
    health_conditions: List[str] = Field(default=[], description="List of health conditions")
    region: str = Field(..., description="Geographic region for cuisine")
    cuisine_preference: str = Field(..., description="Cuisine preference (e.g., Vegetarian, Non-Vegetarian)")
    allergies: List[str] = Field(default=[], description="List of allergies")


class NutritionRequest(BaseModel):
    """Request model for nutrition breakdown"""
    foods: List[FoodItem] = Field(..., description="List of food items with quantities")


# ==================== Helper Functions ====================

def construct_diet_plan_prompt(request: DietPlanRequest) -> str:
    """
    Construct a detailed prompt for Gemini to generate a personalized diet plan.
    
    Args:
        request: DietPlanRequest object containing user parameters
        
    Returns:
        Formatted prompt string for Gemini API
    """
    prompt = f"""You are a professional nutritionist and dietitian. Generate a personalized 7-day diet plan as a JSON object.

User Profile:
- Name: {request.name}
- Age: {request.age} years
- Goal: {request.goal}
- Height: {request.height} cm
- Current Weight: {request.current_weight} kg
- Target Weight: {request.target_weight} kg
- Health Conditions: {', '.join(request.health_conditions) if request.health_conditions else 'None'}
- Region: {request.region}
- Cuisine Preference: {request.cuisine_preference}
- Allergies: {', '.join(request.allergies) if request.allergies else 'None'}

Calculate appropriate daily calorie intake based on the user's goal and body metrics.

Requirements:
1. Generate a SINGLE representative daily plan (not 7 separate days)
2. Total daily calories should be appropriate for the user's goal
3. Include breakfast, lunch, and dinner with specific items
4. All food items must comply with cuisine preference and avoid allergens
5. Use regional cuisine from {request.region}
6. Consider health conditions when selecting foods
7. Include 2-3 healthy snacks

Output Format (valid JSON only, no markdown):
{{
  "daily_plan": {{
    "total_calories": <number>,
    "meals": {{
      "breakfast": {{
        "items": ["item1", "item2"],
        "calories": <number>
      }},
      "lunch": {{
        "items": ["item1", "item2", "item3"],
        "calories": <number>
      }},
      "dinner": {{
        "items": ["item1", "item2"],
        "calories": <number>
      }}
    }},
    "snacks": ["snack1", "snack2"]
  }}
}}

Important:
- Return ONLY valid JSON, no additional text or explanation
- Make the diet plan healthy, balanced, and appropriate for the goal
- Ensure item names are clear and specific"""

    return prompt


def construct_nutrition_prompt(request: NutritionRequest) -> str:
    """
    Construct a prompt for Gemini to analyze nutritional content of foods.
    
    Args:
        request: NutritionRequest object containing food items
        
    Returns:
        Formatted prompt string for Gemini API
    """
    foods_str = "\n".join([f"- {food.item}: {food.quantity}" for food in request.foods])
    
    prompt = f"""You are a professional nutritionist. Analyze the nutritional content of the following food items.

Food Items:
{foods_str}

Provide accurate nutritional breakdown including calories, protein, carbohydrates, and fats.

Output Format (valid JSON only, no markdown):
{{
  "meal_nutrition": {{
    "total_calories": <number>,
    "macros": {{
      "protein": <number in grams>,
      "carbs": <number in grams>,
      "fat": <number in grams>
    }},
    "breakdown": [
      {{
        "item": "<name> (<quantity>)",
        "calories": <number>,
        "protein": <number in grams>,
        "carbs": <number in grams>,
        "fat": <number in grams>
      }}
    ]
  }}
}}

Important:
- Return ONLY valid JSON, no additional text or explanation
- Provide realistic and accurate nutritional values
- Ensure breakdown matches individual food items"""

    return prompt


def parse_gemini_response(text: str) -> Dict[str, Any]:
    """
    Parse Gemini API response and extract JSON content.
    
    Args:
        text: Raw response text from Gemini
        
    Returns:
        Parsed JSON as dictionary
        
    Raises:
        ValueError: If JSON parsing fails
    """
    try:
        # Try to extract JSON from markdown code blocks if present
        if "```json" in text:
            start = text.find("```json") + 7
            end = text.find("```", start)
            text = text[start:end].strip()
        elif "```" in text:
            start = text.find("```") + 3
            end = text.find("```", start)
            text = text[start:end].strip()
        
        # Parse JSON
        return json.loads(text)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse Gemini response as JSON: {str(e)}")
        logger.error(f"Response content: {text[:500]}")
        raise ValueError(f"Failed to parse AI response: {str(e)}")


# ==================== API Endpoints ====================

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "AI Diet Plan & Nutrition API",
        "version": "1.0.0",
        "endpoints": {
            "/generate_diet_plan": "POST - Generate personalized diet plan",
            "/nutrition_breakdown": "POST - Analyze food nutrition",
            "/docs": "GET - API documentation"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "api_key_exists": bool(GOOGLE_API_KEY)}


@app.post("/generate_diet_plan", response_model=DietPlanResponse)
async def generate_diet_plan(request: DietPlanRequest):
    """
    Generate a personalized 7-day diet plan based on user parameters.
    
    Args:
        request: DietPlanRequest containing user information
        
    Returns:
        DietPlanResponse with generated diet plan
        
    Raises:
        HTTPException: If API call fails or response parsing fails
    """
    try:
        logger.info(f"Generating diet plan for user: {request.name}")
        
        # Construct prompt
        prompt = construct_diet_plan_prompt(request)
        
        # Call Gemini API
        logger.info("Calling Google Gemini API...")
        response = model.generate_content(prompt)
        
        # Parse response
        parsed_response = parse_gemini_response(response.text)
        logger.info("Parsed response: ", parsed_response)
        # Validate and structure response
        diet_plan_response = DietPlanResponse(**parsed_response)
        logger.info("Diet plan response: ", diet_plan_response.model_dump_json())
        logger.info("Diet plan generated successfully")
        return diet_plan_response
        
    except ValueError as e:
        logger.error(f"Error parsing response: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Error generating diet plan: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate diet plan: {str(e)}")


@app.post("/nutrition_breakdown", response_model=NutritionBreakdownResponse)
async def nutrition_breakdown(request: NutritionRequest):
    """
    Analyze nutritional content of food items.
    
    Args:
        request: NutritionRequest containing list of food items
        
    Returns:
        NutritionBreakdownResponse with nutritional analysis
        
    Raises:
        HTTPException: If API call fails or response parsing fails
    """
    try:
        logger.info(f"Analyzing nutrition for {len(request.foods)} food items")
        
        # Construct prompt
        prompt = construct_nutrition_prompt(request)
        
        # Call Gemini API
        logger.info("Calling Google Gemini API...")
        response = model.generate_content(prompt)
        
        # Parse response
        parsed_response = parse_gemini_response(response.text)
        
        # Validate and structure response
        nutrition_response = NutritionBreakdownResponse(**parsed_response)
        
        logger.info("Nutrition breakdown completed successfully")
        return nutrition_response
        
    except ValueError as e:
        logger.error(f"Error parsing response: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Error analyzing nutrition: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to analyze nutrition: {str(e)}")


# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

