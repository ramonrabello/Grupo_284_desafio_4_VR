from fastapi import FastAPI

app = FastAPI()

@app.post("/jsonrpc/tasks/send")
def impute_data():
    # Simulação de imputação
    return {
        "jsonrpc": "2.0",
        "result": {
            "messages": [{
                "role": "agent",
                "parts": [{
                    "type": "data",
                    "data": {
                        "base_imputada": []  # Resultado simulado
                    }
                }]
            }]
        },
        "id": "impute-data"
    }
