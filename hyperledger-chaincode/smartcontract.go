package chaincode

import (
	"encoding/json"
	"fmt"

	"github.com/hyperledger/fabric-contract-api-go/v2/contractapi"
)

// SmartContract provides functions for managing an ticket
type SmartContract struct {
	contractapi.Contract
}

// ticket describes basic details of what makes up a simple ticket
// Insert struct field in alphabetic order => to achieve determinism across languages
// golang keeps the order when marshal to json but doesn't order automatically
type ticket struct {
	TicketID       string `json:"TicketID"`
	EventName      string `json:"EventName"`
	TicketCategory string `json:"TicketCategory"`
	Owner          string `json:"Owner"`
	SeatNumber     string `json:"SeatNumber"`
}

// InitLedger adds a base set of tickets to the ledger
func (s *SmartContract) InitLedger(ctx contractapi.TransactionContextInterface) error {
	tickets := []ticket{
		{TicketID: "ticket1", EventName: "Taylor Swift Eras Tour", TicketCategory: "Cat 1", Owner: "Default", SeatNumber: "12A"},
		{TicketID: "ticket2", EventName: "Taylor Swift Eras Tour", TicketCategory: "Cat 2", Owner: "Default", SeatNumber: "12B"},
		{TicketID: "ticket3", EventName: "Taylor Swift Eras Tour", TicketCategory: "VIP", Owner: "Default", SeatNumber: "12C"},
		{TicketID: "ticket4", EventName: "Taylor Swift Eras Tour", TicketCategory: "CAT 3", Owner: "Default", SeatNumber: "12D"},
		{TicketID: "ticket5", EventName: "Taylor Swift Eras Tour", TicketCategory: "CAT 4", Owner: "Default", SeatNumber: "12E"},
		{TicketID: "ticket6", EventName: "Taylor Swift Eras Tour", TicketCategory: "VIP", Owner: "Default", SeatNumber: "12F"},
	}

	for _, ticket := range tickets {
		ticketJSON, err := json.Marshal(ticket)
		if err != nil {
			return err
		}

		err = ctx.GetStub().PutState(ticket.TicketID, ticketJSON)
		if err != nil {
			return fmt.Errorf("failed to put to world state. %v", err)
		}
	}

	return nil
}

// CreateTicket issues a new ticket to the world state with given details.
func (s *SmartContract) CreateTicket(ctx contractapi.TransactionContextInterface, ticketId string, eventName string, ticketCategory string, owner string, seatNumber string) error {
	exists, err := s.TicketExists(ctx, ticketId)
	if err != nil {
		return err
	}
	if exists {
		return fmt.Errorf("the ticket %s already exists", ticketId)
	}

	ticket := ticket{
		TicketID:       ticketId,
		EventName:      eventName,
		TicketCategory: ticketCategory,
		Owner:          owner,
		SeatNumber:     seatNumber,
	}
	ticketJSON, err := json.Marshal(ticket)
	if err != nil {
		return err
	}

	return ctx.GetStub().PutState(ticketId, ticketJSON)
}

// ReadTicket returns the ticket stored in the world state with given id.
func (s *SmartContract) ReadTicket(ctx contractapi.TransactionContextInterface, ticketId string) (*ticket, error) {
	ticketJSON, err := ctx.GetStub().GetState(ticketId)
	if err != nil {
		return nil, fmt.Errorf("failed to read from world state: %v", err)
	}
	if ticketJSON == nil {
		return nil, fmt.Errorf("the ticket %s does not exist", ticketId)
	}

	var ticket ticket
	err = json.Unmarshal(ticketJSON, &ticket)
	if err != nil {
		return nil, err
	}

	return &ticket, nil
}

// UpdateTicket updates an existing ticket in the world state with provided parameters.
func (s *SmartContract) UpdateTicket(ctx contractapi.TransactionContextInterface, ticketId string, eventName string, ticketCategory string, owner string, seatNumber string) error {
	exists, err := s.TicketExists(ctx, ticketId)
	if err != nil {
		return err
	}
	if !exists {
		return fmt.Errorf("the ticket %s does not exist", ticketId)
	}

	// overwriting original ticket with new ticket
	ticket := ticket{
		TicketID:       ticketId,
		EventName:      eventName,
		TicketCategory: ticketCategory,
		Owner:          owner,
		SeatNumber:     seatNumber,
	}
	ticketJSON, err := json.Marshal(ticket)
	if err != nil {
		return err
	}

	return ctx.GetStub().PutState(ticketId, ticketJSON)
}

// DeleteTicket deletes an given ticket from the world state.
func (s *SmartContract) DeleteTicket(ctx contractapi.TransactionContextInterface, ticketId string) error {
	exists, err := s.TicketExists(ctx, ticketId)
	if err != nil {
		return err
	}
	if !exists {
		return fmt.Errorf("the ticket %s does not exist", ticketId)
	}

	return ctx.GetStub().DelState(ticketId)
}

// TicketExists returns true when ticket with given ID exists in world state
func (s *SmartContract) TicketExists(ctx contractapi.TransactionContextInterface, ticketId string) (bool, error) {
	ticketJSON, err := ctx.GetStub().GetState(ticketId)
	if err != nil {
		return false, fmt.Errorf("failed to read from world state: %v", err)
	}

	return ticketJSON != nil, nil
}

// TransferTicket updates the owner field of ticket with given id in world state, and returns the old owner.
func (s *SmartContract) TransferTicket(ctx contractapi.TransactionContextInterface, ticketId string, newOwner string) (string, error) {
	ticket, err := s.ReadTicket(ctx, ticketId)
	if err != nil {
		return "", err
	}

	oldOwner := ticket.Owner
	ticket.Owner = newOwner

	ticketJSON, err := json.Marshal(ticket)
	if err != nil {
		return "", err
	}

	err = ctx.GetStub().PutState(ticketId, ticketJSON)
	if err != nil {
		return "", err
	}

	return oldOwner, nil
}

// GetAllTickets returns all tickets found in world state
func (s *SmartContract) GetAllTickets(ctx contractapi.TransactionContextInterface) ([]*ticket, error) {
	// range query with empty string for startKey and endKey does an
	// open-ended query of all tickets in the chaincode namespace.
	resultsIterator, err := ctx.GetStub().GetStateByRange("", "")
	if err != nil {
		return nil, err
	}
	defer resultsIterator.Close()

	var tickets []*ticket
	for resultsIterator.HasNext() {
		queryResponse, err := resultsIterator.Next()
		if err != nil {
			return nil, err
		}

		var ticket ticket
		err = json.Unmarshal(queryResponse.Value, &ticket)
		if err != nil {
			return nil, err
		}
		tickets = append(tickets, &ticket)
	}

	return tickets, nil
}
