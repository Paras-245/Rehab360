from ninja import NinjaAPI
from api.api import router as sensor_router  # Import the router

# Create the main API instance
api = NinjaAPI()

# Include the router, assigning a path prefix (optional)
api.add_router("/", sensor_router)