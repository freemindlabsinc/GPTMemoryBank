from llama_index.llms.ollama import Ollama
llm = Ollama(model="llama2", request_timeout=60.0, base_url="http://localhost:11434")
resp = llm.complete("How much is 1 + 121 x 20?")
print(resp)