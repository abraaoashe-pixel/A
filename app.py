from flask import Flask, request
import requests, os, json
from datetime import datetime
from openai import OpenAI

app = Flask(__name__)
Z_INSTANCE = os.getenv("Z_INSTANCE")
Z_TOKEN = os.getenv("Z_TOKEN")
OPENAI_KEY = os.getenv("OPENAI_KEY")
client = OpenAI(api_key=OPENAI_KEY)
ARQ = "gastos.json"
if not os.path.exists(ARQ):
    with open(ARQ,"w") as f: json.dump([], f)

def enviar(num, txt):
    url = f"https://api.z-api.io/instances/{Z_INSTANCE}/token/{Z_TOKEN}/send-text"
    requests.post(url, json={"phone": num, "message": txt})

def carregar():
    try: return json.load(open(ARQ))
    except: return []
def salvar(d):
    json.dump(d, open(ARQ,"w"))

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    num = data.get("phone")
    msg = data.get("text",{}).get("message","")
    if not num or not msg: return "ok"
    gastos = carregar()
    prompt = f"Voce e o General, financeiro RISPIDO e direto de BH. Cobra o usuario. Usuario disse: {msg} Gastos: {gastos} Se for gasto novo retorne JSON: novo com data {datetime.now().strftime('%d/%m')}, desc, valor. Se for pergunta, responda rispido, curto, max 3 linhas, e fala total do mes no final. Total={sum(g['valor'] for g in gastos) if gastos else 0}"
    r = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role":"user","content":prompt}])
    resposta = r.choices[0].message.content
    try:
        if '"novo"' in resposta or "'novo'" in resposta or "novo" in resposta:
            import re
            j = json.loads(re.search(r'\{.*\}', resposta, re.DOTALL).group())
            if "novo" in j:
                gastos.append(j["novo"])
                salvar(gastos)
                enviar(num, f"Anotado. {j['novo']['desc']} - R${j['novo']['valor']} | Total mes: R${sum(g['valor'] for g in gastos)}\nTa gastando hein...")
                return "ok"
    except: pass
    enviar(num, resposta)
    return "ok"

@app.route("/")
def home(): return "ON"
