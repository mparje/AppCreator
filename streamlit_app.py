import streamlit as st
from langchain.embeddings import OpenAIEmbeddings
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain import PromptTemplate
from langchain import PromptTemplate, LLMChain
from langchain.memory import ConversationBufferMemory
from langchain.chat_models import ChatOpenAI
from streamlit_extras.switch_page_button import switch_page
import ast
from langchain import OpenAI
import os
import openai

openai.api_key = os.environ.get("OPENAI_API_KEY")

def main():
    if "state" not in st.session_state:
        st.session_state["state"] = "main"
    
    for variable in ['app_name', 'app_emoji', 'app_description', 'system_prompt', 'user_input_label', 'placeholder']:
        if variable not in st.session_state:
            st.session_state[variable] = ''
        
    st.title("Creador de Chatbots para Streamlit🤯")
    st.markdown("¡Bienvenido al futuro de la creación de aplicaciones! Esta es una plataforma alimentada por LLM que crea sin esfuerzo otras aplicaciones alimentadas por LLM.")

    app_user_input = st.text_area(label="Describe la aplicación que necesitas a continuación: ", key="appinput",
            placeholder="Ej. Una aplicación que me dé ideas para videos de YouTube sobre un tema dado...")

    if st.button("Crear"):
        
        app_system_prompt = """Eres streamlitGPT y tu trabajo es ayudar a un usuario a generar una aplicación de streamlit LLM simple. El usuario te describirá lo que hará la aplicación. Luego tomarás esa descripción y generarás un Nombre Divertido, un emoji para la aplicación, una descripción de la aplicación y el sistema de indicaciones para el LLM. Deberás usar este formato exacto como se muestra a continuación para las variables.

        Tu salida debe ser un diccionario de Python que solo incluya estas variables y nada más. Preséntalo como código Python.

        'app_name': "Aquí debería ir el nombre de la aplicación como una cadena, siempre agrega emojis",
        'app_emoji': "Aquí debería ir el emoji que mejor se adapte al nombre de la aplicación",
        'app_description': "Aquí debería ir una descripción de la aplicación como una cadena. Sé divertido e ingenioso",
        'system_prompt': "Eres un chatbot llamado [nombre de la aplicación aquí] que ayuda al humano con [describe lo que hará la aplicación]. Tu trabajo es [dale su rol].\nHistorial del chat: [agrega la variable de entrada llamada chat_history delimitada por llaves] \nPregunta del usuario: [agrega una variable de entrada llamada question delimitada por llaves]",
        'user_input_label': "[agrega una etiqueta para la caja de entrada aquí]",
        'placeholder': "Crea un marcador de posición para la caja de entrada de preguntas, esto debería ser un ejemplo relevante de entrada de usuario",
        
        {app_question}
        """
        custom_prompt1 = PromptTemplate(template=app_system_prompt, input_variables=["app_question"])

        chain1 = LLMChain(
            llm=ChatOpenAI(
                temperature=0.2, 
                model_name="gpt-3.5-turbo",
                openai_api_key=openai.api_key,
            ),
            prompt=custom_prompt1,
            verbose="False",
        ) 

        app_output_str = chain1.run(app_question=app_user_input, return_only_outputs=True)
        app_output = ast.literal_eval(app_output_str)
        
        st.session_state.app_name = app_output['app_name']
        st.session_state.app_emoji = app_output['app_emoji']
        st.session_state.app_description = app_output['app_description']
        st.session_state.system_prompt = app_output['system_prompt']
        st.session_state.user_input_label = app_output['user_input_label']
        st.session_state.placeholder = app_output['placeholder']
        
        # Cambiar la variable de estado después de almacenar las variables
        st.session_state["state"] = "creado"
        
        st.experimental_rerun()
  
def creado():
    # Verificar el valor de la variable de estado
    if st.session_state["state"] == "creado":
        
        if "generado" not in st.session_state:
            st.session_state["generado"] = []

        if "pasado" not in st.session_state:
            st.session_state["pasado"] = []

        st.title(st.session_state.app_name)
        st.markdown(f"{st.session_state.app_emoji} {st.session_state.app_description}")

        if "memoria" not in st.session_state:
            st.session_state["memoria"] = ConversationBufferMemory(memory_key="chat_history", input_key="question")

        user_input = st.text_input(label=st.session_state.user_input_label, placeholder=st.session_state.placeholder)

        if st.button("Entrar"):
                            
            custom_prompt2 = PromptTemplate(template=st.session_state.system_prompt, input_variables=["question", "chat_history"])

            chain2 = LLMChain(
                llm=ChatOpenAI(
                    temperature=0.5, 
                    model_name="gpt-3.5-turbo",
                    openai_api_key=openai.api_key,
                ),
                prompt=custom_prompt2,
                verbose="False",
                memory=st.session_state.memoria
            ) 
            
            output = chain2.run(question=user_input, chat_history=st.session_state["memory"], return_only_outputs=True)
            
            st.session_state.pasado.append(user_input)
            st.session_state.generado.append(output)

            st.markdown(output)
            
            if st.session_state["generado"]:
                with st.expander("Ver Historial de Chat"):
                    for i in range(len(st.session_state["generado"]) - 1, -1, -1):
                        st.markdown(st.session_state["pasado"][i])
                        st.markdown(st.session_state["generado"][i])

def aplicacion():
    if st.session_state.get("state", "main") == "main":
        main()
    elif st.session_state["state"] == "creado":
        creado()

if __name__ == "__main__":
    aplicacion()
