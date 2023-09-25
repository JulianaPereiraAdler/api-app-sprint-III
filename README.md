# API do Portal de Cadastro da Gestora X (MVP - Sprint 3)

### Introdução

A API do Portal de Cadastro de Investimentos foi projetada especificamente para a Gestora X, visando otimizar o processo cadastral de investidores pessoa física. Através de uma interface amigável e processos seguros, os investidores têm à disposição uma ferramenta que lhes permite não só se cadastrar, mas também renovar e acompanhar seu status cadastral.

Funcionalidades Detalhadas:

(i) Cadastro de Investidores:
- Os novos investidores podem iniciar seu processo de cadastro fornecendo informações básicas.
- A API valida os dados inseridos para assegurar consistência e conformidade.

(ii) Acompanhamento de Status:
- Os investidores podem fazer login no portal a qualquer momento para verificar o progresso de seu cadastro.
- Notificações serão enviadas em cada etapa concluída ou se informações adicionais forem necessárias.

(iii) Renovação de Cadastro:
- Uma ferramenta intuitiva permite que os investidores atualizem suas informações pessoais e financeiras conforme necessário.
- Lembretes automáticos são enviados para informar os investidores sobre a necessidade de renovação.

(iv) Submissão de Ficha Cadastral:
- Os investidores preenchem uma ficha detalhada, garantindo que todas as informações relevantes sejam coletadas.
- Suporte para upload de documentos associados à ficha.

(v) Declaração de Investidor Qualificado:
- Possibilidade de auto-declaração como investidor qualificado, juntamente com um processo de validação.
  
(vi) Definição de Perfil de Risco do Cliente:
- Um questionário interativo ajuda a definir o perfil de risco do investidor, garantindo alinhamento com as oportunidades de investimento adequadas.

Esta API foi rigorosamente desenvolvida em consonância com as normativas da Resolução CVM nº 30/21 e Resolução CVM nº 50/21, assegurando integridade, transparência e segurança em todos os processos, especialmente em relação à prevenção de atividades ilícitas.

---
### Tecnologias Utilizadas
Backend: Flask (Python)
Frontend: HTML, CSS, JS

Esta API desenvolvida em Flask para servir uma aplicação desenvolvida em HTML, CSS e JS.



---
### Instalação

Certifique-se de ter todas as bibliotecas Python listadas no `requirements.txt` instaladas. Após clonar o repositório, navegue ao diretório raiz pelo terminal para executar os comandos abaixo.

> É fortemente indicado o uso de ambientes virtuais do tipo [virtualenv](https://virtualenv.pypa.io/en/latest/installation.html).
> No Ambiente Windows foi utilizado o comando (python -m venv env) para a criação do ambiente virtual e o comando (env\Scripts\activate) para ativar o ambiente virtual.

```
(env)$ pip install -r requirements.txt
```
Este comando instala as dependências/bibliotecas, descritas no arquivo `requirements.txt`.

---
### Executando o servidor

Para iniciar a API, execute:

```
(env)$ flask run --host 0.0.0.0 --port 5000
```

Em modo de desenvolvimento é recomendado executar utilizando o parâmetro reload, que reiniciará o servidor automaticamente após uma mudança no código fonte. 

```
(env)$ flask run --host 0.0.0.0 --port 5000 --reload
```

---
### Acesso no browser

Abra o [http://localhost:5000/#/](http://localhost:5000/#/) no navegador para verificar o status da API em execução.

---
## Como executar através do Docker

Certifique-se de ter o [Docker](https://docs.docker.com/engine/install/) instalado e em execução em sua máquina.

Navegue até o diretório que contém o Dockerfile e o requirements.txt no terminal.
Execute **como administrador** o seguinte comando para construir a imagem Docker:

```
$ docker build -t rest-api_app .
```

Uma vez criada a imagem, para executar o container basta executar, **como administrador**, seguinte o comando:

```
$ docker run -p 5000:5000 rest-api_app
```

Uma vez executando, para acessar a API, basta abrir o [http://localhost:5000/#/](http://localhost:5000/#/) no navegador.



### Alguns comandos úteis do Docker

>**Para verificar se a imagem foi criada** você pode executar o seguinte comando:
>
>```
>$ docker images
>```
>
> Caso queira **remover uma imagem**, basta executar o comando:
>```
>$ docker rmi <IMAGE ID>
>```
>Subistituindo o `IMAGE ID` pelo código da imagem
>
>**Para verificar se o container está em exceução** você pode executar o seguinte comando:
>
>```
>$ docker container ls --all
>```
>
> Caso queira **parar um conatiner**, basta executar o comando:
>```
>$ docker stop <CONTAINER ID>
>```
>Subistituindo o `CONTAINER ID` pelo ID do conatiner
>
>
> Caso queira **destruir um conatiner**, basta executar o comando:
>```
>$ docker rm <CONTAINER ID>
>```
>Para mais comandos, veja a [documentação do docker](https://docs.docker.com/engine/reference/run/).

