import asyncio
import httpx
import json
import time
import sys

async def main():
    async with httpx.AsyncClient(timeout=30) as client:
        payload = {'question': 'Chào bạn, giải thích về luật lao động Việt Nam ngắn gọn.'}
        print('Sending Request...')
        start_time = time.time()
        async with client.stream('POST', 'http://127.0.0.1:8000/ai/chat', json=payload) as response:
            print(f'Status: {response.status_code} at {time.time()-start_time:.2f}s')
            async for chunk in response.aiter_text():
                for line in chunk.split('\n'):
                    if line.startswith('data: '):
                        data = line[6:]
                        if data == '[DONE]':
                            continue
                        try:
                            parsed = json.loads(data)
                            if 'text' in parsed:
                                # Just print the timestamp and the first char of the text to avoid unicode issues
                                sys.stdout.write(f'[{time.time()-start_time:.2f}s]*')
                                sys.stdout.flush()
                        except Exception:
                            pass
            print(f'\nFinished at {time.time()-start_time:.2f}s')
                
asyncio.run(main())
