# importing all the libraries 
import socket 
import sys 
import os

server_IP = sys.argv[1]
PORT = int(sys.argv[2])

client = socket.socket()

"""
For the simple socket implementation, geeksforgeeks.org was used for reference 
The article used was contributed by Kishlay Verma
Client-server architecture of geeksforgeeks.org was followed 
Copied code to establish connection between client and server

"""

BUFFER_SIZE = 524288 # choosing a large buffer size to read all the file data together

# connect given the PORT and the server IP
client.connect((server_IP, PORT)) 

"""
https://linuxhint.com/python_socket_file_transfer_send/
The website above was used for reference to read data from files and send over sockets and understand the structure
It is written by Bamdeb Ghosh 
Copied the section where socket was used to read files from client to server 

"""

user_input = input("Enter command: ")
list_input = user_input.split()
file = open(list_input[1], "r")

# send file to server 
data_to_send = file.read(BUFFER_SIZE)
while data_to_send: 
    client.send(data_to_send.encode())
    break

# wait for server's response 
print("Awaiting for server response.")
print(client.recv(2048).decode("utf-8"))
file.close()

# ask the server to remap the file that was sent over
command_to_send = input("Enter command: ")
client.send(command_to_send.encode())

# wait for server's response
print(client.recv(2048).decode("utf-8"))

# get the remapped file from the server
command_to_send = input("Enter command: ")
client.send(command_to_send.encode())

# receive and write the data into another file 
data_to_receive = client.recv(BUFFER_SIZE).decode("utf-8")
file_to_write = open("remap.txt", "w")
file_to_write.write(data_to_receive)

# rename files to avoid redundancy in the file directory
if os.path.isfile("test_remap.txt"): 
        os.remove("test_remap.txt")
    
if os.path.isfile("remap.txt"): 
    os.rename("remap.txt", "test_remap.txt")

# print that file was downloaded
print("File test_remap.txt downloaded.")
file_to_write.close()

# quit the program
command_to_send = input("Enter command: ")
client.send(command_to_send.encode())
if(command_to_send == "quit"): 
    print("Exiting the program")
    client.close()

client.close()





