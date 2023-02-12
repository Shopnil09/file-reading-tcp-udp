# importing the important libraries
import socket
import os 
import sys

# getting the port from command line args
PORT = int(sys.argv[1])

# creating a socket object and initializing a large buffer size
server = socket.socket()
BUFFER_SIZE = 524288

"""
For the simple socket implementation, geeksforgeeks.org was used for reference 
The article used was contributed by Kishlay Verma
Client-server architecture of geeksforgeeks.org was followed 
Copied code to establish connection between C-S

"""
# binding the port 
server.bind(('', PORT))
server.listen()

# opening a file to write the data that server will receive from client
file_to_receive = open("recv.txt", "w")

# remapping helper function 
def remappingFile(file_to_write, line, remapNumber): 
    line_list = line.split()
    line_remapped = ""
    # for each letter in each word in each line, remap the letters using the dictionaries created below 
    for word in line_list: 
        remapString = ""
        for letter in word: 
            letter_number = letters_to_numbers[letter]
            letter_number = letter_number + remapNumber
            if (letter_number > 26): # if number exceeds 26, start from the beginning of the alphabets
                letter_number = letter_number - 26
                letter_from_number = numbers_to_letters[letter_number]
            else: 
                letter_from_number = numbers_to_letters[letter_number]
            remapString = remapString + letter_from_number # construct the remap string
        line_remapped = line_remapped + remapString + " " # construct the remap line
    # write each line in the file specified 
    file_to_write.write(line_remapped)
    file_to_write.write("\n")

# helper function read files line by line
def readWriteFiles(file_to_read, file_to_write, size): 
    while True: 
        line = file_to_read.readline()
        if not line: 
            break
        remappingFile(file_to_write, line, size)

# initializing list of letters and numbers for dictionaries 
letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26]
letters_to_numbers = { 
    key: value
    for key, value
    in zip(letters, numbers) 
}

numbers_to_letters = { 
    key: value 
    for key, value
    in zip(numbers, letters)
}


"""
https://linuxhint.com/python_socket_file_transfer_send/
The website above was used for reference to read data from files and send over sockets and understand the structure
It is written by Bamdeb Ghosh 
Copied the section where socket was used to read files from client to server 

"""

# infinite loop until interrupted
while True: 
    # establish connection with client
    connection, address = server.accept()
    # receive the data from client
    data_to_receive = connection.recv(BUFFER_SIZE)
    # write the data to the file opended before 
    file_to_receive.write(data_to_receive.decode("utf-8"))
    # close the file 
    file_to_receive.close()
 
    # send a completion message from server
    completion_message = "Server response: File uploaded."
    connection.send(completion_message.encode())

    # receive the next command from client 
    command = connection.recv(2048).decode("utf-8").split()

    # modify file names to avoid same name files
    if os.path.isfile("data.txt"): 
        os.remove("data.txt")
    
    if os.path.isfile("recv.txt"): 
        os.rename("recv.txt", command[2])
    
    # open file to write the remapped words 
    file_to_write = open("test_remap.txt", "w")
    # open the prev file to read the transferred file from client 
    file_to_read = open(command[2], "r")

    # call helper function
    readWriteFiles(file_to_read, file_to_write, int(command[1]))
    file_to_read.close()
    file_to_write.close()

    # respond from server side that file has been remapped
    remap_completion_message = "Server Response: File " + command[2] + " remapped. Output file is test_remap.txt"
    connection.send(remap_completion_message.encode())

    # send the remapped file to client 
    command = connection.recv(2048).decode("utf-8").split()
    file_to_send = open(command[1], "r")
    data_to_send = file_to_send.read(BUFFER_SIZE)

    if data_to_send: 
        while data_to_send:
            connection.send(data_to_send.encode())
            break
    
    # quit the program and close connection
    command = connection.recv(2048).decode("utf-8")
    if (command.strip() == "quit"): 
        connection.close()
        break