# importing libraries for the program 
import socket
import sys
import os 

# IP and PORT taken from command line 
server_IP = sys.argv[1] 
PORT = int(sys.argv[2])
BYTES_TO_READ = 1000 # numbers of byte to be read everytime 

"""
For the simple socket implementation, geeksforgeeks.org was used for reference 
The article used was contributed by Kishlay Verma
Client-server architecture of geeksforgeeks.org was followed 
Copied the code to establish connection 

"""
# creating a socket object
client = socket.socket()

# connecting the IP and the PORT 
client.connect((server_IP, PORT))

user_input = input("Enter command: ").split() # asking for input in the console

file_to_send = open(user_input[1], "r") # opening the file mentioned for reading purposes
size = os.path.getsize(user_input[1]) # getting the file size in bytes using python libraries 

file_length_message = "LEN:" + str(size)
client.send(file_length_message.encode()) # sending the file length to the server side 

#print(client.recv(1024).decode("utf-8")) # receiving the data from server and decoding it into a string ("utf-8")

message_from_receiver = None 

#reading from the file and acting as a sender in this stop-and-wait protocol
data_to_send = file_to_send.read(BYTES_TO_READ)
while True: 
    if not data_to_send: # if there is no data to read, send "EOF" to the server and receive message from server
        client.send("EOF".encode())
        message_from_receiver = client.recv(1024).decode("utf-8")
        if message_from_receiver == "FIN" or None: # if message is "FIN" break the loop
            break
    # if there is data to send, keep reading and sending data to server
    client.send(data_to_send.encode())
    data_to_send = file_to_send.read(BYTES_TO_READ)
    client.settimeout(1) # set a timeout for the client for 1 second
    # if message is not received from server, print and close connection 
    try: 
        message_from_receiver = client.recv(1024).decode("utf-8")
    except TimeoutError: 
        print("Did not receive ACK. Terminating")
        client.close()
        break
    
    #if message_from_receiver == "FIN" or None:
        #client.close()
        #break

# once file is read and sent to the server, client waits for server's response
print("Awaiting server response.")
client.send("done".encode())
print(client.recv(1024).decode("utf-8"))

# requests for the next input and sends it to the server 
user_input = input("Enter command: ")
client.send(user_input.encode())
print(client.recv(1024).decode("utf-8"))

# asks for the user input for remapped file from server 
user_input = input("Enter command: ")
client.send(user_input.encode())

# client acting as a receiver 
client.settimeout(1)
# if data is not received before client is timed out, connection closes
try: 
    recv_data = client.recv(1000).decode("utf-8")
    temp = recv_data
except TimeoutError:
    print("Did not receive data. Terminating")
    client.close()

# opening file to be written 
file_to_receive = open("remap_file.txt", "w")
# while client is receiving data, client writes data into file; sends acknowledgements, and waits for next data 
while recv_data: 
    if(recv_data == "EOF"): 
        client.send("FIN".encode())
        break
    file_to_receive.write(recv_data)
    client.send("ACK".encode())
    client.settimeout(1)
    # if no data is received before connection is timed out, connection closes
    try: 
        recv_data = client.recv(1000).decode("utf-8")
    except TimeoutError: 
        print("Data transmission terminated prematurely")
        client.close()

# once all the data is received, files are renamed to reduce redundancy 
signal = client.recv(1024).decode("utf-8")
if signal == "done": 
    if os.path.isfile("test_remap.txt"): 
        os.remove("test_remap.txt")

    if os.path.isfile("remap_file.txt"): 
        os.rename("remap_file.txt", "test_remap.txt")

print("File test_remap.txt downloaded. ")
# quitting the program once file has been transferred
user_input = input("Enter command: ")
if(user_input == "quit"): 
    print("Exiting the program!")
    client.send(user_input.encode())
    client.close()

# closing connection
client.close()



















    










