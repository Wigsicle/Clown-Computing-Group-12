You will need docker and wsl2 to run this.
It does require the docker wsl2 integration

Once started you will need wsl, install Ubuntu-24.04
You will need to install jq and go

mkdir -p $HOME/go/src/github.com/<your_github_userid>
cd $HOME/go/src/github.com/<your_github_userid>

curl -sSLO https://raw.githubusercontent.com/hyperledger/fabric/main/scripts/install-fabric.sh && chmod +x install-fabric.sh

./install-fabric.sh d s b

cd go/src/Hyperledger/fabric-samples/test-network
./network.sh down
./network.sh up
./network.sh createChannel

- Deploy chaincode
cd fabric-samples/asset-transfer-basic/chaincode-go
GO111MODULE=on go mod vendor
cd ../../test-network
export PATH=${PWD}/../bin:$PATH
export FABRIC_CFG_PATH=$PWD/../config/
peer version
peer lifecycle chaincode package basic.tar.gz --path ../asset-transfer-basic/chaincode-go/ --lang golang --label basic_1.0

- Install chaincode package (Org1 peer)
export CORE_PEER_TLS_ENABLED=true
export CORE_PEER_LOCALMSPID="Org1MSP"
export CORE_PEER_TLS_ROOTCERT_FILE=${PWD}/organizations/peerOrganizations/org1.example.com/peers/peer0.org1.example.com/tls/ca.crt
export CORE_PEER_MSPCONFIGPATH=${PWD}/organizations/peerOrganizations/org1.example.com/users/Admin@org1.example.com/msp
export CORE_PEER_ADDRESS=localhost:7051

peer lifecycle chaincode install basic.tar.gz

- Install chaincode package (Org2 peer)
export CORE_PEER_LOCALMSPID="Org2MSP"
export CORE_PEER_TLS_ROOTCERT_FILE=${PWD}/organizations/peerOrganizations/org2.example.com/peers/peer0.org2.example.com/tls/ca.crt
export CORE_PEER_MSPCONFIGPATH=${PWD}/organizations/peerOrganizations/org2.example.com/users/Admin@org2.example.com/msp
export CORE_PEER_ADDRESS=localhost:9051

peer lifecycle chaincode install basic.tar.gz

- Approve a chaincode definition
peer lifecycle chaincode queryinstalled
Copy the basic_1.0............ until the comma

- Replace the basic_1.0..............................................
export CC_PACKAGE_ID=basic_1.0:d75ab1e7f780ec577095b5df2c43b4e3adda632e3cac6b2be8addd3a6a0bec00

peer lifecycle chaincode approveformyorg -o localhost:7050 --ordererTLSHostnameOverride orderer.example.com --channelID mychannel --name basic --version 1.0 --package-id $CC_PACKAGE_ID --sequence 1 --tls --cafile "${PWD}/organizations/ordererOrganizations/example.com/orderers/orderer.example.com/msp/tlscacerts/tlsca.example.com-cert.pem"

- Need to switch back to (Org1 peer)
export CORE_PEER_LOCALMSPID="Org1MSP"
export CORE_PEER_MSPCONFIGPATH=${PWD}/organizations/peerOrganizations/org1.example.com/users/Admin@org1.example.com/msp
export CORE_PEER_TLS_ROOTCERT_FILE=${PWD}/organizations/peerOrganizations/org1.example.com/peers/peer0.org1.example.com/tls/ca.crt
export CORE_PEER_ADDRESS=localhost:7051

peer lifecycle chaincode approveformyorg -o localhost:7050 --ordererTLSHostnameOverride orderer.example.com --channelID mychannel --name basic --version 1.0 --package-id $CC_PACKAGE_ID --sequence 1 --tls --cafile "${PWD}/organizations/ordererOrganizations/example.com/orderers/orderer.example.com/msp/tlscacerts/tlsca.example.com-cert.pem"

- Committing the chaincode definition to the channel
peer lifecycle chaincode checkcommitreadiness --channelID mychannel --name basic --version 1.0 --sequence 1 --tls --cafile "${PWD}/organizations/ordererOrganizations/example.com/orderers/orderer.example.com/msp/tlscacerts/tlsca.example.com-cert.pem" --output json

peer lifecycle chaincode commit -o localhost:7050 --ordererTLSHostnameOverride orderer.example.com --channelID mychannel --name basic --version 1.0 --sequence 1 --tls --cafile "${PWD}/organizations/ordererOrganizations/example.com/orderers/orderer.example.com/msp/tlscacerts/tlsca.example.com-cert.pem" --peerAddresses localhost:7051 --tlsRootCertFiles "${PWD}/organizations/peerOrganizations/org1.example.com/peers/peer0.org1.example.com/tls/ca.crt" --peerAddresses localhost:9051 --tlsRootCertFiles "${PWD}/organizations/peerOrganizations/org2.example.com/peers/peer0.org2.example.com/tls/ca.crt"

peer lifecycle chaincode querycommitted --channelID mychannel --name basic --cafile "${PWD}/organizations/ordererOrganizations/example.com/orderers/orderer.example.com/msp/tlscacerts/tlsca.example.com-cert.pem"

- Invoking the chaincode
peer chaincode invoke -o localhost:7050 --ordererTLSHostnameOverride orderer.example.com --tls --cafile "${PWD}/organizations/ordererOrganizations/example.com/orderers/orderer.example.com/msp/tlscacerts/tlsca.example.com-cert.pem" -C mychannel -n basic --peerAddresses localhost:7051 --tlsRootCertFiles "${PWD}/organizations/peerOrganizations/org1.example.com/peers/peer0.org1.example.com/tls/ca.crt" --peerAddresses localhost:9051 --tlsRootCertFiles "${PWD}/organizations/peerOrganizations/org2.example.com/peers/peer0.org2.example.com/tls/ca.crt" -c '{"function":"InitLedger","Args":[]}'

- Test getting all tickets
peer chaincode query -C mychannel -n basic -c '{"Args":["GetAllTickets"]}'

- Certs and shit for Org1
cd test-network/organizations/peerOrganizations/org1.example.com/users/User1@org1.example.com

- There are 3 things you'll need inside msp and tls
cd msp
cd keystore
cat priv_sk
copy the key and paste it inside the keystore folder

cd msp
cd signcerts
cat User1@org1.example.com-cert.pem
copy the key and paste it inside the signcerts folder

cd tls
cat ca.crt
copy the key and paste it in the folder

- Do the same for Org2

- How to run the Hyperledger fabric application (ticketTransfer.go)

You will need to install go
You will also need to have copied the certs over
Inside ticketTransfer.go 
const (
	mspID        = "Org1MSP"
	cryptoPath   = "C:/Users/Wigsicle/Desktop/Hyperledger" // Update to the new path
	certPath     = cryptoPath + "/Org1/signcerts"          // Adjusted for new path
	keyPath      = cryptoPath + "/Org1/keystore"           // Adjusted for new path
	tlsCertPath  = cryptoPath + "/Org1/ca.crt"             // Adjusted for new path
	peerEndpoint = "dns:///localhost:7051"
	gatewayPeer  = "peer0.org1.example.com"
)

Please change accordingly 

Org1MSP
localhost:7051
peer0.org1.example.com

Org2MSP
localhost:9051
peer0.org2.example.com

