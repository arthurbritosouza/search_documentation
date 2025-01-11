import pysqlite3  # Substitui o módulo sqlite3 por pysqlite3
import sys
sys.modules["sqlite3"] = pysqlite3

from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.prompts import PromptTemplate
from langchain_chroma import Chroma
from urllib.parse import urlparse
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import requests
import os


load_dotenv()
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")

def translate(url_doc,text):
    '''Faz a tradução da pergunta'''
    prompt = ChatPromptTemplate.from_messages([
        ('system','traduza essa entrada para inglês,e apenas me retorne a frase em ingles.'),
        MessagesPlaceholder("chat_history",optional=True),
        ('user',text),
        MessagesPlaceholder("agent_scratchpad")
    ])
    chain = prompt | llm
    text_english = chain.invoke([])
    return text_english.content,url_doc

def extract_keyword(text):
    '''
    extract_keyword: Ira extrair a palavra chave da pergunta recebida criando um PromptTemplate.
    Exemplo: 'Como instalo o Transformers?', a palavra chave é Transformers.
    '''
    prompt_templete = PromptTemplate(
        input_variables=["text"],
        template="Extract the main keyword or topic from the following text: {text}. Only return the main keyword."
    )
    chain = prompt_templete | llm
    keyword = chain.invoke(text)
    print("chave:",keyword.content)
    return keyword.content

def search_documentation(url_doc, keyword):
    '''
        1 - A função recebe uma URL de documentação e realiza uma requisição HTTP para obter o conteúdo da página.
        O conteúdo da página é analisado com BeautifulSoup para extrair todos os links contidos na documentação.
        
        2- Utilizo o modelo all-MiniLM-L6-v2 da Hugging Face para criar embeddings dos links da documentação. Esses embeddings são representações vetoriais dos links que permitem comparar sua semelhança com palavras-chave de forma eficiente.
        Criação de banco de dados Chroma:

        3 - Verifica se um banco de dados Chroma já existe para armazenar os embeddings. Se não existir, cria um novo banco de dados com os links da documentação.
        O banco de dados Chroma armazena os embeddings dos links, o que permite fazer buscas rápidas de similaridade.

        4 - Com o banco de dados Chroma criado ou carregado, a função realiza uma busca para encontrar o link mais relevante para a palavra-chave fornecida, com base na similaridade entre a palavra-chave e os embeddings dos links.
        O resultado é o link da documentação que tem maior similaridade com a palavra-chave.
        Retorno:

        5 - Se um link relevante for encontrado, a função retorna a URL da documentação e o conteúdo da página correspondente ao link mais similar.
        Caso contrário, retorna None para indicar que nenhum link correspondente foi encontrado para a palavra-chave.
    '''

    # Pega links da documentação
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    url = requests.get(url_doc, headers=headers)
    resposta = url.text
    soup = BeautifulSoup(resposta, 'html.parser')
    links = soup.find_all('a', href=True)
    link_href = [link['href'] for link in links]
    
    # Modelo do embedding
    model = "all-MiniLM-L6-v2"
    embedding_model = HuggingFaceEmbeddings(model_name=model)
    domain = urlparse(url_doc).netloc
    
    db = Chroma.from_texts(
        texts=link_href,
        embedding=embedding_model,
        persist_directory=None
    )
    print(db._collection.count())
    print('Banco de dados criado com sucesso.')

    # if not os.path.exists(domain):
    #     os.mkdir(domain)
     
    # if not os.path.exists(os.path.join(domain, 'chroma.sqlite3')):
    #     db = Chroma.from_texts(
    #         texts=link_href,
    #         embedding=embedding_model,
    #         persist_directory=domain
    #     )
    #     print(db._collection.count())
    #     print('Banco de dados criado com sucesso.')
    # else:
    #     db = Chroma(
    #         embedding_function=embedding_model,
    #         persist_directory=domain,
    #     )
    #     print(db._collection.count())
    #     print('Banco de dados carregado com sucesso.')
    
    # Busca a similaridade
    result = db.similarity_search(keyword, k=1)
    if result:  
        result_page = result[0].page_content
        print("Página encontrada:", result_page)
        return url_doc, result_page
    else:
        print("Nenhuma correspondência encontrada para o termo:", keyword)
        return None, None

        
