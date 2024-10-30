/*
Copyright 2021 IBM All Rights Reserved.

SPDX-License-Identifier: Apache-2.0
*/

package main

import (
	"bytes"
	"context"
	"crypto/x509"
	"encoding/json"
	"errors"
	"fmt"
	"os"
	"path"
	"strings"
	"time"

	"github.com/hyperledger/fabric-gateway/pkg/client"
	"github.com/hyperledger/fabric-gateway/pkg/hash"
	"github.com/hyperledger/fabric-gateway/pkg/identity"
	"github.com/hyperledger/fabric-protos-go-apiv2/gateway"
	"google.golang.org/grpc"
	"google.golang.org/grpc/credentials"
	"google.golang.org/grpc/status"
)

const (
	mspID        = "Org1MSP"
	cryptoPath   = "C:/Users/Wigsicle/Desktop/Hyperledger" // Update to the new path
	certPath     = cryptoPath + "/Org1/signcerts"          // Adjusted for new path
	keyPath      = cryptoPath + "/Org1/keystore"           // Adjusted for new path
	tlsCertPath  = cryptoPath + "/Org1/ca.crt"             // Adjusted for new path
	peerEndpoint = "dns:///localhost:7051"
	gatewayPeer  = "peer0.org1.example.com"
)

var now = time.Now()
var assetId = fmt.Sprintf("asset%d", now.Unix()*1e3+int64(now.Nanosecond())/1e6)

func main() {
	// The gRPC client connection should be shared by all Gateway connections to this endpoint
	clientConnection := newGrpcConnection()
	defer clientConnection.Close()

	id := newIdentity()
	sign := newSign()

	// Create a Gateway connection for a specific client identity
	gw, err := client.Connect(
		id,
		client.WithSign(sign),
		client.WithHash(hash.SHA256),
		client.WithClientConnection(clientConnection),
		// Default timeouts for different gRPC calls
		client.WithEvaluateTimeout(5*time.Second),
		client.WithEndorseTimeout(15*time.Second),
		client.WithSubmitTimeout(5*time.Second),
		client.WithCommitStatusTimeout(1*time.Minute),
	)
	if err != nil {
		panic(err)
	}
	defer gw.Close()

	// Override default values for chaincode and channel name as they may differ in testing contexts.
	chaincodeName := "basic"
	if ccname := os.Getenv("CHAINCODE_NAME"); ccname != "" {
		chaincodeName = ccname
	}

	channelName := "mychannel"
	if cname := os.Getenv("CHANNEL_NAME"); cname != "" {
		channelName = cname
	}

	network := gw.GetNetwork(channelName)
	contract := network.GetContract(chaincodeName)

	initLedger(contract)
	// GetAlltickets(contract)
	// createticket(contract, "Bring Me The Horizon", "Cat 1", "Richard", "322")
	// readticketByID(contract, "ticket6")
	// readticketByID(contract, "ticket7")
	test, err := readticketByID(contract, "ticket6")
	fmt.Printf(test)
	// test2, err := readticketByID(contract, "ticket7")
	// fmt.Printf(test2)
	// // transferticketAsync(contract, "ticket6", "Joel")
	test3, err := transferticketAsync(contract, "ticket6", "Joel")
	fmt.Printf("\n%t\n", test3)
	// GetAlltickets(contract)
	// test4, err := transferticketAsync(contract, "ticket7", "Sam")
	// fmt.Printf("\n%t\n", test4)
	// exampleErrorHandling(contract)
	// deleteTicket(contract, "asset1729966479242")
	GetAlltickets(contract)
	test4, err := transferticketAsync(contract, "ticket6", "Jun Ye")
	fmt.Printf("\n%t\n", test4)
}

// newGrpcConnection creates a gRPC connection to the Gateway server.
func newGrpcConnection() *grpc.ClientConn {
	certificatePEM, err := os.ReadFile(tlsCertPath)
	if err != nil {
		panic(fmt.Errorf("failed to read TLS certifcate file: %w", err))
	}

	certificate, err := identity.CertificateFromPEM(certificatePEM)
	if err != nil {
		panic(err)
	}

	certPool := x509.NewCertPool()
	certPool.AddCert(certificate)
	transportCredentials := credentials.NewClientTLSFromCert(certPool, gatewayPeer)

	connection, err := grpc.NewClient(peerEndpoint, grpc.WithTransportCredentials(transportCredentials))
	if err != nil {
		panic(fmt.Errorf("failed to create gRPC connection: %w", err))
	}

	return connection
}

