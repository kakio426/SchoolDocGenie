
import asyncio
from main import perform_analysis

async def test():
    print("Testing perform_analysis...")
    try:
        content = "# Test Document\nThis is a test document."
        filename = "test.md"
        result = await perform_analysis(content, filename, save=False)
        print("Success:", result)
    except Exception as e:
        print("Failure:", e)
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test())
