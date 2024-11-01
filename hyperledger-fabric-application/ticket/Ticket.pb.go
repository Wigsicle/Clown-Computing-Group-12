// Code generated by protoc-gen-go. DO NOT EDIT.
// versions:
// 	protoc-gen-go v1.35.1
// 	protoc        v5.28.3
// source: Ticket.proto

package ticket

import (
	protoreflect "google.golang.org/protobuf/reflect/protoreflect"
	protoimpl "google.golang.org/protobuf/runtime/protoimpl"
	reflect "reflect"
	sync "sync"
)

const (
	// Verify that this generated code is sufficiently up-to-date.
	_ = protoimpl.EnforceVersion(20 - protoimpl.MinVersion)
	// Verify that runtime/protoimpl is sufficiently up-to-date.
	_ = protoimpl.EnforceVersion(protoimpl.MaxVersion - 20)
)

type ReadTicketByIdRequest struct {
	state         protoimpl.MessageState
	sizeCache     protoimpl.SizeCache
	unknownFields protoimpl.UnknownFields

	TicketId string `protobuf:"bytes,1,opt,name=ticketId,proto3" json:"ticketId,omitempty"`
}

func (x *ReadTicketByIdRequest) Reset() {
	*x = ReadTicketByIdRequest{}
	mi := &file_Ticket_proto_msgTypes[0]
	ms := protoimpl.X.MessageStateOf(protoimpl.Pointer(x))
	ms.StoreMessageInfo(mi)
}

func (x *ReadTicketByIdRequest) String() string {
	return protoimpl.X.MessageStringOf(x)
}

func (*ReadTicketByIdRequest) ProtoMessage() {}

func (x *ReadTicketByIdRequest) ProtoReflect() protoreflect.Message {
	mi := &file_Ticket_proto_msgTypes[0]
	if x != nil {
		ms := protoimpl.X.MessageStateOf(protoimpl.Pointer(x))
		if ms.LoadMessageInfo() == nil {
			ms.StoreMessageInfo(mi)
		}
		return ms
	}
	return mi.MessageOf(x)
}

// Deprecated: Use ReadTicketByIdRequest.ProtoReflect.Descriptor instead.
func (*ReadTicketByIdRequest) Descriptor() ([]byte, []int) {
	return file_Ticket_proto_rawDescGZIP(), []int{0}
}

func (x *ReadTicketByIdRequest) GetTicketId() string {
	if x != nil {
		return x.TicketId
	}
	return ""
}

type TransferTicketRequest struct {
	state         protoimpl.MessageState
	sizeCache     protoimpl.SizeCache
	unknownFields protoimpl.UnknownFields

	TicketId string `protobuf:"bytes,1,opt,name=ticketId,proto3" json:"ticketId,omitempty"`
	NewOwner string `protobuf:"bytes,2,opt,name=newOwner,proto3" json:"newOwner,omitempty"`
}

func (x *TransferTicketRequest) Reset() {
	*x = TransferTicketRequest{}
	mi := &file_Ticket_proto_msgTypes[1]
	ms := protoimpl.X.MessageStateOf(protoimpl.Pointer(x))
	ms.StoreMessageInfo(mi)
}

func (x *TransferTicketRequest) String() string {
	return protoimpl.X.MessageStringOf(x)
}

func (*TransferTicketRequest) ProtoMessage() {}

func (x *TransferTicketRequest) ProtoReflect() protoreflect.Message {
	mi := &file_Ticket_proto_msgTypes[1]
	if x != nil {
		ms := protoimpl.X.MessageStateOf(protoimpl.Pointer(x))
		if ms.LoadMessageInfo() == nil {
			ms.StoreMessageInfo(mi)
		}
		return ms
	}
	return mi.MessageOf(x)
}

// Deprecated: Use TransferTicketRequest.ProtoReflect.Descriptor instead.
func (*TransferTicketRequest) Descriptor() ([]byte, []int) {
	return file_Ticket_proto_rawDescGZIP(), []int{1}
}