// newIdentity creates a client identity for this Gateway connection using an X.509 certificate.
func newIdentity() *identity.X509Identity {
	certificatePEM, err := readFirstFile(certPath)
	if err != nil {
		panic(fmt.Errorf("failed to read certificate file: %w", err))
	}

	certificate, err := identity.CertificateFromPEM(certificatePEM)
	if err != nil {
		panic(err)
	}

	id, err := identity.NewX509Identity(mspID, certificate)
	if err != nil {
		panic(err)
	}

	return id
}

// newSign creates a function that generates a digital signature from a message digest using a private key.
func newSign() identity.Sign {
	privateKeyPEM, err := readFirstFile(keyPath)
	if err != nil {
		panic(fmt.Errorf("failed to read private key file: %w", err))
	}

	privateKey, err := identity.PrivateKeyFromPEM(privateKeyPEM)
	if err != nil {
		panic(err)
	}

	sign, err := identity.NewPrivateKeySign(privateKey)
	if err != nil {
		panic(err)
	}

	return sign
}

func readFirstFile(dirPath string) ([]byte, error) {
	dir, err := os.Open(dirPath)
	if err != nil {
		return nil, err
	}

	fileNames, err := dir.Readdirnames(1)
	if err != nil {
		return nil, err
	}

	return os.ReadFile(path.Join(dirPath, fileNames[0]))
}

// This type of transaction would typically only be run once by an application the first time it was started after its
// initial deployment. A new version of the chaincode deployed later would likely not need to run an "init" function.
func initLedger(contract *client.Contract) {
	fmt.Printf("\n--> Submit Transaction: InitLedger, function creates the initial set of tickets on the ledger \n")

	_, err := contract.SubmitTransaction("InitLedger")
	if err != nil {
		panic(fmt.Errorf("failed to submit transaction: %w", err))
	}

	fmt.Printf("*** Transaction committed successfully\n")
}

// Evaluate a transaction to query ledger state.
func GetAlltickets(contract *client.Contract) {
	fmt.Println("\n--> Evaluate Transaction: GetAlltickets, function returns all the current assets on the ledger")

	evaluateResult, err := contract.EvaluateTransaction("GetAllTickets")
	if err != nil {
		panic(fmt.Errorf("failed to evaluate transaction: %w", err))
	}
	result := formatJSON(evaluateResult)

	fmt.Printf("*** Result:%s\n", result)
}

// Submit a transaction synchronously, blocking until it has been committed to the ledger.
func createticket(contract *client.Contract, eventName string, ticketCategory string, owner string, seatNumber string) {
	fmt.Printf("\n--> Submit Transaction: CreateTicket, creates new ticket with TicketID, EventName, TicketCategory, Owner and SeatNumber arguments \n")

	_, err := contract.SubmitTransaction("CreateTicket", assetId, eventName, ticketCategory, owner, seatNumber)
	if err != nil {
		panic(fmt.Errorf("failed to submit transaction: %w", err))
	}

	fmt.Printf("*** Transaction committed successfully\n")
}

// Evaluate a transaction by assetID to query ledger state.
func readticketByID(contract *client.Contract, ticketID string) (string, error) {
	fmt.Printf("\n--> Evaluate Transaction: ReadTicket, function returns ticket attributes\n")

	result, err := contract.EvaluateTransaction("ReadTicket", ticketID)
	if err != nil {
		if strings.Contains(err.Error(), "does not exist") {
			// fmt.Printf("Ticket with ID %s does not exist\n", ticketID)
			return "", nil
		} else {
			return "", fmt.Errorf("failed to evaluate transaction: %w", err)
		}
	}

	// fmt.Printf("*** Ticket details: %s\n", string(result))
	return string(result), nil
}

