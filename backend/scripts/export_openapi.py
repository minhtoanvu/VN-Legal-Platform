import json
import sys
import os

# Add backend directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app
from fastapi.openapi.utils import get_openapi

def export():
    openapi_schema = get_openapi(
        title="VN-Legal-Platform API",
        version="1.0.0",
        openapi_version=app.openapi_version,
        description="API Documentation for VN-Legal-Platform (QA Portfolio)",
        routes=app.routes,
    )
    
    # Export to the root of the project for easy access
    export_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "openapi.json")
    
    with open(export_path, "w", encoding="utf-8") as f:
        json.dump(openapi_schema, f, ensure_ascii=False, indent=2)
        
    print(f"✅ Successfully exported OpenAPI schema to: {export_path}")
    print("👉 You can now import this file directly into Postman!")

if __name__ == "__main__":
    export()
