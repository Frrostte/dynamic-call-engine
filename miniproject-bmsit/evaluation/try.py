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

# Define input sizes
input_sizes = {
    "small": "Hello, world!",
    "medium": "Can you explain the concept of machine learning in simple terms?",
    "large": "Write a short story about a robot learning to understand human emotions. Include details about its experiences and challenges."
}

# Define output sizes
output_sizes = [100, 250, 500, 1000]

# Function to send an asynchronous HTTP request to the given model endpoint
async def fetch(session, model_name, input_size, output_size):
    url = f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/ai/run/{model_name}"
    payload = json.dumps({
        "prompt": input_sizes[input_size],
        "max_tokens": output_size,
    })
    start_time = time.time()
    async with session.post(url, headers=headers, data=payload) as response:
        resp = await response.text()
    return time.time() - start_time  # Return the latency

# Function to run benchmarks for all models
async def run_benchmarks():
    async with aiohttp.ClientSession() as session:
        latencies = {}
        for model in text_generation_cloudflare:
            for input_size in input_sizes.keys():
                for output_size in output_sizes:
                    key = f"{model}_{input_size}_{output_size}"
                    latency = await fetch(session, model, input_size, output_size)
                    if key not in latencies:
                        latencies[key] = []
                    latencies[key].append(latency)
        return latencies

# Function to analyze and plot results
def analyze_results(latencies):
    means = {key: statistics.mean(times) for key, times in latencies.items()}

    # Prepare data for plotting
    models = list(set([key.split('_')[0] for key in means.keys()]))
    input_sizes_list = list(input_sizes.keys())
    output_sizes_list = output_sizes

    # Create subplots
    fig, axs = plt.subplots(len(input_sizes_list), len(output_sizes_list), figsize=(20, 15))
    fig.suptitle("Benchmarking Cloudflare AI Models")

    for i, input_size in enumerate(input_sizes_list):
        for j, output_size in enumerate(output_sizes_list):
            data = [means[f"{model}_{input_size}_{output_size}"] for model in models]
            axs[i, j].bar(models, data)
            axs[i, j].set_title(f"Input: {input_size}, Output: {output_size}")
            axs[i, j].set_xticklabels(models, rotation=90)
            axs[i, j].set_ylabel("Average Latency (s)")

    plt.tight_layout()
    plt.savefig("./cloudflare_ai_benchmarks2.png")
    plt.close()

    # Save results to text and JSON files
    with open("./cloudflare_ai_benchmarks.txt", "w") as f:
        for key, latency in means.items():
            f.write(f"{key}: {latency}\n")

    with open("./cloudflare_ai_benchmarks.json", "w") as f:
        json.dump(means, f, indent=4)

# Main asynchronous loop to execute the benchmark
async def main():
    latencies = await run_benchmarks()
    analyze_results(latencies)

# Run the benchmark
if __name__ == "__main__":
    asyncio.run(main())