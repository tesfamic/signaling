import asyncio
import json
import os
from aiohttp import web

async def handle_post(request):
    try:
        data = await request.json()
        target_id = data.get('target')
        message = data.get('message')
        client_id = request.query.get('clientId', '')
        room_id = request.query.get('room', 'default')

        if not target_id or message is None or not client_id:
            return web.json_response({'status': 'error', 'message': 'Missing parameters'}, status=400)

        message_dir = f'messages/{room_id}'
        os.makedirs(message_dir, exist_ok=True)
        message_path = os.path.join(message_dir, f'{target_id}.json')

        message_data = {
            'sender': client_id,
            'message': message,
            'timestamp': asyncio.get_event_loop().time()
        }

        with open(message_path, 'w') as f:
            json.dump(message_data, f)

        return web.json_response({'status': 'success'})
    except json.JSONDecodeError:
        return web.json_response({'status': 'error', 'message': 'Invalid JSON'}, status=400)
    except Exception as e:
        return web.json_response({'status': 'error', 'message': str(e)}, status=500)

async def handle_get(request):
    client_id = request.query.get('clientId', '')
    room_id = request.query.get('room', 'default')

    if not client_id:
        return web.json_response({'status': 'error', 'message': 'Missing clientId'}, status=400)

    message_dir = f'messages/{room_id}'
    message_path = os.path.join(message_dir, f'{client_id}.json')

    if os.path.exists(message_path):
        try:
            with open(message_path, 'r') as f:
                content = f.read()
            os.remove(message_path)
            return web.Response(text=content, content_type='application/json')
        except Exception as e:
            return web.json_response({'status': 'error', 'message': str(e)}, status=500)
    else:
        return web.json_response({'status': 'no_message'})

async def handle_options(request):
    return web.Response(status=204, headers={
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
    })

async def main():
    app = web.Application()
    app.add_routes([
        web.post('/signaling', handle_post),
        web.get('/signaling', handle_get),
        web.options('/signaling', handle_options),
    ])
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '216.24.60.0', 10000) # Replace with your desired IP and port
    await site.start()
    print("Signaling server started ")#at http://your_server_ip:8080/signaling")
    await asyncio.Future()  # Keep the server running

if __name__ == "__main__":
    asyncio.run(main())
