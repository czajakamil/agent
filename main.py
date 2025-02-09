import asyncio
import subprocess
import webbrowser
import time
import os
import sys

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.config.settings import settings
from src.utils.errors import AppError, ConfigError

def start_server(script_path: str, port: int, name: str) -> subprocess.Popen:
    """Start a server process.
    
    Args:
        script_path: Path to the server script
        port: Server port
        name: Server name for logging
        
    Returns:
        subprocess.Popen: The server process
    """
    try:
        process = subprocess.Popen([sys.executable, script_path])
        print(f"Started {name} server on port {port}")
        return process
    except Exception as e:
        raise ConfigError(f"Failed to start {name} server: {str(e)}")

def main():
    """Main application entry point."""
    try:
        # Start Flask API server
        api_process = start_server(
            'src/api.py',
            settings.api_port,
            'API'
        )
        time.sleep(2)  # Give API server time to start
        
        # Start Gradio interface
        gradio_process = start_server(
            'src/interfaces/gradio_app.py',
            settings.gradio_port,
            'Gradio'
        )
        time.sleep(3)  # Give Gradio time to start
        
        # Open the Gradio app in default browser
        webbrowser.open(f'http://localhost:{settings.gradio_port}')
        
        print("\nAll servers are running!")
        print(f"API server: http://localhost:{settings.api_port}")
        print(f"Gradio interface: http://localhost:{settings.gradio_port}")
        print("\nPress Ctrl+C to stop all servers.")
        
        # Keep the main process running
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
            
    except AppError as e:
        print(f"\nApplication error: {e.message}")
    except Exception as e:
        print(f"\nUnexpected error: {str(e)}")
    finally:
        # Ensure processes are terminated
        if 'api_process' in locals():
            api_process.terminate()
        if 'gradio_process' in locals():
            gradio_process.terminate()

if __name__ == "__main__":
    main() 