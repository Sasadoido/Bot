import streamlit as st
import replicate
import os

#tradutor
from deep_translator import GoogleTranslator

# Titulo
st.set_page_config(page_title="PsicoBoto")

# Autentificar as credenciais
with st.sidebar:
    st.title('💬 PsicoBot')
    if 'REPLICATE_API_TOKEN' in st.secrets:
        st.success('API key correta!', icon='✅')
        replicate_api = st.secrets["REPLICATE_API_TOKEN"]
        client = replicate.Client(api_token=replicate_api)
        #os.environ["REPLICATE_API_TOKEN"] = replicate_api
        #replicate_api = replicate_api.Client(api_token=os.environ["REPLICATE_API_TOKEN"])
    else:
        replicate_api = st.text_input('Replicate API token:', type='password')
        if not (replicate_api.startswith('r8_') and len(replicate_api)==40):
            st.warning('Insira suas credencias ', icon='⚠️')
        else:
            st.success('Pode falar com o bot!', icon='👉')

    #llm = 'a16z-infra/llama7b-v2-chat:4f0a4744c7295c024a1de15e1a63c880d3da035fa1f49bfd344fe076074c8eea'

# Guarda o historico do chat LLM
if "messages" not in st.session_state.keys():
    st.session_state.messages = [{"role": "Assistant", "content": "Como você está se sentindo hoje??"}]

# Mostrar ou limpar as a conversa
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

def clear_chat_history():
    st.session_state.messages = [{"role": "Assistant", "content": "Como você está se sentindo hoje??"}]
st.sidebar.button('Limpar chat', on_click=clear_chat_history)

# Fução para gerar a resposta
def generate_llama2_response(prompt_input):
    string_dialogue = "Você é um psicólogo brasileiro que tenta ajudar os usuários com problemas ou sentimentos que os incomodam com conselhos, sempre em portugues. Você não responde como 'User' nem finge ser 'User'. Você só uma vez quando for 'Assistant'."
    for dict_message in st.session_state.messages:
        if dict_message["role"] == "User":
            string_dialogue += "User: " + dict_message["content"] + "\n\n"
        else:
            string_dialogue += "Assistant: " + dict_message["content"] + "\n\n"
    output = replicate.run('a16z-infra/llama13b-v2-chat:df7690f1994d94e96ad9d568eac121aecf50684a0b0963b25a41cc40061269e5', 
                            #'a16z-infra/llama7b-v2-chat:4f0a4744c7295c024a1de15e1a63c880d3da035fa1f49bfd344fe076074c8eea',
                           input={"prompt": f"{string_dialogue} {prompt_input} Assistant: ",
                                  "temperature":0.1, "top_p":0.9, "max_length":120, "repetition_penalty":1})# temperatura bem baixa para o modelo nao correr riscos e dar uma resposta menos criativa
    return output

# Prompt do usuario
if prompt := st.chat_input(disabled=not replicate_api):
    st.session_state.messages.append({"role": "User", "content": prompt})
    with st.chat_message("User"):
        st.write(prompt)

# Gera a resposta se a ultima msg nao for do Assistant
if st.session_state.messages[-1]["role"] != "Assistant":
    with st.chat_message("Assistant"):
        with st.spinner("Pensando..."):
            response = generate_llama2_response(prompt)
            placeholder = st.empty()
            full_response = ''
            for item in response:
                full_response += item
                placeholder.markdown(full_response)
                full_response = GoogleTranslator(source='auto', target='pt').translate(full_response)
            placeholder.markdown(full_response)
            full_response = GoogleTranslator(source='auto', target='pt').translate(full_response)    
    
    # Traduzindo a resposta para português
    
    message = {"role": "Assistant", "content": full_response}
    st.session_state.messages.append(message)
