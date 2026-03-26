print("1. Starting script...")
import sys
print(f"2. Python version: {sys.version}")

try:
    print("3. Importing fastapi...")
    from fastapi import FastAPI
    print("4. FastAPI imported successfully")
    
    print("5. Creating app...")
    app = FastAPI()
    print("6. App created")
    
    print("7. Starting server...")
    if __name__ == "__main__":
        import uvicorn
        print("8. Running uvicorn...")
        uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()