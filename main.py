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
        
        # Start Streamlit app in a separate process with disabled auto-browser opening
        streamlit_process = subprocess.Popen(['streamlit', 'run', '--server.headless=true', 'streamlit_app.py'])
        print("Started Streamlit app...")
        
        # Give Streamlit a moment to start
        time.sleep(3)
        
        # Open the Streamlit app in the default browser
        webbrowser.open('http://localhost:8501')
        
        print("\nBoth servers are running!")
        print("API server is available at: http://localhost:8000")
        print("Streamlit app is available at: http://localhost:8501")
        print("\nPress Ctrl+C to stop both servers.")
        
        # Keep the main process running and handle graceful shutdown
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nShutting down servers...")
            api_process.terminate()
            streamlit_process.terminate()
            api_process.wait()
            streamlit_process.wait()
            print("Servers stopped. Goodbye!")
            
    except Exception as e:
        print(f"\nError during initialization: {str(e)}")
        # Ensure processes are terminated in case of error
        if 'api_process' in locals():
            api_process.terminate()
        if 'streamlit_process' in locals():
            streamlit_process.terminate()
        return

if __name__ == "__main__":
    main() 