func (x *TransferTicketRequest) GetTicketId() string {
	if x != nil {
		return x.TicketId
	}
	return ""
}

func (x *TransferTicketRequest) GetNewOwner() string {
	if x != nil {
		return x.NewOwner
	}
	return ""
}

type ReadTicketByIdReply struct {
	state         protoimpl.MessageState
	sizeCache     protoimpl.SizeCache
	unknownFields protoimpl.UnknownFields

	TicketInfo string `protobuf:"bytes,1,opt,name=ticketInfo,proto3" json:"ticketInfo,omitempty"`
}

func (x *ReadTicketByIdReply) Reset() {
	*x = ReadTicketByIdReply{}
	mi := &file_Ticket_proto_msgTypes[2]
	ms := protoimpl.X.MessageStateOf(protoimpl.Pointer(x))
	ms.StoreMessageInfo(mi)
}

func (x *ReadTicketByIdReply) String() string {
	return protoimpl.X.MessageStringOf(x)
}

func (*ReadTicketByIdReply) ProtoMessage() {}

func (x *ReadTicketByIdReply) ProtoReflect() protoreflect.Message {
	mi := &file_Ticket_proto_msgTypes[2]
	if x != nil {
		ms := protoimpl.X.MessageStateOf(protoimpl.Pointer(x))
		if ms.LoadMessageInfo() == nil {
			ms.StoreMessageInfo(mi)
		}
		return ms
	}
	return mi.MessageOf(x)
}

// Deprecated: Use ReadTicketByIdReply.ProtoReflect.Descriptor instead.
func (*ReadTicketByIdReply) Descriptor() ([]byte, []int) {
	return file_Ticket_proto_rawDescGZIP(), []int{2}
}

func (x *ReadTicketByIdReply) GetTicketInfo() string {
	if x != nil {
		return x.TicketInfo
	}
	return ""
}

type TransferTicketReply struct {
	state         protoimpl.MessageState
	sizeCache     protoimpl.SizeCache
	unknownFields protoimpl.UnknownFields

	Success bool `protobuf:"varint,1,opt,name=success,proto3" json:"success,omitempty"`
}

func (x *TransferTicketReply) Reset() {
	*x = TransferTicketReply{}
	mi := &file_Ticket_proto_msgTypes[3]
	ms := protoimpl.X.MessageStateOf(protoimpl.Pointer(x))
	ms.StoreMessageInfo(mi)
}

func (x *TransferTicketReply) String() string {
	return protoimpl.X.MessageStringOf(x)
}

func (*TransferTicketReply) ProtoMessage() {}

func (x *TransferTicketReply) ProtoReflect() protoreflect.Message {
	mi := &file_Ticket_proto_msgTypes[3]
	if x != nil {
		ms := protoimpl.X.MessageStateOf(protoimpl.Pointer(x))
		if ms.LoadMessageInfo() == nil {
			ms.StoreMessageInfo(mi)
		}
		return ms
	}
	return mi.MessageOf(x)
}

// Deprecated: Use TransferTicketReply.ProtoReflect.Descriptor instead.
func (*TransferTicketReply) Descriptor() ([]byte, []int) {
	return file_Ticket_proto_rawDescGZIP(), []int{3}
}

func (x *TransferTicketReply) GetSuccess() bool {
	if x != nil {
		return x.Success
	}
	return false
}

var File_Ticket_proto protoreflect.FileDescriptor

