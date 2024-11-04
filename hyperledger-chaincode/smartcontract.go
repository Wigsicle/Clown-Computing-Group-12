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
	OwnerID        string `json:"OwnerID"`
	SeatNumber     string `json:"SeatNumber"`
	HashVal        string `json:"HashVal"`
}

// InitLedger adds a base set of tickets to the ledger
func (s *SmartContract) InitLedger(ctx contractapi.TransactionContextInterface) error {
	tickets := []ticket{
		{TicketID: "1", TicketCategory: "2", OwnerID: "2", EventName: "Jazz Night", SeatNumber: "24F", HashVal: "13c0330d81f175cc283d81414858cd4c8e66ff747cee538670cb85e06c7d9f4d"},
		{TicketID: "2", TicketCategory: "2", OwnerID: "3", EventName: "Pop Festival", SeatNumber: "33B", HashVal: "114bd151f8fb0c58642d2170da4ae7d7c57977260ac2cc8905306cab6b2acabc"},
		{TicketID: "3", TicketCategory: "VIP", OwnerID: "1", EventName: "Jazz Night", SeatNumber: "35C", HashVal: "da70dfa4d9f95ac979f921e8e623358236313f334afcd06cddf8a5621cf6a1e9"},
		{TicketID: "4", TicketCategory: "3", OwnerID: "1", EventName: "Rock Concert", SeatNumber: "40D", HashVal: "b3a8e0e1f9ab1bfe3a36f231f676f78bb30a519d2b21e6c530c0eee8ebb4a5d0"},
		{TicketID: "5", TicketCategory: "2", OwnerID: "4", EventName: "Pop Festival", SeatNumber: "77A", HashVal: "97a6d21df7c51e8289ac1a8c026aaac143e15aa1957f54f42e30d8f8a85c3a55"},
		{TicketID: "6", TicketCategory: "1", OwnerID: "3", EventName: "Pop Festival", SeatNumber: "93G", HashVal: "cebe3d9d614ba5c19f633566104315854a11353a333bf96f16b5afa0e90abdc4"},
		{TicketID: "7", TicketCategory: "2", OwnerID: "1", EventName: "Pop Festival", SeatNumber: "89Q", HashVal: "35a9e381b1a27567549b5f8a6f783c167ebf809f1c4d6a9e367240484d8ce281"},
		{TicketID: "8", TicketCategory: "2", OwnerID: "1", EventName: "Rock Concert", SeatNumber: "18I", HashVal: "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"},
		{TicketID: "9", TicketCategory: "2", OwnerID: "3", EventName: "Rock Concert", SeatNumber: "33C", HashVal: "a6b0f90d2ac2b8d1f250c687301aef132049e9016df936680e81fa7bc7d81d70"},
		{TicketID: "10", TicketCategory: "1", OwnerID: "5", EventName: "Jazz Night", SeatNumber: "47B", HashVal: "08a018a9549220d707e11c5c4fe94d8dd60825f010e71efaa91e5e784f364d7b"},
		{TicketID: "11", TicketCategory: "3", OwnerID: "3", EventName: "Jazz Night", SeatNumber: "55D", HashVal: "cb8379ac2098aa165029e3938a51da0bcecfc008fd6795f401178647f96c5b34"},
		{TicketID: "12", TicketCategory: "2", OwnerID: "5", EventName: "Jazz Night", SeatNumber: "23C", HashVal: "d4ffe8e9ee0b48eba716706123a7187f32eae3bdcb0e7763e41e533267bd8a53"},
		{TicketID: "13", TicketCategory: "Normal", OwnerID: "3", EventName: "Rock Concert", SeatNumber: "41C", HashVal: "36e0fd847d927d68475f32a94efff30812ee3ce87c7752973f4dd7476aa2e97e"},
		{TicketID: "14", TicketCategory: "Normal", OwnerID: "5", EventName: "Pop Festival", SeatNumber: "82B", HashVal: "50ae61e841fac4e8f9e40baf2ad36ec868922ea48368c18f9535e47db56dd7fb"},
		{TicketID: "15", TicketCategory: "2", OwnerID: "4", EventName: "Pop Festival", SeatNumber: "92E", HashVal: "722c8c993fd75a7627d69ed941344fe2a1423a3e75efd3e6778a142884227104"},
		{TicketID: "16", TicketCategory: "VIP", OwnerID: "5", EventName: "Jazz Night", SeatNumber: "64C", HashVal: "fcb1030a56a4b53d7297a4f8ee3088adf3b5b0771bc9490bdb64d2ec25d1e158"},
		{TicketID: "17", TicketCategory: "3", OwnerID: "4", EventName: "Jazz Night", SeatNumber: "73B", HashVal: "268f277c6d766d31334fda0f7a5533a185598d269e61c76a805870244828a5f1"},
		{TicketID: "18", TicketCategory: "1", OwnerID: "3", EventName: "Jazz Night", SeatNumber: "88B", HashVal: "15cb41f1adc95ad4f19386c0ad1be2fd2749d781380a5096b7004860ec2fa608"},
		{TicketID: "19", TicketCategory: "VIP", OwnerID: "2", EventName: "Jazz Night", SeatNumber: "12A", HashVal: "21b480da0f8977881b77fa1db5ad1a0587d01480d6ae99b5be2132598a0a60e9"},
		{TicketID: "20", TicketCategory: "1", OwnerID: "1", EventName: "Rock Concert", SeatNumber: "37C", HashVal: "cf63b8eb216845d24edd4b249b146957b42199cd12759647df90cb57525b4e90"},
		{TicketID: "21", TicketCategory: "2", OwnerID: "default", EventName: "Rock Concert", SeatNumber: "44D", HashVal: "2b8fbda969a8aaa908e763c57e6b22a1697b7c0c5f95fc35b95d492fcc54d082"},
		{TicketID: "22", TicketCategory: "4", OwnerID: "default", EventName: "Jazz Night", SeatNumber: "12E", HashVal: "57041cf4167df98d6cff07187471110e64c5ee782c8f64e31c464599c1a881a3"},
		{TicketID: "23", TicketCategory: "VIP", OwnerID: "default", EventName: "Rock Concert", SeatNumber: "244I", HashVal: "5a5a5eff214997248974e6fe5a7abd9433fe95899abba23e7c5dd7d8c8093044"},
		{TicketID: "24", TicketCategory: "3", OwnerID: "default", EventName: "Pop Festival", SeatNumber: "62E", HashVal: "0f336a037e1f61303d8f5a6f471140f38d995574e21f30e2cf38f4409e42a904"},
		{TicketID: "25", TicketCategory: "2", OwnerID: "default", EventName: "Jazz Night", SeatNumber: "85F", HashVal: "fadfef49b40bf551a279f820bd863ac96aebcbf39b4431dff4f0d5cb62dd5303"},
		{TicketID: "26", TicketCategory: "1", OwnerID: "default", EventName: "Rock Concert", SeatNumber: "92G", HashVal: "e32dd9bb5ec7cb608d54a405f0795421b7b5cd2d8d0d236e25cc08d9f05d54c8"},
		{TicketID: "27", TicketCategory: "Normal", OwnerID: "default", EventName: "Pop Festival", SeatNumber: "41D", HashVal: "4d53c751332b1add999c596731faa353bda10b2088bd78a0ef9c442f5d2839ba"},
		{TicketID: "28", TicketCategory: "4", OwnerID: "default", EventName: "Jazz Night", SeatNumber: "95F", HashVal: "2823b9b5bcb42ee813ba0656b87079fd0bae1792e992cb946a145460387c6564"},
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
func (s *SmartContract) CreateTicket(ctx contractapi.TransactionContextInterface, ticketId string, eventName string, ticketCategory string, ownerID string, seatNumber string) error {
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
		OwnerID:        ownerID,
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
func (s *SmartContract) UpdateTicket(ctx contractapi.TransactionContextInterface, ticketId string, eventName string, ticketCategory string, ownerID string, seatNumber string) error {
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
		OwnerID:        ownerID,
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
func (s *SmartContract) TransferTicket(ctx contractapi.TransactionContextInterface, ticketId string, newOwnerID string) (string, error) {
	ticket, err := s.ReadTicket(ctx, ticketId)
	if err != nil {
		return "", err
	}

	oldOwnerID := ticket.OwnerID
	ticket.OwnerID = newOwnerID

	ticketJSON, err := json.Marshal(ticket)
	if err != nil {
		return "", err
	}

	err = ctx.GetStub().PutState(ticketId, ticketJSON)
	if err != nil {
		return "", err
	}

	return oldOwnerID, nil
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
