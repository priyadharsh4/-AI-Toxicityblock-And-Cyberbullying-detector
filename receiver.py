# receiver.py - FIXED (ASCII only)
import socket
import threading
import joblib
from datetime import datetime

# Load YOUR existing model
model = joblib.load("model/toxic_model.pkl")
labels = joblib.load("model/labels.pkl")

def is_toxic(text):
    pred = model.predict([text])[0]
    toxic_labels = [labels[i] for i, val in enumerate(pred) if val == 1]
    return len(toxic_labels) > 0, toxic_labels

def handle_sender(client_socket, addr):
    print(f"\nSender {addr} connected!")
    print(f"Labels: {', '.join(labels)}")
    
    while True:
        try:
            data = client_socket.recv(1024).decode('utf-8', errors='ignore')
            if not data or data == "QUIT": 
                break
            
            timestamp = datetime.now().strftime('%H:%M:%S')
            print(f"\n[{timestamp}] RAW: {data}")
            
            # AI TOXIC CHECK
            is_tox, toxic_labels = is_toxic(data)
            
            if is_tox:
                print(f"BLOCKED! Labels: {', '.join(toxic_labels)}")
                client_socket.send(b"BLOCKED")
            else:
                print(f"SAFE - Delivered: {data}")
                client_socket.send(b"OK:" + data.encode('utf-8'))
                
        except Exception as e:
            print(f"Connection lost: {e}")
            break
    
    client_socket.close()
    print(f"Sender {addr} disconnected")

# Start server
if __name__ == "__main__":
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('localhost', 12345))
    server.listen(5)
    
    print("TOXIC MESSAGE BLOCKER ACTIVE")
    print("Listening on localhost:12345")
    print("Run: python sender.py")
    print("=" * 50)
    
    while True:
        client, addr = server.accept()
        thread = threading.Thread(target=handle_sender, args=(client, addr))
        thread.daemon = True
        thread.start()
