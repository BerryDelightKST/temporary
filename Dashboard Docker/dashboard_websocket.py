import websockets
import asyncio
import json
import threading
import socket

WS_PORT = 8081

def update_config():
    with open("./dashboard/static/config.json", "w", encoding="utf-8") as f:
        server_ip = socket.gethostbyname(socket.gethostname())
        config = {
            "serverAddress": f"{server_ip}:{WS_PORT}"
        }
        f.write(json.dumps(config))


def create_socket():
    update_config()
    broadcast_thread = threading.Thread(target=start_async_loop)
    broadcast_thread.start()

connected_clients = set()


# dummy data

AT_data = [[1,10],[2,11],[3,12],[4,1],[5,5],[6,20],[7,35],[8,20]]
PH_data = [[1,2],[2,11],[3,12],[4,1],[5,5],[6,20],[7,35],[8,20]]
EC_data = [[1,3],[2,11],[3,12],[4,1],[5,5],[6,20],[7,35],[8,20]]
humidity_data = [[1,4],[2,11],[3,12],[4,1],[5,5],[6,20],[7,35],[8,20]]
light_data = [[1,10],[2,11],[3,12],[4,1],[5,5],[6,20],[7,35],[8,20]]
uv_light_source_data = [[1,10],[2,11],[3,12],[4,1],[5,5],[6,20],[7,35],[8,20]]
fan_data = [[1,10],[2,11],[3,12],[4,1],[5,5],[6,20],[7,35],[8,20]]
pump_data = [[1,10],[2,11],[3,12],[4,1],[5,5],[6,20],[7,35],[8,20]]


data = {
    "Ambient Temperature": AT_data,
    "pH Level": PH_data,
    "Electrical Conductivity": EC_data,
    "Humidity": humidity_data,
    "Light Level": light_data,
    "UV Light Source": uv_light_source_data,
    "Fan": fan_data,
    "Pump": pump_data
}


async def broadcast(data):
    if connected_clients:
        message = json.dumps(data)
        for client in connected_clients:
            await client.send(message)


# send data to all users every 5 seconds
async def broadcast_loop():
    while True:
        AT_data[0][1] += 1
        await broadcast(data)
        await asyncio.sleep(5)


async def handle_client(websocket, path):
    print(f'WS: {websocket.remote_address} connected')
    connected_clients.add(websocket)
    try:
        async for message in websocket:
            print(f'WS: Received message from client: {message}')

    finally:
        connected_clients.remove(websocket)


async def serve_websocket():
    websocket_server = await websockets.serve(handle_client, "0.0.0.0", WS_PORT)
    print(f'WS: Server started on ws://0.0.0.0:{WS_PORT}')
    await websocket_server.wait_closed() # run forever


# run websocket and broadcast on a loop
def start_async_loop():
    async def main():
        await asyncio.gather(
            broadcast_loop(),
            serve_websocket()
        )

    broadcast_event_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(broadcast_event_loop)
    broadcast_event_loop.run_until_complete(main())