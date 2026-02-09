import asyncio
import os
import uuid
import grpc
from grpc_health.v1 import health, health_pb2, health_pb2_grpc
import service_pb2
import service_pb2_grpc

class SmartServicer(service_pb2_grpc.SmartServiceServicer):
    def __init__(self):
        self.server_id = f"Pod-{os.getenv('HOSTNAME', uuid.uuid4().hex[:6])}"

    async def CallMe(self, request, context):
        print(f"Received request on {self.server_id}")
        return service_pb2.ServerInfo(server_id=self.server_id)

async def serve():
    server = grpc.aio.server(options=[
        ('grpc.max_connection_age_ms', 60000), # 1 minute churn
    ])
    
    # Add Business Logic
    service_pb2_grpc.add_SmartServiceServicer_to_server(SmartServicer(), server)
    
    # Add gRPC Health Checking
    health_servicer = health.HealthServicer()
    health_pb2_grpc.add_HealthServicer_to_server(health_servicer, server)
    health_servicer.set("", health_pb2.HealthCheckResponse.SERVING)
    
    server.add_insecure_port('[::]:50051')
    print(f"Starting server on port 50051")
    await server.start()
    await server.wait_for_termination()

if __name__ == "__main__":
    asyncio.run(serve())
