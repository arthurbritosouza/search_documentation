<h2>Descrição do sistema</h2>

O sistema Search Documentation é capaz de analisar a URL recebida, obtendo total acesso ao conteúdo da documentação. Com base na pergunta fornecida, ele identifica uma palavra-chave relevante e realiza uma pesquisa dentro dos links disponíveis na documentação. Ao encontrar o link mais adequado, o sistema extrai toda a base de texto correspondente e a utiliza como referência para responder de forma precisa à pergunta recebida.

<h2>Como funciona</h2>
<ol>
    <li><strong>Tradução:</strong> As perguntas feitas pelo usuário são traduzidas para o inglês para facilitar o processamento.</li>
    <li><strong>Extração de Palavras-chave:</strong> O chatbot identifica a palavra-chave principal da pergunta.</li>
    <li><strong>Busca de Documentação:</strong> Utiliza BeautifulSoup para analisar links de uma documentação e FAISS para criar uma base de dados vetorial.</li>
    <li><strong>Requisição de URL:</strong> Verifica URLs e garante acesso a links válidos.</li>
    <li><strong>Resposta:</strong> Extrai o conteúdo relevante da documentação e utiliza um modelo de linguagem para responder à pergunta.</li>
</ol>

<h2>Tecnologias Utilizadas</h2>
<ul>
    <li><strong>Python:</strong> Linguagem principal do projeto.</li>
    <li><strong>Streamlit:</strong> Framework para criar a interface do usuário.</li>
    <li><strong>LangChain:</strong> Para gerenciamento de prompts e integração com modelos de linguagem.</li>
    <li><strong>Google Generative AI:</strong> Modelo LLM usado para tradução e respostas.</li>
    <li><strong>FAISS:</strong> Biblioteca para buscas rápidas em vetores.</li>
    <li><strong>BeautifulSoup:</strong> Para extração de links e conteúdo de páginas HTML.</li>
    <li><strong>dotenv:</strong> Para carregar variáveis de ambiente.</li>
</ul>

<h2>Como Usar</h2>
<ol>
    <li>Clone o repositório:</li>
    <pre><code>git clone https://github.com/arthurbritosouza/search_documentation.git</code></pre>
    <li>Instale as dependências:</li>
    <pre><code>pip install -r requirements.txt</code></pre>
    <li>Execute a aplicação:</li>
    <pre><code>streamlit run main.py</code></pre>
    <li>Insira a URL da documentação no campo de entrada e faça sua pergunta no chat.</li>
</ol>