var file_Ticket_proto_rawDesc = []byte{
	0x0a, 0x0c, 0x54, 0x69, 0x63, 0x6b, 0x65, 0x74, 0x2e, 0x70, 0x72, 0x6f, 0x74, 0x6f, 0x12, 0x06,
	0x74, 0x69, 0x63, 0x6b, 0x65, 0x74, 0x22, 0x33, 0x0a, 0x15, 0x52, 0x65, 0x61, 0x64, 0x54, 0x69,
	0x63, 0x6b, 0x65, 0x74, 0x42, 0x79, 0x49, 0x64, 0x52, 0x65, 0x71, 0x75, 0x65, 0x73, 0x74, 0x12,
	0x1a, 0x0a, 0x08, 0x74, 0x69, 0x63, 0x6b, 0x65, 0x74, 0x49, 0x64, 0x18, 0x01, 0x20, 0x01, 0x28,
	0x09, 0x52, 0x08, 0x74, 0x69, 0x63, 0x6b, 0x65, 0x74, 0x49, 0x64, 0x22, 0x4f, 0x0a, 0x15, 0x54,
	0x72, 0x61, 0x6e, 0x73, 0x66, 0x65, 0x72, 0x54, 0x69, 0x63, 0x6b, 0x65, 0x74, 0x52, 0x65, 0x71,
	0x75, 0x65, 0x73, 0x74, 0x12, 0x1a, 0x0a, 0x08, 0x74, 0x69, 0x63, 0x6b, 0x65, 0x74, 0x49, 0x64,
	0x18, 0x01, 0x20, 0x01, 0x28, 0x09, 0x52, 0x08, 0x74, 0x69, 0x63, 0x6b, 0x65, 0x74, 0x49, 0x64,
	0x12, 0x1a, 0x0a, 0x08, 0x6e, 0x65, 0x77, 0x4f, 0x77, 0x6e, 0x65, 0x72, 0x18, 0x02, 0x20, 0x01,
	0x28, 0x09, 0x52, 0x08, 0x6e, 0x65, 0x77, 0x4f, 0x77, 0x6e, 0x65, 0x72, 0x22, 0x35, 0x0a, 0x13,
	0x52, 0x65, 0x61, 0x64, 0x54, 0x69, 0x63, 0x6b, 0x65, 0x74, 0x42, 0x79, 0x49, 0x64, 0x52, 0x65,
	0x70, 0x6c, 0x79, 0x12, 0x1e, 0x0a, 0x0a, 0x74, 0x69, 0x63, 0x6b, 0x65, 0x74, 0x49, 0x6e, 0x66,
	0x6f, 0x18, 0x01, 0x20, 0x01, 0x28, 0x09, 0x52, 0x0a, 0x74, 0x69, 0x63, 0x6b, 0x65, 0x74, 0x49,
	0x6e, 0x66, 0x6f, 0x22, 0x2f, 0x0a, 0x13, 0x54, 0x72, 0x61, 0x6e, 0x73, 0x66, 0x65, 0x72, 0x54,
	0x69, 0x63, 0x6b, 0x65, 0x74, 0x52, 0x65, 0x70, 0x6c, 0x79, 0x12, 0x18, 0x0a, 0x07, 0x73, 0x75,
	0x63, 0x63, 0x65, 0x73, 0x73, 0x18, 0x01, 0x20, 0x01, 0x28, 0x08, 0x52, 0x07, 0x73, 0x75, 0x63,
	0x63, 0x65, 0x73, 0x73, 0x32, 0xa4, 0x01, 0x0a, 0x06, 0x54, 0x69, 0x63, 0x6b, 0x65, 0x74, 0x12,
	0x4c, 0x0a, 0x0e, 0x52, 0x65, 0x61, 0x64, 0x54, 0x69, 0x63, 0x6b, 0x65, 0x74, 0x42, 0x79, 0x49,
	0x64, 0x12, 0x1d, 0x2e, 0x74, 0x69, 0x63, 0x6b, 0x65, 0x74, 0x2e, 0x52, 0x65, 0x61, 0x64, 0x54,
	0x69, 0x63, 0x6b, 0x65, 0x74, 0x42, 0x79, 0x49, 0x64, 0x52, 0x65, 0x71, 0x75, 0x65, 0x73, 0x74,
	0x1a, 0x1b, 0x2e, 0x74, 0x69, 0x63, 0x6b, 0x65, 0x74, 0x2e, 0x52, 0x65, 0x61, 0x64, 0x54, 0x69,
	0x63, 0x6b, 0x65, 0x74, 0x42, 0x79, 0x49, 0x64, 0x52, 0x65, 0x70, 0x6c, 0x79, 0x12, 0x4c, 0x0a,
	0x0e, 0x54, 0x72, 0x61, 0x6e, 0x73, 0x66, 0x65, 0x72, 0x54, 0x69, 0x63, 0x6b, 0x65, 0x74, 0x12,
	0x1d, 0x2e, 0x74, 0x69, 0x63, 0x6b, 0x65, 0x74, 0x2e, 0x54, 0x72, 0x61, 0x6e, 0x73, 0x66, 0x65,
	0x72, 0x54, 0x69, 0x63, 0x6b, 0x65, 0x74, 0x52, 0x65, 0x71, 0x75, 0x65, 0x73, 0x74, 0x1a, 0x1b,
	0x2e, 0x74, 0x69, 0x63, 0x6b, 0x65, 0x74, 0x2e, 0x54, 0x72, 0x61, 0x6e, 0x73, 0x66, 0x65, 0x72,
	0x54, 0x69, 0x63, 0x6b, 0x65, 0x74, 0x52, 0x65, 0x70, 0x6c, 0x79, 0x42, 0x11, 0x5a, 0x0f, 0x2e,
	0x2f, 0x74, 0x69, 0x63, 0x6b, 0x65, 0x74, 0x3b, 0x74, 0x69, 0x63, 0x6b, 0x65, 0x74, 0x62, 0x06,
	0x70, 0x72, 0x6f, 0x74, 0x6f, 0x33,
}

