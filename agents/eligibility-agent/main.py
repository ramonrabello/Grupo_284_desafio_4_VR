from fastapi import FastAPI

app = FastAPI()

@app.post("/jsonrpc/tasks/send")
def filter_ineligible():
    return {
        "jsonrpc": "2.0",
        "result": {
            "messages": [{
                "role": "agent",
                "parts": [{
                    "type": "data",
                    "data": {
                        "base_filtrada": []  # Simulação de resultado
                    }
                }]
            }]
        },
        "id": "filter-ineligible"
    }
}