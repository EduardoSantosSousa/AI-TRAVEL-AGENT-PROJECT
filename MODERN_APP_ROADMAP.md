# Roadmap Para Modernizar o AI Travel Planner

Este guia mostra uma ordem recomendada para transformar o projeto atual em um app mais moderno, profissional e parecido com a interface descrita para o Google Stitch.

O objetivo final e ter um app Streamlit com:

- layout moderno em duas colunas;
- formulario de planejamento bem organizado;
- sugestoes de interesses em formato de chips;
- resultado do roteiro em cards ou timeline;
- estado vazio antes de gerar o roteiro;
- estado de carregamento enquanto a IA trabalha;
- prompt da IA mais completo;
- base preparada para evoluir para JSON estruturado, historico e exportacao.

---

## 1. Corrigir A Base Do Projeto

Antes de mexer na interface, corrija nomes com erro de digitacao. Isso deixa o projeto mais facil de manter.

### Arquivos envolvidos

- `app.py`
- `core/planner.py`
- `src/chains/itinerary_chain.py`

### Trocas recomendadas

Troque:

```text
itinerary
```

por:

```text
itinerary
```

Troque:

```text
itnineary_prompt
```

por:

```text
itinerary_prompt
```

Troque:

```text
generate_itinerary
```

por:

```text
generate_itinerary
```

Troque:

```text
create_itinerary
```

por:

```text
create_itinerary
```

### Exemplo em `core/planner.py`

Antes:

```python
def create_itinerary(self):
    ...
```

Depois:

```python
def create_itinerary(self):
    ...
```

### Exemplo em `app.py`

Antes:

```python
itinerary = planner.create_itinerary()
st.markdown(itinerary)
```

Depois:

```python
itinerary = planner.create_itinerary()
st.markdown(itinerary)
```

---

## 2. Corrigir O Logger

Se ainda nao corrigiu, ajuste o formato do logger.

### Arquivo

- `utils/logger.py`

### Antes

```python
format='%(asctime) - %(levelname)s - %(message)s',
```

### Depois

```python
format='%(asctime)s - %(levelname)s - %(message)s',
```

---

## 3. Transformar O `app.py` Em Uma Tela Moderna

Hoje o app esta em formato simples:

```python
st.title(...)
st.write(...)
with st.form(...)
```

A primeira grande melhoria visual e usar uma tela larga com duas colunas:

- coluna esquerda: formulario de planejamento;
- coluna direita: preview ou resultado do roteiro.

### Arquivo

- `app.py`

### Estrutura recomendada

```python
import streamlit as st
from dotenv import load_dotenv
from core.planner import TravelPlanner

load_dotenv()

st.set_page_config(
    page_title="AI Travel Planner",
    page_icon="✈️",
    layout="wide"
)

st.title("AI Travel Planner")
st.write("Create a personalized travel itinerary with AI.")

left_col, right_col = st.columns([1, 1.4])

with left_col:
    st.subheader("Plan your trip")

    with st.form("planner_form"):
        city = st.text_input("Destination city")
        interests = st.text_input("Interests")
        submitted = st.form_submit_button("Generate itinerary")

with right_col:
    st.subheader("Your itinerary")
    st.info("Your generated itinerary will appear here.")
```

Esse passo ja deixa a experiencia mais parecida com um app real.

---

## 4. Adicionar CSS Customizado Para Visual Profissional

O Streamlit permite inserir CSS usando `st.markdown`.

### Arquivo

- `app.py`

### Adicione perto do topo do arquivo

```python
st.markdown(
    """
    <style>
    .main {
        background-color: #f7fafc;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }

    .app-card {
        background: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 24px;
        box-shadow: 0 8px 24px rgba(15, 23, 42, 0.06);
    }

    .muted-text {
        color: #64748b;
        font-size: 0.95rem;
    }

    .chip {
        display: inline-block;
        padding: 6px 10px;
        margin: 4px 4px 4px 0;
        border-radius: 999px;
        background: #e0f2fe;
        color: #075985;
        font-size: 0.85rem;
        font-weight: 500;
    }

    .itinerary-card {
        background: #ffffff;
        border: 1px solid #e5e7eb;
        border-left: 4px solid #0f766e;
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 12px;
    }

    .time-label {
        color: #0f766e;
        font-weight: 700;
        font-size: 0.9rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)
```

---

## 5. Criar Um Header Mais Bonito

Substitua o titulo simples por um header com nome do app, descricao e badges.

### Arquivo

- `app.py`

### Exemplo

