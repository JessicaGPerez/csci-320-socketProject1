import socket
import os
import struct
import hashlib  # needed to verify file hash


IP = '127.0.0.1'  # change to the IP address of the server
PORT = 12000  # change to a desired port number
BUFFER_SIZE = 1024  # change to a desired buffer size




def get_file_info(data: bytes) -> (str, int):
    return data[8:].decode(), int.from_bytes(data[:8],byteorder='big')


def upload_file(server_socket: socket, file_name: str, file_size: int):
    # create a SHA256 object to verify file hash
    # TODO: section 1 step 5 in README.md file
    hash_object = hashlib.sha256()

    # create a new file to store the received data
    with open(file_name +'.temp', 'wb') as file:
        # TODO: section 1 step 7a - 7e in README.md file
        remaining = file_size
        while remaining > 0:
            data, addr = server_socket.recvfrom(min(remaining, BUFFER_SIZE))
            if not data:
                break
            file.write(data)
            hash_object.update(data)
            remaining -= len(data)
            server_socket.sendto(b'received', addr)
          # replace this line with your code for section 1 step 7a - 7e
    filename_t = file_name + '.temp', 'wb'
    # get hash from client to verify
    # TODO: section 1 step 8 in README.md file
    client_hash, addr = server_socket.recvfrom(BUFFER_SIZE)
    client_hash = client_hash.decode('utf-8')
    # TODO: section 1 step 9 in README.md file
    server_hash = hash_object.hexdigest()
    if client_hash == server_hash:
        os.rename(filename_t, file_name)
        server_socket.sendto(b'success', addr)
    else:
        os.remove(filename_t)
        server_socket.sendto(b'failed',addr)


def start_server():
    # create a UDP socket and bind it to the specified IP and port
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((IP, PORT))
    print(f'Server ready and listening on {IP}:{PORT}')

    try:
        while True:
            # TODO: section 1 step 2 in README.md file
            data, client_address = server_socket.recvfrom(BUFFER_SIZE)
            print("Received: ", data.decode())
            # expecting an 8-byte byte string for file size followed by file name
            # TODO: section 1 step 3 in README.md file
            file_size = struct.unpack('q', data[:8])[0]
            file_name = data[:8].decode()
            file_info = get_file_info(file_name)

            # TODO: section 1 step 4 in README.md file
            upload_file(server_socket, file_name, file_size)
            server_socket.sendto(b"go ahead", client_address)
    except KeyboardInterrupt as ki:
        pass
    except Exception as e:
        print(f'An error occurred while receiving the file:str {e}')
    finally:
        server_socket.close()


if __name__ == '__main__':
    start_server()