def request_url(full_url, url_doc, final):
    '''Tenta diferentes formas de formar a url a url valida'''
    
    print(f"Tentando acessar: {full_url}")
    #verifica se a url é valida ou não
    get_request = requests.get(full_url)
    
    if get_request.status_code == 200:
        print("200 - URL válida encontrada!")
        return full_url
    else:
        print("Erro - URL inválida")
        
        # Primeira tentativa: Adiciona '/' antes do 'final'
        new_full_url = '/'.join(url_doc.split('/')) + '/' + final
        
        # Segunda tentativa: Sem adicionar '/' antes do 'final'
        new_full_url_2 = '/'.join(url_doc.split('/')) + final
        
        # Evita recursão infinita ao verificar se já tentou ambas as opções
        if new_full_url == full_url or new_full_url_2 == full_url:
            print("Recursão finalizada: Nenhuma URL válida encontrada.")
            return None

        # Chamada recursiva para a URL com '/'
        result_with_slash = request_url(new_full_url, url_doc, final)
        if result_with_slash is not None:  # Se a URL com '/' funcionar, retorna
            return result_with_slash
        
        # Chamada recursiva para a URL sem '/'
        result_without_slash = request_url(new_full_url_2, url_doc, final)
        return result_without_slash
        
def get_url(url_doc,url):
    '''Pegando a url para a verificação'''
    #pega o útimo elemnto da url da documentação pega pela vector store
    final = url.split("/")[-1]
    
    #faço uma url que é padrão das documentaçãoes
    full_url = '/'.join(url_doc.split('/')[:-1])+'/'+final
    
    #mando para a função que vai verificar se aa url é correta ou não 
    url_function = request_url(full_url,url_doc,final)

    #apenas retorna  a url da função 
    if url_function:
        return url_function
    else:
        print('não foi')
    
def get_data(url,question):
    '''Com o link em mão é extraido todo o texto da documentação e envianodo essa base de dados para a llm responder em cima dos dados fornecidos'''
    #extrair o texto e limitando em 2000
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    url = requests.get(url, headers=headers)
    soup = BeautifulSoup(url.content, 'html.parser')
    text_content = soup.get_text()
    limited_text_content = text_content[:2000] 

    llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro")
    #Prompr para responder da maneira correta
    prompt = ChatPromptTemplate.from_messages([
        ('system',f'você tem esta base de dados para responder a pergunta {limited_text_content}'),
        ('user',question),
    ])
    
    chain = prompt | llm
    response = chain.invoke({})
    print(response.content)
    return response.content

def main(url_doc,user_input):
    '''Função inicial'''
    question = user_input
    
    text_or_url = translate(url_doc,user_input)
    text_english = text_or_url[0]
    doc_url = text_or_url[1]
    
    keyword = extract_keyword(text_english)
    
    # # Buscar nos links da documentação
    link_doc_keyword = search_documentation(doc_url,keyword)
    link_doc = link_doc_keyword[0]
    link_keyword = link_doc_keyword[1]
    
    url_doc_get = get_url(link_doc,link_keyword)
    
    result = get_data(url_doc_get,question)
    return result

# Exemplo de uso
# response = main("https://laravel.com/docs/11.x/readme","como instalo o laravel?")
# response = main("https://python.langchain.com/api_reference/aws/index.html","como eu crio um agents")
# print(search_documentation("https://laravel.com/docs/11.x/readme",'install'))
# # print(search_documentation("https://python.langchain.com/api_reference/aws/index.html",'agents'))
# print("Resultado final:", response)