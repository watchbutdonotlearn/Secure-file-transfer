# Secure-file-transfer
This is a project which seeks to create a secure, unbreakable way to transfer encrypted files over email. 


The basic concept of the project is simple. First, two clients agree to send each other a file filled with random numbers, then, chunks of the random numbers are used as passwords for a password encrypted archive which is sent openly via email. On the recieving end, the reciever uses the pre-sent file with all the passwords to decrypt the archive. Like this, a file can be transferred securely, with almost no hope at all of anyone ever being able to break the encryption.


This process, however, could be a little more streamlined, with most parts of it being able to be completely automated. 