var (
	file_Ticket_proto_rawDescOnce sync.Once
	file_Ticket_proto_rawDescData = file_Ticket_proto_rawDesc
)

func file_Ticket_proto_rawDescGZIP() []byte {
	file_Ticket_proto_rawDescOnce.Do(func() {
		file_Ticket_proto_rawDescData = protoimpl.X.CompressGZIP(file_Ticket_proto_rawDescData)
	})
	return file_Ticket_proto_rawDescData
}

var file_Ticket_proto_msgTypes = make([]protoimpl.MessageInfo, 4)
var file_Ticket_proto_goTypes = []any{
	(*ReadTicketByIdRequest)(nil), // 0: ticket.ReadTicketByIdRequest
	(*TransferTicketRequest)(nil), // 1: ticket.TransferTicketRequest
	(*ReadTicketByIdReply)(nil),   // 2: ticket.ReadTicketByIdReply
	(*TransferTicketReply)(nil),   // 3: ticket.TransferTicketReply
}
var file_Ticket_proto_depIdxs = []int32{
	0, // 0: ticket.Ticket.ReadTicketById:input_type -> ticket.ReadTicketByIdRequest
	1, // 1: ticket.Ticket.TransferTicket:input_type -> ticket.TransferTicketRequest
	2, // 2: ticket.Ticket.ReadTicketById:output_type -> ticket.ReadTicketByIdReply
	3, // 3: ticket.Ticket.TransferTicket:output_type -> ticket.TransferTicketReply
	2, // [2:4] is the sub-list for method output_type
	0, // [0:2] is the sub-list for method input_type
	0, // [0:0] is the sub-list for extension type_name
	0, // [0:0] is the sub-list for extension extendee
	0, // [0:0] is the sub-list for field type_name
}

func init() { file_Ticket_proto_init() }
func file_Ticket_proto_init() {
	if File_Ticket_proto != nil {
		return
	}
	type x struct{}
	out := protoimpl.TypeBuilder{
		File: protoimpl.DescBuilder{
			GoPackagePath: reflect.TypeOf(x{}).PkgPath(),
			RawDescriptor: file_Ticket_proto_rawDesc,
			NumEnums:      0,
			NumMessages:   4,
			NumExtensions: 0,
			NumServices:   1,
		},
		GoTypes:           file_Ticket_proto_goTypes,
		DependencyIndexes: file_Ticket_proto_depIdxs,
		MessageInfos:      file_Ticket_proto_msgTypes,
	}.Build()
	File_Ticket_proto = out.File
	file_Ticket_proto_rawDesc = nil
	file_Ticket_proto_goTypes = nil
	file_Ticket_proto_depIdxs = nil
}