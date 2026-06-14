import os
import json
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage

load_dotenv()

# ---- Scelta del modello ----
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "anthropic")  # Prende dalla variabile del .env, altrimenti "anthropic"

def get_llm():
    if LLM_PROVIDER == "openai":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(model="gpt-4o", temperature=0)
    elif LLM_PROVIDER == "anthropic":
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(model="claude-haiku-4-5-20251001", temperature=0) #type: ignore
    elif LLM_PROVIDER == "ollama":
        from langchain_ollama import ChatOllama
        model = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
        return ChatOllama(model=model, temperature=0)
    elif LLM_PROVIDER == "groq":
        from langchain_groq import ChatGroq
        model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
        return ChatGroq(model=model, temperature=0, api_key=os.getenv("GROQ_API_KEY")) #type: ignore
    else:
        raise ValueError(f"Provider non supportato: {LLM_PROVIDER}")



ROUTER_SYSTEM_PROMPT = """
Sei un esperto di CI/CD e DevOps. Il tuo compito è classificare
il tipo di errore di una pipeline CI analizzando i log.

Categorie disponibili:
- DEPENDENCY: errori su librerie, pip install fallito, ModuleNotFoundError,
  versioni incompatibili, ImportError, package not found
- TEST: test falliti, AssertionError, fixture rotte, mock issues,
  pytest failures, coverage insufficiente
- CONFIG: errori YAML, variabili d'ambiente mancanti, Docker issues,
  secrets non configurati, errori di sintassi nel file CI
- UNKNOWN: non riconducibile alle categorie precedenti

Rispondi ESCLUSIVAMENTE con un JSON valido, senza testo aggiuntivo:
{
  "category": "DEPENDENCY|TEST|CONFIG|UNKNOWN",
  "confidence": 0.0-1.0,
  "reasoning": "spiegazione breve in italiano di max 2 righe"
}
"""


def router_node(state: dict) -> dict:
    """
    Nodo Router: classifica il tipo di errore CI usando LLM.
    Riceve lo State e restituisce gli aggiornamenti da applicare.
    """
    llm = get_llm()

    # Prepara il contesto per l'LLM
    user_message = f"""
        Analizza questo errore CI e classificalo.

        **Job fallito:** {state['ci_job_name']}
        **Conclusione:** {state['ci_conclusion']}
        **Commit SHA:** {state['commit_sha'][:8]}

        **Log CI (ultimi 100 righe):**
        ```
        {state['ci_logs'][-3000:]}
        ```

        **Git diff del commit:**
        ```
        {state.get('git_diff', 'Non disponibile')[:1500]}
        ```

        Classifica l'errore rispondendo SOLO con il JSON richiesto.
    """

    messages = [
        SystemMessage(content=ROUTER_SYSTEM_PROMPT),
        HumanMessage(content=user_message)
    ]

    # Chiama l'LLM
    response = llm.invoke(messages)
    raw = response.content.strip() #type: ignore

    # Pulisce la risposta (a volte l'LLM aggiunge ```json ...```)
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]

    try:
        result = json.loads(raw)
    except json.JSONDecodeError:
        # Fallback se il JSON è malformato
        result = {"category": "UNKNOWN", "confidence": 0.0, "reasoning": "Parsing fallito"}

    print(f"🧭 Router → {result['category']} (confidence: {result['confidence']:.0%})")
    print(f"   Reasoning: {result['reasoning']}")

    # Restituisce gli aggiornamenti allo State
    return {
        "error_category": result["category"].lower(),
        "error_confidence": result["confidence"],
        "router_reasoning": result["reasoning"]
    }