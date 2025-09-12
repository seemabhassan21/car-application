from .tools import (
    create_car,
    get_car_by_id,
    list_cars,
    update_car,
    delete_car,
    search_cars,
)

TOOLS_DEFINITION = [
    {
        "name": "create_car",
        "description": "Create a new car entry with make, model, and year. Returns the created car details.",
        "input_schema": {
            "type": "object",
            "properties": {
                "make_name": {"type": "string", "description": "The manufacturer name (e.g., Toyota, BMW, Ford)."},
                "model_name": {"type": "string", "description": "The specific model name (e.g., Camry, X5, Mustang)."},
                "year": {"type": "integer", "description": "The manufacturing year (e.g., 2020, 2019)."},
            },
            "required": ["make_name", "model_name", "year"],
        },
        "function": create_car,
    },
    {
        "name": "get_car",
        "description": "Retrieve a specific car by its unique ID. Optionally specify which fields to return.",
        "input_schema": {
            "type": "object",
            "properties": {
                "car_id": {"type": "string", "description": "The unique identifier of the car."},
                "fields": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Optional list of fields to include (make, model, year, car)."
                },
            },
            "required": ["car_id"],
        },
        "function": get_car_by_id,
    },
    {
        "name": "list_cars",
        "description": "Search and list cars with optional filters. Use limit=None to get all results. Returns complete car information including make, model, and year.",
        "input_schema": {
            "type": "object",
            "properties": {
                "make_name": {"type": "string", "description": "Filter by manufacturer (e.g., Toyota, BMW)."},
                "model_name": {"type": "string", "description": "Filter by model name (e.g., Camry, Corolla)."},
                "year": {"type": "integer", "description": "Filter by specific year (e.g., 2020, 2019)."},
                "limit": {"type": "integer", "description": "Maximum number of results. Omit or use null to get all matching cars."},
                "offset": {"type": "integer", "description": "Number of results to skip for pagination. Defaults to 0."},
            },
            "required": [],
        },
        "function": list_cars,
    },
    {
        "name": "update_car",
        "description": "Update existing car details. Can modify year, make, or model. Returns the updated car information.",
        "input_schema": {
            "type": "object",
            "properties": {
                "car_id": {"type": "string", "description": "The unique ID of the car to update."},
                "make_name": {"type": "string", "description": "New manufacturer name (optional)."},
                "model_name": {"type": "string", "description": "New model name (optional)."},
                "year": {"type": "integer", "description": "New manufacturing year (optional)."},
            },
            "required": ["car_id"],
        },
        "function": update_car,
    },
    {
        "name": "delete_car",
        "description": "Permanently remove a car from the database by its ID. Returns confirmation of deletion.",
        "input_schema": {
            "type": "object",
            "properties": {
                "car_id": {"type": "string", "description": "The unique ID of the car to delete."},
            },
            "required": ["car_id"],
        },
        "function": delete_car,
    },
    {
        "name": "search_cars",
        "description": "Advanced search with filter dictionary. Use limit=None for all results. Returns filtered car listings.",
        "input_schema": {
            "type": "object",
            "properties": {
                "filters": {"type": "object", "description": "Filter criteria: {'make_name': 'Toyota', 'year': 2020}"},
                "fields": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Optional fields to include in results."
                },
                "limit": {"type": "integer", "description": "Maximum results. Omit for all matches."},
                "offset": {"type": "integer", "description": "Pagination offset. Default 0."},
            },
            "required": ["filters"],
        },
        "function": search_cars,
    },
]
