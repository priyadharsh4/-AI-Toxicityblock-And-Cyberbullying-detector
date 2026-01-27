# sender.py
import socket
import time

def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        print("🔄 Connecting to receiver...")
        s.connect(('localhost', 12345))
        print("🚀 CONNECTED TO TOXIC BLOCKER!")
        print("=" * 50)
        
        while True:
            message = input("\n💬 You: ").strip()
            
            if message.lower() in ['quit', 'exit', 'q']:
                s.send(b"QUIT")
                print("👋 Goodbye!")
                break
            
            if not message:
                continue
            
            print(f"📤 Sending: {message}")
            s.send(message.encode('utf-8'))
            
            # Get response from receiver
            response = s.recv(1024).decode('utf-8', errors='ignore')
            print(f"📥 Receiver: {response}")
            
    except Exception as e:
        print(f"❌ Connection error: {e}")
    finally:
        s.close()

if __name__ == "__main__":
    main()
