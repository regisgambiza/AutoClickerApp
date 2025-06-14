import ollama
import os
import time

LOG_FILE = "C:/Users/regis/Documents/AutoClickerLogs/autoclicker.log"

def list_models():
    try:
        return ollama.list().models
    except Exception as e:
        print(f"❌ Failed to fetch models from Ollama: {e}")
        return []

def select_model():
    models = list_models()
    if not models:
        print("❌ No models available.")
        return None

    print("\n📦 Available Models:")
    for i, m in enumerate(models):
        print(f"{i + 1}. {m.model}")

    while True:
        try:
            choice = int(input("\n👉 Select a model by number: ")) - 1
            if 0 <= choice < len(models):
                return models[choice].model
        except ValueError:
            pass
        print("❗Invalid choice. Try again.")

def read_logs():
    if not os.path.exists(LOG_FILE):
        print(f"❌ Log file not found: {LOG_FILE}")
        return ""
    
    with open(LOG_FILE, 'r', encoding='utf-8', errors='ignore') as file:
        return file.read()

def summarize_logs(model_name, log_content):
    if not log_content.strip():
        print("⚠️ Log file is empty.")
        return

    prompt = (
        "You are analyzing automation performance logs from an auto-clicker app.\n"
        "Summarize the performance, including:\n"
        "- Number of scan cycles\n"
        "- Number of clicks performed\n"
        "- Click success or failure indications\n"
        "- Errors if any\n"
        "- Overall reliability (brief analysis)\n\n"
        "Here are the logs:\n\n"
        f"{log_content}\n\n"
        "Now provide a clear and concise analysis of these logs."
    )

    print(f"\n📡 Sending logs to model '{model_name}'...")
    try:
        response = ollama.chat(model=model_name, messages=[
            {"role": "user", "content": prompt}
        ])
        print("\n🧠 Analysis from model:\n")
        print(response['message']['content'])

    except Exception as e:
        print(f"❌ Failed to generate response: {e}")

def main():
    model_name = select_model()
    if not model_name:
        return

    log_content = read_logs()
    summarize_logs(model_name, log_content)

if __name__ == "__main__":
    main()