```python
st.markdown(
    """
    <div style="margin-bottom: 28px;">
        <p class="muted-text">AI-powered travel assistant</p>
        <h1 style="margin-bottom: 8px;">AI Travel Planner</h1>
        <p class="muted-text">
            Build a personalized day-by-day itinerary based on your destination,
            interests, budget and travel style.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)
```

---

## 6. Melhorar O Formulario

Hoje o formulario recebe apenas:

- cidade;
- interesses.

Para ficar mais profissional, adicione:

- quantidade de dias;
- orcamento;
- ritmo da viagem;
- horario de inicio;
- horario de fim.

### Arquivo

- `app.py`

### Exemplo

```python
with st.form("planner_form"):
    city = st.text_input("Destination city", placeholder="Example: Tokyo")

    interests = st.text_input(
        "Interests",
        placeholder="Museums, food, historical places, nature"
    )

    days = st.number_input(
        "Trip duration",
        min_value=1,
        max_value=7,
        value=1
    )

    budget = st.selectbox(
        "Budget",
        ["Low", "Medium", "High"]
    )

    travel_style = st.selectbox(
        "Travel style",
        ["Relaxed", "Balanced", "Intense"]
    )

    start_time = st.time_input("Start time")
    end_time = st.time_input("End time")

    submitted = st.form_submit_button("Generate itinerary")
```

---

## 7. Adicionar Chips De Interesse

Como o Streamlit nao tem chips nativos simples, voce pode simular visualmente com HTML.

### Arquivo

- `app.py`

### Exemplo

```python
st.markdown(
    """
    <div>
        <span class="chip">Museums</span>
        <span class="chip">Food</span>
        <span class="chip">Nature</span>
        <span class="chip">Historical places</span>
        <span class="chip">Architecture</span>
    </div>
    """,
    unsafe_allow_html=True
)
```

Coloque isso abaixo do campo `interests`.

---

## 8. Criar Estado Vazio No Resultado

Antes de gerar o roteiro, a coluna direita nao deve ficar vazia.

### Arquivo

- `app.py`

### Exemplo

```python
with right_col:
    st.markdown('<div class="app-card">', unsafe_allow_html=True)
    st.subheader("Your itinerary")
    st.info("Fill in your trip details and generate an itinerary to see the result here.")
    st.markdown("</div>", unsafe_allow_html=True)
```

---

## 9. Adicionar Loading Com `st.spinner`

Quando o usuario clicar no botao, mostre um estado de carregamento.

### Arquivo

- `app.py`

### Antes

```python
itinerary = planner.create_itinerary()
```

### Depois

```python
with st.spinner("Building your itinerary with AI..."):
    itinerary = planner.create_itinerary()
```

---

## 10. Atualizar O `TravelPlanner` Para Preferencias

Depois de adicionar novos campos no formulario, o `TravelPlanner` precisa receber esses valores.

### Arquivo

- `core/planner.py`

### Adicione atributos no `__init__`

```python
self.days = 1
self.budget = ""
self.travel_style = ""
self.start_time = ""
self.end_time = ""
```

### Adicione um metodo novo

```python
def set_preferences(self, days, budget, travel_style, start_time, end_time):
    self.days = days
    self.budget = budget
    self.travel_style = travel_style
    self.start_time = start_time
    self.end_time = end_time
```

### Atualize a chamada no `app.py`

```python
planner = TravelPlanner()
planner.set_city(city)
planner.set_interests(interests)
planner.set_preferences(days, budget, travel_style, start_time, end_time)
itinerary = planner.create_itinerary()
```

---

## 11. Atualizar A Chain Da IA

Agora a funcao que chama o modelo precisa receber os novos parametros.

### Arquivo

- `src/chains/itinerary_chain.py`

### Antes

```python
def generate_itinerary(city: str, interests: list[str]) -> str:
```

### Depois

```python
def generate_itinerary(
    city: str,
    interests: list[str],
    days: int,
    budget: str,
    travel_style: str,
    start_time: str,
    end_time: str
) -> str:
```

### Atualize a chamada dentro do `TravelPlanner`

No arquivo `core/planner.py`, troque:

```python
itinerary = generate_itinerary(self.city, self.interests)
```

por:

```python
itinerary = generate_itinerary(
    self.city,
    self.interests,
    self.days,
    self.budget,
    self.travel_style,
    self.start_time,
    self.end_time
)
```

---

## 12. Melhorar O Prompt Da IA

O prompt atual e simples. Para um app profissional, ele deve ser mais especifico.

### Arquivo

- `src/chains/itinerary_chain.py`

### Exemplo de prompt melhor

