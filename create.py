# Importar bibliotecas
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

# Configurar la clave de la API de OpenAI
def configurar_clave_api_openai():
    st.sidebar.title("Configuración de la API de OpenAI")
    api_key = st.sidebar.text_input("Ingresa tu clave de API de OpenAI", type="password")
    if not api_key:
        st.warning("Por favor, ingresa una clave de API válida para continuar.")
        return None
    else:
        return api_key

# Función principal
def principal(api_key):
    if "estado" not in st.session_state:
        st.session_state["estado"] = "principal"

    for variable in ['nombre_app', 'emoji_app', 'descripcion_app', 'system_prompt', 'etiqueta_entrada_usuario', 'placeholder']:
        if variable not in st.session_state:
            st.session_state[variable] = ''

    st.title("Creador de Chatbots en Streamlit🤯")
    st.markdown("¡Bienvenido al futuro de la creación de aplicaciones! Esta es una plataforma impulsada por LLM que crea sin esfuerzo otras aplicaciones impulsadas por LLM.")

    descripcion_app_usuario = st.text_area(label= "Describe la aplicación que necesitas a continuación: ", key= "appinput",
            placeholder="Ej. Una aplicación que me da ideas para videos de YouTube sobre un tema dado...")

    if st.button("Crear"):

        sistema_prompt_app = """Eres streamlitGPT, tu trabajo es ayudar a un usuario a generar una aplicación simple en Streamlit impulsada por LLM. El usuario te describirá lo que hará la aplicación. Luego tomarás esa descripción y generarás un nombre divertido, un emoji para la aplicación, una descripción de la aplicación y el prompt del sistema para el LLM. Debes utilizar este formato exacto como se muestra a continuación para las variables. 

        Tu salida debe ser un diccionario de Python que incluye solo estas variables y nada más. Preséntalo como código de Python. 

        'nombre_app': "El nombre de la aplicación debe ir aquí como una cadena, siempre agrega emojis",
        'emoji_app': "El emoji que mejor se adapte al nombre de la aplicación debe ir aquí",
        'descripcion_app': "Una descripción de la aplicación debe ir aquí como una cadena, diviértete y sé ingenioso",
        'system_prompt': "Eres un chatbot llamado [nombre de la aplicación aquí] que ayuda a los humanos con [describe lo que hará la aplicación]. Tu trabajo es [dale su función].\nHistorial del Chat: [agrega la variable de entrada llamada chat_history delimitada por llaves] \nPregunta del Usuario: [agrega una variable de entrada llamada question delimitada por llaves]",
        'etiqueta_entrada_usuario': "[agrega una etiqueta para la caja de entrada aquí]",
        'placeholder': "Crea un marcador de posición para la caja de entrada de preguntas; este debe ser un ejemplo relevante de entrada del usuario",

        {app_question}
        """
        plantilla_personalizada1 = PromptTemplate(template=sistema_prompt_app, input_variables=["app_question"])

        cadena1 = LLMChain(
        llm = ChatOpenAI (
            temperature=0.2, 
            model_name="gpt-3.5-turbo",
            openai_api_key=api_key,
            ),
        prompt=plantilla_personalizada1,
        verbose="False",
        ) 

        salida_app_str = cadena1.run(app_question=descripcion_app_usuario, return_only_outputs=True)
        salida_app = ast.literal_eval(salida_app_str)

        st.session_state.nombre_app = salida_app['nombre_app']
        st.session_state.emoji_app = salida_app['emoji_app']
        st.session_state.descripcion_app = salida_app['descripcion_app']
        st.session_state.system_prompt = salida_app['system_prompt']
        st.session_state.etiqueta_entrada_usuario = salida_app['etiqueta_entrada_usuario']
        st.session_state.placeholder = salida_app['placeholder']

        # Cambiar la variable de estado después de que se hayan almacenado las variables
        st.session_state["estado"] = "creado"

        st.experimental_rerun()

# Función creada
def creado(api_key):
    # Comprobar el valor de la variable de estado
    if st.session_state["estado"] == "creado":

        if "generado" not in st.session_state:
            st.session_state["generado"] = []

        if "pasado" not in st.session_state:
            st.session_state["pasado"] = []

        st.title(st.session_state.nombre_app)
        st.markdown(f"{st.session_state.emoji_app} {st.session_state.descripcion_app}")

        if "memoria" not in st.session_state:
            st.session_state["memoria"] = ConversationBufferMemory(memory_key="chat_history", input_key= "question")

        entrada_usuario = st.text_input(label=st.session_state.etiqueta_entrada_usuario, placeholder=st.session_state.placeholder)

        if st.button("Entrar"):

            plantilla_personalizada2 = PromptTemplate(template=st.session_state.system_prompt, input_variables=["question", "chat_history"])

            cadena2 = LLMChain(
            llm = ChatOpenAI (
                temperature=0.5, 
                model_name="gpt-3.5-turbo",
                openai_api_key=api_key,
                ),
            prompt=plantilla_personalizada2,
            verbose="False",
            memory = st.session_state.memoria
            ) 

            salida = cadena2.run(question=entrada_usuario, chat_history = st.session_state["memoria"], return_only_outputs=True)

            st.session_state.pasado.append(entrada_usuario)
            st.session_state.generado.append(salida)

            st.markdown(salida)

            if st.session_state["generado"]:
                with st.expander("Ver Historial de Chat"):
                    #st.markdown(st.session_state["generated"])
                    for i in range(len(st.session_state["generado"]) - 1, -1, -1):
                        st.markdown(st.session_state["pasado"][i])
                        st.markdown(st.session_state["generado"][i])

# Función de la aplicación principal
def aplicacion():
    api_key = configurar_clave_api_openai()  # Obtener la clave API de OpenAI
    if api_key:
        if st.session_state.get("estado", "principal") == "principal":
            principal(api_key)
        elif st.session_state["estado"] == "creado":
            creado(api_key)

if __name__ == "__main__":
    aplicacion()
