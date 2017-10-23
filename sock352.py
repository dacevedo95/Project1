# the CS 352 socket library

import binascii
import socket as syssock
import struct
import sys
import random

udpSocket = (0,0)

transmitter = -1
receiver = -1

sequenceNumber = 0

otherHostAddress = ""
sequenceNumber = 0
sock352PktHdrData = "!8BLLBB"

version = 0x1
opt_ptr = 0x0
protocol = 0x0
checksum = 0x0
source_port = 0x0
dest_port = 0x0
window = 0x0
header_len = 18
deliveredData = ""


def init(UDPportTx,UDPportRx):

    global udpSocket
    udpSocket = syssock.socket(syssock.AF_INET, syssock.SOCK_DGRAM)

    global receiver
    receiver = int(UDPportRx)

    # Needs fixing to account for 0
    global transmitter
    if(UDPportTx == ''):
        transmitter = receiver
    else:
        transmitter = int(UDPportTx)

    udpSocket.bind(('', receiver))
    udpSocket.settimeout(0.2)

    print('----------------------')
    print('UDP Socket Initialized')
    print('----------------------')

    return

class socket:

    def __init__(self):
        print("Init 352 socket")
        print('----------------------')
        return

    def bind(self, address):
        print("Binding")
        print('----------------------')
        return

    def connect(self, address):

        print("Initiating a conection on %s" % (transmitter))
        print('----------------------')

        global sequenceNumber
        sequenceNumber = int(random.randint(20, 100))

        header = self.__make_header(0x01, sequenceNumber, 0, 0)
        ackFlag = -1

        while(ackFlag != sequenceNumber):
            print("Requesting new connection. %d bytes sent!" % (udpSocket.sendto(header, (address[0], transmitter))))
            print('----------------------')

            newHeader = self.__sock352_get_packet()
            ackFlag = newHeader[9]

        global udpSocket
        udpSocket.connect( (address[0], transmitter))

        sequenceNumber += 1
        return

    def accept(self):

        global receiver
        print("Waiting for connection on %s" % (receiver))
        print("----------------------\n")

        flag = -1
        newHeader = ""

        while(flag != 0x01):
            newHeader = self.__sock352_get_packet()
            flag = newHeader[1]

        global sequenceNumber
        sequenceNumber = newHeader[8]

        header = self.__make_header(0x04,0,sequenceNumber,13)

        global udpSocket
        udpSocket.sendto(header+"I accept you.", otherHostAddress)

        sequenceNumber += 1

        print("\n----------------------")
        print("Connection Established")
        print("----------------------")

        clientsocket = socket()
        return (clientsocket,otherHostAddress)

    def close(self):

        print("\n----------------------")
        print("Closing the connection")
        print("----------------------")

        terimanalNumber = random.randint(7,19)
        header = self.__make_header(0x02, terimanalNumber, 0, 0)
        ackFlag = -1

        while(ackFlag != terimanalNumber):
            try:
                udpSocket.sendto(header, otherHostAddress)
            except TypeError:
                udpSocket.send(header)
            newHeader = self.__sock352_get_packet()
            ackFlag = newHeader[9]

        udpSocket.close()
        return

    def listen(self,buffer): #null code for part 1
        print("Listining")
        print('----------------------')
        return

    def send(self,buffer):

        bytesSent = 0
        msglen = len(buffer)

        print("Starting to send")
        while(msglen > 0):
            parcel = buffer[:255]
            parcelHeader = self.__make_header(0x03,sequenceNumber,0,len(parcel) )
            tempBytesSent = 0
            ackFlag = -1

            global udpSocket
            global sequenceNumber
            global header_len

            while(ackFlag != sequenceNumber):
                tempBytesSent = udpSocket.send(parcelHeader+parcel) - header_len

                newHeader = self.__sock352_get_packet()
                ackFlag = newHeader[9]

            msglen -= 255
            buffer = buffer[255:]
            bytesSent += tempBytesSent
            sequenceNumber += 1

        print("Segment sent: size = %d bytes" % bytesSent)
        print('----------------------')
        return bytesSent

    def recv(self,bytes_to_receive):
        print("Recieving requested amount\n")

        global deliveredData
        deliveredData = ""

        fullMessage = ""

        while(bytes_to_receive > 0):
            seq_no = -1

            global sequenceNumber
            while(seq_no != sequenceNumber):
                newHeader = self.__sock352_get_packet()
                seq_no = newHeader[8]
                print("\tReceived sequence number %d" % seq_no)
                if(seq_no != sequenceNumber):
                    print("\tWe expected the sequence number %d, but didn't get it!" % sequenceNumber)

                header = self.__make_header(0x04, 0,seq_no,0)

                global udpSocket
                udpSocket.sendto(header, otherHostAddress)

            fullMessage += deliveredData
            bytes_to_receive -= len(deliveredData)

            sequenceNumber += 1
        print("\nFinished receiving the requested amount!")
        """
        print("test")
        """
        print('----------------------')
        return fullMessage

    def  __sock352_get_packet(self):
        global udpSocket, sock352PktHdrData, otherHostAddress, deliveredData

        # Wait 0.2 seconds to receive a packet, otherwise return an empty header
        try:
            (data, senderAddress) = udpSocket.recvfrom(4096)
        except syssock.timeout:
            print("No packets received before the timeout!")
            z = [0,0,0,0,0,0,0,0,0,0,0,0]
            return z

        (data_header, data_msg) = (data[:18],data[18:])
        header = struct.unpack(sock352PktHdrData, data_header)
        flag = header[1]

        if(flag == 0x01):
            otherHostAddress = senderAddress
            return header
        elif(flag == 0x02):
            terminalHeader = self.__make_header(0x04,0,header[8],0)
            udpSocket.sendto(terminalHeader, senderAddress)
            return header
        elif(flag == 0x03):
            deliveredData = data_msg
            return header
        elif(flag == 0x04):
            return header
        elif(flag == 0x08):
            return header
        else:
            header = self.__make_header(0x08,header[8],header[9],0)
            if(udpSocket.sendto(header,senderAddress) > 0):
                print("Reset Packet Sent")
            else:
                print("Failed to send Reset Packet")
            return header

    def  __make_header(self, givenFlag, givenSeqNo, givenAckNo, givenPayload):
        global sock352PktHdrData, header_len, version, opt_ptr, protocol
        #TODO: figure out line breaks!
        global checksum, source_port, dest_port, window

        # For Part 1, these are the only flags that vary based on the type
        # of packet being sent, so we ask for them in the parameters
        # the rest aren't used and have been initialized globally
        flags = givenFlag
        sequence_no = givenSeqNo
        ack_no = givenAckNo
        payload_len = givenPayload
        # create a struct using the format that was saved globally
        udpPkt_hdr_data = struct.Struct(sock352PktHdrData)
        # pack this data into a struct and return it
        return udpPkt_hdr_data.pack(version, flags, opt_ptr, protocol,
            header_len, checksum, source_port, dest_port, sequence_no,
            ack_no, window, payload_len)
#end
