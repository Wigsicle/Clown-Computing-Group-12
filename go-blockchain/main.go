package main

import (
	"crypto/sha256"
	"encoding/hex"
	"fmt"
	"time"
)

// Ticket represents a concert ticket on the blockchain
type Ticket struct {
	ID    string
	Event string
	Venue string
	Date  string
	Seat  string
	Price float64
	Owner string
}

// Block represents a block on the blockchain
type Block struct {
	Index     int
	Timestamp string
	Ticket    Ticket
	Hash      string
	PrevHash  string
}

// Blockchain represents the full chain
var Blockchain []Block

// CalculateHash calculates a hash for a block using SHA256
func CalculateHash(block Block) string {
	record := fmt.Sprintf("%d%s%s%s%s%f%s%s", block.Index, block.Timestamp, block.Ticket.ID, block.Ticket.Owner, block.PrevHash, block.Ticket.Price, block.Ticket.Seat, block.Ticket.Event)
	h := sha256.New()
	h.Write([]byte(record))
	hashed := h.Sum(nil)
	return hex.EncodeToString(hashed)
}

// CreateBlock generates a new block with ticket information
func CreateBlock(prevBlock Block, ticket Ticket) Block {
	block := Block{
		Index:     prevBlock.Index + 1,
		Timestamp: time.Now().String(),
		Ticket:    ticket,
		PrevHash:  prevBlock.Hash,
	}
	block.Hash = CalculateHash(block)
	return block
}

// GenesisBlock creates the first block in the chain
func GenesisBlock() Block {
	ticket := Ticket{
		ID:    "0000",
		Event: "Genesis Event",
		Venue: "Origin Arena",
		Date:  time.Now().String(),
		Seat:  "0",
		Price: 0.0,
		Owner: "creator",
	}
	block := Block{
		Index:     0,
		Timestamp: time.Now().String(),
		Ticket:    ticket,
		PrevHash:  "0",
	}
	block.Hash = CalculateHash(block)
	return block
}

// TransferTicket changes ownership of a ticket and adds it to the blockchain
func TransferTicket(ticket Ticket, newOwner string) Block {
	ticket.Owner = newOwner
	prevBlock := Blockchain[len(Blockchain)-1]
	newBlock := CreateBlock(prevBlock, ticket)
	Blockchain = append(Blockchain, newBlock)
	return newBlock
}

func main() {
	// Initialize the blockchain with a genesis block
	genesisBlock := GenesisBlock()
	Blockchain = append(Blockchain, genesisBlock)

	// Create a ticket for a concert
	ticket1 := Ticket{
		ID:    "12345",
		Event: "Go Fest",
		Venue: "Go Arena",
		Date:  "2024-10-12",
		Seat:  "A12",
		Price: 150.50,
		Owner: "Alice",
	}

	// Add ticket to the blockchain
	block1 := CreateBlock(genesisBlock, ticket1)
	Blockchain = append(Blockchain, block1)

	fmt.Printf("Ticket created for: %s\n", ticket1.Event)
	fmt.Printf("Ticket owner: %s\n", ticket1.Owner)
	fmt.Printf("Ticket block hash: %s\n", block1.Hash)

	// Transfer the ticket to Bob
	fmt.Println("\nTransferring ticket to Bob...\n")
	block2 := TransferTicket(ticket1, "Bob")
	fmt.Printf("Ticket owner after transfer: %s\n", ticket1.Owner)
	fmt.Printf("New block hash: %s\n", block2.Hash)

	// Print the entire blockchain
	fmt.Println("\n--- Blockchain ---")
	for _, block := range Blockchain {
		fmt.Printf("\nIndex: %d\n", block.Index)
		fmt.Printf("Timestamp: %s\n", block.Timestamp)
		fmt.Printf("Event: %s\n", block.Ticket.Event)
		fmt.Printf("Owner: %s\n", block.Ticket.Owner)
		fmt.Printf("Hash: %s\n", block.Hash)
		fmt.Printf("PrevHash: %s\n", block.PrevHash)
	}
}
