# AI-Based Diet Plan Recommendation & Nutrition Breakdown API

A comprehensive FastAPI application that leverages Google Gemini AI to generate personalized diet plans and provide detailed nutritional analysis of food items.

## Features

-  **Personalized Diet Plan Generation**: Create custom 7-day diet plans based on user parameters
-  **Nutrition Analysis**: Get detailed nutritional breakdown including calories and macros
-  **AI-Powered**: Uses Google Gemini AI for intelligent meal planning and analysis
-  **Health-Aware**: Considers health conditions, allergies, and dietary preferences
-  **Regional Cuisine Support**: Generates plans based on regional food preferences

## Tech Stack

- **Python 3.11+**
- **FastAPI** - Modern, fast web framework
- **Google Gemini AI** - AI-powered meal planning and analysis
- **Pydantic** - Data validation
- **Uvicorn** - ASGI server

## Installation

### 1. Clone or Download the Project

```bash
cd "diet plain"
```

### 2. Create Virtual Environment

```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

Create a `.env` file in the project root:

```env
GOOGLE_API_KEY=your_google_gemini_api_key_here
```

**How to get your Google Gemini API Key:**
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Get API Key"
4. Create a new API key
5. Copy the key and paste it in your `.env` file

## Running the Application

### Start the Server

```bash
python app.py
```

Or using uvicorn directly:

```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

## API Endpoints

### 1. Generate Diet Plan

**Endpoint:** `POST /generate_diet_plan`

**Description:** Generates a personalized 7-day diet plan based on user parameters.

**Request Body:**
```json
{
  "name": "Arjun",
  "age": 30,
  "goal": "Weight Loss",
  "height": 175,
  "current_weight": 78,
  "target_weight": 70,
  "health_conditions": ["Diabetes", "High BP"],
  "region": "South India",
  "cuisine_preference": "Vegetarian",
  "allergies": ["Peanuts", "Milk"]
}
```

**Response:**
```json
{
  "daily_plan": {
    "total_calories": 1800,
    "meals": {
      "breakfast": {
        "items": ["Oats with banana", "Boiled eggs"],
        "calories": 380
      },
      "lunch": {
        "items": ["Brown rice", "Grilled chicken", "Steamed vegetables"],
        "calories": 650
      },
      "dinner": {
        "items": ["Chapathi", "Paneer curry"],
        "calories": 500
      }
    },
    "snacks": ["Green tea", "Almonds"]
  }
}
```

**Example cURL:**
```bash
curl -X POST "http://localhost:8000/generate_diet_plan" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Arjun",
    "age": 30,
    "goal": "Weight Loss",
    "height": 175,
    "current_weight": 78,
    "target_weight": 70,
    "health_conditions": ["Diabetes", "High BP"],
    "region": "South India",
    "cuisine_preference": "Vegetarian",
    "allergies": ["Peanuts", "Milk"]
  }'
```

### 2. Nutrition Breakdown

**Endpoint:** `POST /nutrition_breakdown`

**Description:** Analyzes nutritional content of food items.

**Request Body:**
```json
{
  "foods": [
    {"item": "Chapathi", "quantity": "4 pieces"},
    {"item": "Potato Kuruma", "quantity": "200 gms"}
  ]
}
```

**Response:**
```json
{
  "meal_nutrition": {
    "total_calories": 560,
    "macros": {
      "protein": 18.5,
      "carbs": 75.3,
      "fat": 15.4
    },
    "breakdown": [
      {
        "item": "Chapathi (4 pieces)",
        "calories": 320,
        "protein": 10,
        "carbs": 60,
        "fat": 5
      },
      {
        "item": "Potato Kuruma (200 gms)",
        "calories": 240,
        "protein": 8.5,
        "carbs": 15.3,
        "fat": 10.4
      }
    ]
  }
}
```

**Example cURL:**
```bash
curl -X POST "http://localhost:8000/nutrition_breakdown" \
  -H "Content-Type: application/json" \
  -d '{
    "foods": [
      {"item": "Chapathi", "quantity": "4 pieces"},
      {"item": "Potato Kuruma", "quantity": "200 gms"}
    ]
  }'
```

### Other Endpoints

- `GET /` - Root endpoint with API information
- `GET /health` - Health check endpoint


## Error Handling

The API includes comprehensive error handling:
- **400 Bad Request**: Invalid input data
- **500 Internal Server Error**: API failures or parsing errors
- All errors return JSON with detailed error messages

## Requirements

### Mandatory Parameters

**For Diet Plan:**
- `name`, `age`, `goal`, `height`, `current_weight`, `target_weight`, `region`, `cuisine_preference`

**For Nutrition Breakdown:**
- `foods` (list of food items)

### Optional Parameters

- `health_conditions` (empty list if none)
- `allergies` (empty list if none)

## Tips

1. **Be Specific with Quantities**: Use clear quantities like "200 gms", "4 pieces", "1 cup"
2. **Health Conditions**: List all relevant conditions for personalized recommendations
3. **Regional Cuisine**: Specify the region for culturally appropriate meal suggestions
4. **Allergies**: Always list allergies to avoid unsafe recommendations



---


