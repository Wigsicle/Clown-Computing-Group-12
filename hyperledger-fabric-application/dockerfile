# Use the official Go image as the build environment
FROM golang:1.22 AS builder

# Set the Current Working Directory inside the container
WORKDIR /app/hyperledger-fabric-application

# Copy the go.mod and go.sum files to the container
COPY ./hyperledger-fabric-application/go.* ./

# Download the Go modules
RUN go mod download

# Copy the source code into the container
COPY ./hyperledger-fabric-application /app/hyperledger-fabric-application

# Copy the certificate and keys into the image
COPY ./hyperledger-fabric-application/Org1/ca.crt /app/Org1/ca.crt
COPY ./hyperledger-fabric-application/Org1/signcerts/User1@org1.example.com-cert.pem /app/Org1/signcerts/User1@org1.example.com-cert.pem
COPY ./hyperledger-fabric-application/Org1/keystore/priv_sk /app/Org1/keystore/priv_sk

# Build the Go app and specify the full path for the output binary
RUN CGO_ENABLED=0 GOOS=linux go build -o ticketTransfer . && ls -l /app

# Verify binary existence
RUN ls -l /app/hyperledger-fabric-application

# Second stage: minimal image for running the application
FROM alpine:latest

# Set the Current Working Directory inside the container
WORKDIR /app/hyperledger-fabric-application

# Copy the binary from the builder stage
COPY --from=builder /app/hyperledger-fabric-application/ticketTransfer .

# Command to run the executable
CMD ["./ticketTransfer"]

# Expose the port if your app listens on a specific port (adjust as necessary)
EXPOSE 50051
