# importing relevant libraries for the program
import socket 
import sys
import os

# storing the PORT number 
PORT = int(sys.argv[1])

# creating a socket object and specifying number of bytes to be read everytime
server = socket.socket()
BYTES_TO_READ = 1000

"""
For the simple socket implementation, geeksforgeeks.org was used for reference 
The article used was contributed by Kishlay Verma
Client-server architecture of geeksforgeeks.org was followed 
Copied the code to establish connection 

"""

# binding the port and listening to connections 
server.bind(('', PORT))
server.listen()

# helper function to do the remapping of the file
def remappingFile(file_to_write, line, remapNumber): 
    line_list = line.split() # splitting in word into a list 
    line_remapped = ""
    # for each letter of each word, map the strings by referring dictionaries created below mapping letters to numbers and vice versa
    for word in line_list: 
        remapString = ""
        for letter in word: 
            letter_number = letters_to_numbers[letter]
            letter_number = letter_number + remapNumber
            if (letter_number > 26): # if mapping number exceeds 26 (number of alphabets), subtract it with 26 and start from the beginning of the dictionary
                letter_number = letter_number - 26
                letter_from_number = numbers_to_letters[letter_number]
            else: 
                letter_from_number = numbers_to_letters[letter_number]
            remapString = remapString + letter_from_number # construct the remapped string 
        line_remapped = line_remapped + remapString + " " # construct the remapped line 
    # print(line_remapped)
    file_to_write.write(line_remapped) # write the line into file specified
    file_to_write.write("\n") # go to the next line 

# helper function to read the files line by line
def readWriteFiles(file_to_read, file_to_write, size): 
    # if there is line to read, send it to remappingFile helper function or else break loop
    while True: 
        line = file_to_read.readline()
        #print(line)
        if not line: 
            break
        remappingFile(file_to_write, line, size)

# initializing list of alphabets and numbers
letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26]

# mapping letters to numbers for remapping function
letters_to_numbers = { 
    key: value
    for key, value
    in zip(letters, numbers) 
}

# mapping numbers to letters for remapping function
numbers_to_letters = { 
    key: value 
    for key, value
    in zip(numbers, letters)
}


while True: 
    # establish a connection with the client
    connection, address = server.accept()
    file_length_message = connection.recv(1024).decode("utf-8") # receive the file length sent by the client 

    # send confirmation to client from server
    connection.send("File size received".encode())
    connection.settimeout(1)
    
    # if it times out before data is sent after file size is sent, connection will close
    try: 
        recv_data = connection.recv(1000).decode("utf-8")
    except TimeoutError: 
        print("Did not receive data. Terminating")
        connection.close()
        break

    # opening file to be written and transfered
    # server acting as a receiver in this case
    file_to_receive = open("recv.txt", "w")
    # while there is data to be received 
    while recv_data:
        # if it is end of file, send FIN message to client and break the connection 
        if(recv_data == "EOF"): 
            connection.send("FIN".encode())
            break

        # if data is being received, send acknowledgements and set timeout 
        file_to_receive.write(recv_data)
        connection.send("ACK".encode())
        connection.settimeout(1)

        # if data is not received before timer runs out, connection closes
        try: 
            recv_data = connection.recv(1000).decode("utf-8")
            #print("data received!")
        except TimeoutError:
            print("Data transmission terminated prematurely")
            connection.close()
        
    # once file all of the file is received, client sends message
    signal = connection.recv(1024).decode("utf-8")
    # file renaming is done to reduce confusion and redundancy of files 
    if signal == "done":
        if os.path.isfile("data.txt"): 
            os.remove("data.txt")

        if os.path.isfile("recv.txt"): 
            os.rename("recv.txt", "data.txt")
        
        # message sent to client that file is uploaded which will be decoded at the client side 
        connection.send("Server Response: File uploaded.".encode())   
    
    # message to remap is received 
    connection.settimeout(None)
    message_to_remap = connection.recv(1024).decode("utf-8").split()

    # files to read and write are opened
    file_to_write = open("test_remap.txt", "w")
    file_to_read = open(message_to_remap[2], "r")

    # calling the readWriteFiles which will call the remapper function 
    readWriteFiles(file_to_read, file_to_write, int(message_to_remap[1]))
    
    # closing the files after use
    file_to_write.close()
    file_to_read.close()

    # once remapped, message is sent to client 
    remap_completion_message = "Server Response: File " + message_to_remap[2] + " remapped. Output file is test_remap.txt"
    connection.send(remap_completion_message.encode())

    # server side acting as a the sender in the stop-wait-protocol to send remapped file
    file_to_send = open("test_remap.txt", "r")

    # if client asks for get 
    get_message = connection.recv(1024).decode("utf-8").split()
    if get_message[0] == "get": 
        #print("get command initiated")
        # data is read from the file 
        data_to_send = file_to_send.read(BYTES_TO_READ)
        message_from_receiver = None 
        while True: 
            # if there is no data to be read, send end of file to client and wait for message back and break the loop
            if not data_to_send:
                connection.send("EOF".encode())
                #print("EOF")
                message_from_receiver = connection.recv(1024).decode("utf-8")
                #print(message_from_receiver)
                if message_from_receiver == "FIN" or None: 
                    #print("FIN")
                    connection.send("done".encode())
                    break 
            # if there is data to be read, send data and read the next bytes of data to be sent 
            connection.send(data_to_send.encode())
            data_to_send = file_to_send.read(BYTES_TO_READ)
            # set a timeout and if data is not received within the timeframe, connection closes
            connection.settimeout(1)
            try: 
                message_from_receiver = connection.recv(1024).decode("utf-8")
                #print(message_from_receiver)
            except TimeoutError:
                print("Did not receive ACK. Terminating")
                connection.close()
                break

    # once remapped file is transferred, quit the program
    connection.settimeout(None)
    get_message = connection.recv(1024).decode("utf-8")
    if(get_message == "quit"): 
        connection.close()
        break
    
    # close the connection and break the loop
    connection.close()
    break

    
    