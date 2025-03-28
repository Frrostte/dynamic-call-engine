import asyncio
import aiohttp
import time
import statistics
import matplotlib.pyplot as plt
import os
import seaborn as sns
from dotenv import load_dotenv
import json

load_dotenv()

# List of Cloudflare AI model endpoints
text_generation_cloudflare = [
    "@cf/deepseek-ai/deepseek-math-7b-instruct",
    "@cf/defog/sqlcoder-7b-2",
    "@cf/fblgit/una-cybertron-7b-v2-bf16",
    "@cf/google/gemma-2b-it-lora",
    "@cf/google/gemma-7b-it-lora",
    "@cf/meta-llama/llama-2-7b-chat-hf-lora",
    "@cf/meta/llama-3-8b-instruct",
    "@cf/meta/llama-3-8b-instruct-awq",
    "@cf/microsoft/phi-2",
    "@cf/mistral/mistral-7b-instruct-v0.1-vllm",
    "@cf/mistral/mistral-7b-instruct-v0.2-lora",
    "@cf/openchat/openchat-3.5-0106",
    "@cf/qwen/qwen1.5-0.5b-chat",
    "@cf/qwen/qwen1.5-1.8b-chat",
    "@cf/qwen/qwen1.5-14b-chat-awq",
    "@cf/qwen/qwen1.5-7b-chat-awq",
    "@cf/thebloke/discolm-german-7b-v1-awq",
    "@cf/tiiuae/falcon-7b-instruct",
    "@cf/tinyllama/tinyllama-1.1b-chat-v1.0",
    "@hf/meta-llama/meta-llama-3-8b-instruct",
    "@hf/mistral/mistral-7b-instruct-v0.2",
    "@hf/nexusflow/starling-lm-7b-beta",
    "@hf/nousresearch/hermes-2-pro-mistral-7b",
    "@hf/thebloke/deepseek-coder-6.7b-base-awq",
    "@hf/thebloke/deepseek-coder-6.7b-instruct-awq",
    "@hf/thebloke/llama-2-13b-chat-awq",
    "@hf/thebloke/llamaguard-7b-awq",
    "@hf/thebloke/mistral-7b-instruct-v0.1-awq",
    "@hf/thebloke/neural-chat-7b-v3-1-awq",
    "@hf/thebloke/openhermes-2.5-mistral-7b-awq",
    "@hf/thebloke/zephyr-7b-beta-awq",
]


ACCOUNT_ID = os.environ["CLOUDFLARE_ACCOUNT_ID"]
API_TOKEN = os.environ["CLOUDFLARE_API_TOKEN"]
headers = {"Authorization": f"Bearer {API_TOKEN}", "Content-Type": "application/json"}


# Function to send an asynchronous HTTP request to the given model endpoint
async def fetch(session, model_name):
    url = f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/ai/run/{model_name}"
    payload = json.dumps(
        {
            "prompt": "Hello, world!",  # example prompt
            "max_tokens": 256,
            # Add other parameters as needed
        }
    )
    start_time = time.time()
    async with session.post(url, headers=headers, data=payload) as response:
        resp = await response.text()
    return time.time() - start_time  # Return the latency


# Function to run benchmarks for all models
async def run_benchmarks():
    async with aiohttp.ClientSession() as session:
        latencies = {}
        for model in text_generation_cloudflare:
            latency = await fetch(session, model)
            if model not in latencies:
                latencies[model] = []
            latencies[model].append(latency)
        return latencies


# Function to analyze and plot results
def analyze_results(latencies):
    means = {model: statistics.mean(times) for model, times in latencies.items()}

    # Set the figure size for a bigger plot
    plt.figure(figsize=(15, 8))

    # Use seaborn's color palette for more vibrant colors
    sns.set(style="whitegrid")
    colors = sns.color_palette("hsv", len(means))

    # Create a bar plot
    plt.bar(means.keys(), means.values(), color=colors)
    plt.xlabel("Model")
    plt.ylabel("Average Latency (s)")
    plt.title("Benchmarking Cloudflare AI Models")
    plt.xticks(rotation=90)
    plt.tight_layout()  # Adjust layout to make room for label rotation

    # Save the plot to a file
    plt.savefig("./cloudflare_ai_benchmarks.png")  # Save as PNG file in the data folder
    plt.show()

    with open("./cloudflare_ai_benchmarks.txt", "w") as f:
        for model, latency in means.items():
            f.write(f"{model}: {latency}\n")

    with open("./cloudflare_ai_benchmarks.json", "w") as f:
        json.dump(means, f, indent=4)


# Main asynchronous loop to execute the benchmark
async def main():
    latencies = await run_benchmarks()
    analyze_results(latencies)


# Run the benchmark
if __name__ == "__main__":
    asyncio.run(main())