// Submit transaction asynchronously, blocking until the transaction has been sent to the orderer, and allowing
// this thread to process the chaincode response (e.g. update a UI) without waiting for the commit notification
func transferticketAsync(contract *client.Contract, ticketID string, newOwner string) (bool, error) {
	fmt.Printf("\n--> Async Submit Transaction: TransferTicket, updates existing ticket owner")

	submitResult, commit, err := contract.SubmitAsync("TransferTicket", client.WithArguments(ticketID, newOwner))
	if err != nil {
		fmt.Errorf("failed to submit transaction asynchronously: %w", err)
		return false, nil
	}

	fmt.Printf("\n*** Successfully submitted transaction to transfer ownership from %s to %s. \n", string(submitResult), newOwner)
	fmt.Println("*** Waiting for transaction commit.")

	if commitStatus, err := commit.Status(); err != nil {
		fmt.Errorf("failed to get commit status: %w", err)
	} else if !commitStatus.Successful {
		fmt.Errorf("transaction %s failed to commit with status: %d", commitStatus.TransactionID, int32(commitStatus.Code))
	}

	fmt.Printf("*** Transaction committed successfully\n")
	return true, nil
}

// Submit transaction, passing in the wrong number of arguments ,expected to throw an error containing details of any error responses from the smart contract.
func exampleErrorHandling(contract *client.Contract) {
	fmt.Println("\n--> Submit Transaction: UpdateTicket ticket70, ticket70 does not exist and should return an error")

	_, err := contract.SubmitTransaction("UpdateTicket", "ticket70", "blue", "CAT 12", "Tomoko", "H19")
	if err == nil {
		panic("******** FAILED to return an error")
	}

	fmt.Println("*** Successfully caught the error:")

	var endorseErr *client.EndorseError
	var submitErr *client.SubmitError
	var commitStatusErr *client.CommitStatusError
	var commitErr *client.CommitError

	if errors.As(err, &endorseErr) {
		fmt.Printf("Endorse error for transaction %s with gRPC status %v: %s\n", endorseErr.TransactionID, status.Code(endorseErr), endorseErr)
	} else if errors.As(err, &submitErr) {
		fmt.Printf("Submit error for transaction %s with gRPC status %v: %s\n", submitErr.TransactionID, status.Code(submitErr), submitErr)
	} else if errors.As(err, &commitStatusErr) {
		if errors.Is(err, context.DeadlineExceeded) {
			fmt.Printf("Timeout waiting for transaction %s commit status: %s", commitStatusErr.TransactionID, commitStatusErr)
		} else {
			fmt.Printf("Error obtaining commit status for transaction %s with gRPC status %v: %s\n", commitStatusErr.TransactionID, status.Code(commitStatusErr), commitStatusErr)
		}
	} else if errors.As(err, &commitErr) {
		fmt.Printf("Transaction %s failed to commit with status %d: %s\n", commitErr.TransactionID, int32(commitErr.Code), err)
	} else {
		panic(fmt.Errorf("unexpected error type %T: %w", err, err))
	}

	// Any error that originates from a peer or orderer node external to the gateway will have its details
	// embedded within the gRPC status error. The following code shows how to extract that.
	statusErr := status.Convert(err)

	details := statusErr.Details()
	if len(details) > 0 {
		fmt.Println("Error Details:")

		for _, detail := range details {
			switch detail := detail.(type) {
			case *gateway.ErrorDetail:
				fmt.Printf("- address: %s; mspId: %s; message: %s\n", detail.Address, detail.MspId, detail.Message)
			}
		}
	}
}

// Submit a transaction to delete a ticket by ID.
func deleteTicket(contract *client.Contract, ticketID string) {
	fmt.Printf("\n--> Submit Transaction: DeleteTicket, deletes a ticket by ID\n")

	// Here we use assetId; you may want to replace this with the ID of the ticket you want to delete.
	_, err := contract.SubmitTransaction("DeleteTicket", ticketID)
	if err != nil {
		panic(fmt.Errorf("failed to submit transaction: %w", err))
	}

	fmt.Printf("*** Transaction committed successfully\n")
}

// Format JSON data
func formatJSON(data []byte) string {
	var prettyJSON bytes.Buffer
	if err := json.Indent(&prettyJSON, data, "", "  "); err != nil {
		panic(fmt.Errorf("failed to parse JSON: %w", err))
	}
	return prettyJSON.String()
}