```python
itinerary_prompt = ChatPromptTemplate([
    ("system", """
You are a professional travel planner.

Create a personalized travel itinerary for the user.

Trip details:
- Destination: {city}
- Duration: {days} day(s)
- Interests: {interests}
- Budget: {budget}
- Travel style: {travel_style}
- Start time: {start_time}
- End time: {end_time}

Rules:
- Organize the itinerary by day.
- Use clear time blocks.
- Include place names, short descriptions and practical tips.
- Keep the route realistic for a traveler.
- Respect the user's budget and travel style.
- If the user has many interests, prioritize the best ones.

Return the answer in Markdown.
"""),
    ("human", "Create my travel itinerary.")
])
```

### Atualize o `format_messages`

```python
itinerary_prompt.format_messages(
    city=city,
    interests=", ".join(interests),
    days=days,
    budget=budget,
    travel_style=travel_style,
    start_time=start_time,
    end_time=end_time
)
```

---

## 13. Renderizar O Resultado De Forma Mais Bonita

No inicio, voce pode continuar usando:

```python
st.markdown(itinerary)
```

Mas envolva o resultado em um container visual.

### Arquivo

- `app.py`

### Exemplo

```python
st.markdown('<div class="app-card">', unsafe_allow_html=True)
st.subheader("Your itinerary")
st.markdown(itinerary)
st.markdown("</div>", unsafe_allow_html=True)
```

---

## 14. Proxima Evolucao: JSON Estruturado

Depois que a interface estiver moderna, a maior evolucao tecnica sera pedir para a IA retornar JSON em vez de Markdown.

Isso permite renderizar cada parada como card:

```json
{
  "city": "Tokyo",
  "days": [
    {
      "day": 1,
      "items": [
        {
          "time": "09:00",
          "place": "Senso-ji Temple",
          "description": "Visit one of Tokyo's oldest temples.",
          "duration": "1.5 hours",
          "tip": "Arrive early to avoid crowds."
        }
      ]
    }
  ]
}
```

Com isso, o `app.py` pode montar cards reais em vez de apenas exibir Markdown.

Nao comece por aqui. Primeiro deixe:

1. nomes corrigidos;
2. layout moderno;
3. formulario completo;
4. prompt melhor;
5. app funcionando sem erros.

---

## 15. Ordem Recomendada De Implementacao

Siga nesta ordem:

1. Corrigir nomes `itinerary` para `itinerary`.
2. Corrigir o logger.
3. Alterar `st.set_page_config` para `layout="wide"`.
4. Criar layout com duas colunas.
5. Adicionar CSS customizado.
6. Criar header moderno.
7. Melhorar formulario com novos campos.
8. Adicionar chips visuais de interesses.
9. Adicionar estado vazio na area de resultado.
10. Adicionar `st.spinner` no momento da geracao.
11. Atualizar `TravelPlanner` para receber preferencias.
12. Atualizar `generate_itinerary` para receber preferencias.
13. Melhorar o prompt da IA.
14. Testar o app com `streamlit run app.py`.
15. Depois evoluir para JSON estruturado.

---

## 16. Como Testar Depois De Cada Mudanca

Depois de cada bloco de alteracao, rode:

```powershell
streamlit run app.py
```

Teste com:

```text
City: Delhi
Interests: Red Fort, Lotus Temple, Qutub Minar
Days: 1
Budget: Medium
Travel style: Balanced
```

Verifique:

- se o app abre sem erro;
- se o formulario aparece corretamente;
- se o botao gera o roteiro;
- se o resultado aparece na coluna direita;
- se os logs nao mostram erro de formatacao;
- se a resposta da IA respeita cidade, interesses, budget e estilo.

---

## 17. Melhorias Futuras

Depois que o app moderno estiver funcionando, voce pode adicionar:

- historico de roteiros com SQLite;
- exportacao para PDF;
- botao para baixar Markdown;
- integracao com Google Maps;
- previsao do tempo;
- autenticacao;
- deploy no Streamlit Cloud;
- testes automatizados;
- retorno JSON com Pydantic;
- cards reais para cada atividade do roteiro.

---

## Resumo

O melhor caminho e nao tentar fazer tudo de uma vez.

Primeiro transforme o projeto atual em um app moderno de uma unica tela. Depois melhore a IA e a estrutura dos dados.

A primeira versao profissional deve ter:

- interface em duas colunas;
- formulario completo;
- visual com CSS customizado;
- loading state;
- empty state;
- prompt mais rico;
- resultado bem apresentado.

Depois disso, o projeto ja vai parecer muito mais com um produto real.
