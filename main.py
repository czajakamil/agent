from clasess.OpenAIService import OpenAIService
import asyncio
from dotenv import load_dotenv
import subprocess
import webbrowser
import time
import os

def main():
    # Load environment variables
    load_dotenv()
    
    try:
        # Start Flask API server in a separate process
        api_process = subprocess.Popen(['python', 'api.py'])
        print("Started API server...")
        
        # Give the API server a moment to start
        time.sleep(2)
        
        # Start Gradio app in a separate process
        gradio_process = subprocess.Popen(['python', 'gradio_app.py'])
        print("Started Gradio app...")
        
        # Give Gradio a moment to start
        time.sleep(3)
        
        # Open the Gradio app in the default browser
        webbrowser.open('http://localhost:7860')
        
        print("\nBoth servers are running!")
        print("API server is available at: http://localhost:8000")
        print("Gradio app is available at: http://localhost:7860")
        print("\nPress Ctrl+C to stop both servers.")
        
        # Keep the main process running and handle graceful shutdown
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nShutting down servers...")
            api_process.terminate()
            gradio_process.terminate()
            api_process.wait()
            gradio_process.wait()
            print("Servers stopped. Goodbye!")
            
    except Exception as e:
        print(f"\nError during initialization: {str(e)}")
        # Ensure processes are terminated in case of error
        if 'api_process' in locals():
            api_process.terminate()
        if 'gradio_process' in locals():
            gradio_process.terminate()
        return

if __name__ == "__main__":
    main() 