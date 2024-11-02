import grpc
import Ticket_pb2  # Import the generated message classes
import Ticket_pb2_grpc  # Import the generated gRPC classes

def run():
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = Ticket_pb2_grpc.TicketStub(channel)  # Create a stub for the Ticket service

        # Example: Read Ticket by ID
        ticket_id = "ticket4"  # Replace with the desired ticket ID
        read_ticket_request = Ticket_pb2.ReadTicketByIdRequest(ticketId=ticket_id)
        
        try:
            response = stub.ReadTicketById(read_ticket_request)
            print(f"Ticket Info for ID {ticket_id}: {response.ticketInfo}")
        except grpc.RpcError as e:
            print(f"RPC failed with status code {e.code()}: {e.details()}")
    
        # Example: Transfer Ticket
        ticket_id_to_transfer = "ticket4"  # Replace with the ticket ID to transfer
        new_owner = "Jake"  # Replace with the new owner's identifier
        transfer_ticket_request = Ticket_pb2.TransferTicketRequest(ticketId=ticket_id_to_transfer, newOwner=new_owner)

        try:
            transfer_response = stub.TransferTicket(transfer_ticket_request)
            print(f"Transfer Ticket Success: {transfer_response.success}")
        except grpc.RpcError as e:
            print(f"Transfer RPC failed with status code {e.code()}: {e.details()}")
            return  # Exit if the transfer fails

        # Example: Read the Ticket again after Transfer
        try:
            # Read the ticket again to see if the transfer was successful
            read_ticket2 = Ticket_pb2.ReadTicketByIdRequest(ticketId=ticket_id_to_transfer)
            response_after_transfer = stub.ReadTicketById(read_ticket2)
            print(f"Updated Ticket Info for ID {read_ticket2}: {response_after_transfer.ticketInfo}")
        except grpc.RpcError as e:
            print(f"RPC failed with status code {e.code()}: {e.details()}")

if __name__ == "__main__":
    run()
