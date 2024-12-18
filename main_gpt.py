from demo.demo import demo

if __name__ == "__main__":
    demo(
        ".demo/",
        # "google/gemini-1.5-flash-8b",
        # "ollama/qwen2",
        # "groq/llama3-70b-8192",
        "openai/gpt-4o-mini",
        # "ollama/llama3.2",
        10,
    )
