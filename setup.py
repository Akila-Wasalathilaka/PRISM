"""
PRISM Setup Wizard.
Interactive CLI to configure environment variables for PRISM.
"""

import os
import shutil
from pathlib import Path

def main():
    print("=" * 50)
    print("Welcome to PRISM Setup Wizard")
    print("=" * 50)
    
    env_file = Path(".env")
    if env_file.exists():
        print("A .env file already exists. Overwrite? (y/N)")
        if input().strip().lower() != 'y':
            print("Setup aborted.")
            return
            
    print("\n1. GitHub App Credentials")
    print("Create a GitHub App and provide the following:")
    app_id = input("App ID: ").strip()
    client_id = input("Client ID: ").strip()
    client_secret = input("Client Secret: ").strip()
    webhook_secret = input("Webhook Secret: ").strip()
    private_key_path = input("Path to Private Key (.pem file): ").strip()
    
    if private_key_path and Path(private_key_path).exists():
        with open(private_key_path, 'r') as f:
            private_key = f.read().replace('\n', '\\n')
    else:
        private_key = ""
        
    print("\n2. AI Provider Selection")
    print("Choose your preferred AI provider:")
    print("1) Mistral (Free tier available)")
    print("2) OpenAI")
    print("3) Google Gemini (Free tier available)")
    print("4) Anthropic")
    print("5) Ollama (Local, Free)")
    print("6) Custom OpenAI-Compatible API")
    print("7) None (Deterministic Only)")
    
    choice = input("Enter choice (1-7): ").strip()
    
    mistral_key = openai_key = gemini_key = anthropic_key = ollama_url = custom_url = custom_key = custom_model = ""
    
    if choice == '1':
        mistral_key = input("Mistral API Key: ").strip()
    elif choice == '2':
        openai_key = input("OpenAI API Key: ").strip()
    elif choice == '3':
        gemini_key = input("Gemini API Key: ").strip()
    elif choice == '4':
        anthropic_key = input("Anthropic API Key: ").strip()
    elif choice == '5':
        ollama_url = input("Ollama URL (e.g. http://localhost:11434): ").strip()
    elif choice == '6':
        custom_url = input("Custom LLM URL: ").strip()
        custom_key = input("Custom LLM API Key (optional): ").strip()
        custom_model = input("Custom LLM Model (optional): ").strip()
        
    print("\nGenerating .env file...")
    
    env_content = f"""# ============================================
# PRISM — Environment Variables
# ============================================

ENVIRONMENT=production
DEBUG=false

# ── Database ──
DATABASE_URL=postgresql+asyncpg://prism:prism@postgres:5432/prism

# ── Redis ──
REDIS_URL=redis://redis:6379/0

# ── GitHub App ──
GITHUB_APP_ID={app_id}
GITHUB_APP_PRIVATE_KEY="{private_key}"
GITHUB_CLIENT_ID={client_id}
GITHUB_CLIENT_SECRET={client_secret}
GITHUB_WEBHOOK_SECRET={webhook_secret}

# ── AI Provider ──
MISTRAL_API_KEY={mistral_key}
OPENAI_API_KEY={openai_key}
GEMINI_API_KEY={gemini_key}
ANTHROPIC_API_KEY={anthropic_key}
OLLAMA_URL={ollama_url}
CUSTOM_LLM_URL={custom_url}
CUSTOM_LLM_KEY={custom_key}
CUSTOM_LLM_MODEL={custom_model}

# ── Auth ──
JWT_SECRET_KEY={os.urandom(32).hex()}
"""
    
    with open(env_file, 'w') as f:
        f.write(env_content)
        
    print(f"\nSuccessfully created {env_file}!")
    print("You can now run 'docker compose up -d' to start the PRISM stack.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nSetup aborted.")
