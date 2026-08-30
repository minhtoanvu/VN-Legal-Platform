import sys
import traceback

def main():
    try:
        from app.routers import contract
        print("Import SUCCESS!")
    except Exception as e:
        print("Import FAILED!")
        traceback.print_exc()

if __name__ == "__main__":
    main()
