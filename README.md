# file_distribution_tool

Greetings Everyone, this is our team Classic_coders. We have developed a file distribution tool for organizations. 
It uses the following tech stack : 
1. Socket Programming (it is used for making client-server architecture in organization)
2. Multicasting (it is used for transferring files between server and 0 or more clients)
3. RUDP (Reliable User Datagram Protocol) (it is used for making reliable connections between server and client)
4. Multithreading (to ensure that multiple files are transferred)

FUNCTIONALITIES : 
1. File Distribution 
  • allows administrators to initiate file transfers to a group of systems within an organization 
  • it efficiently uses the organization's network bandwidth using RUDP. Network bandwidth is used efficiently using RUDP
  • Multithreading is used to transfer multiple files at a time 
  • integrity is maintained by using checksum to ensure that the same files are received on the client side 

2. Group Management 
  • Groups are created by the admin to allow multiple file transfer
  • Groups are created automatically 

3. Security 
  • only the administrators can distribute files
  • The administrator can control user access for a group
  • protect the data in transmission through Encryption and Decryption

STEPS TO RUN PROJECT : 
Server Side: 
  1. upload a Python file named as "rudp_server.py" on the server site.
  2. open command prompt
  3. locate the Python file location
  4. run command: python rudp_server.py
  5. server will start

Client Side: 
  1. upload a Python file named as "rudp_client.py" on the client site.
  2. open command prompt
  3. locate the Python file location
  4. run command: python rudp_client.py
  5. the client will start to accept the files 
