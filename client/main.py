import asyncio
import grpc
import service_pb2
import service_pb2_grpc

# The key to the whole blog: The Service Config
SERVICE_CONFIG = '''{
    "loadBalancingConfig": [ { "round_robin": {} } ],
    "healthCheckConfig": { "serviceName": "" }
}'''

async def run():
    # In Docker Compose, 'server' resolves to multiple IPs if we scale it
    target = "dns:///server:50051"
    
    async with grpc.aio.insecure_channel(
        target,
        options=[
            ("grpc.service_config", SERVICE_CONFIG),
            ("grpc.lb_policy_name", "round_robin"),
        ]
    ) as channel:
        stub = service_pb2_grpc.SmartServiceStub(channel)
        
        print("Polling servers... watch the Server IDs change!")
        for i in range(20):
            try:
                response = await stub.CallMe(service_pb2.Empty())
                print(f"Request {i}: Handled by {response.server_id}")
            except Exception as e:
                print(f"Error: {e}")
            await asyncio.sleep(0.5)

if __name__ == "__main__":
    asyncio.run(run())
