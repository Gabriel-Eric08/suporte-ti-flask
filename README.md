# 🧰 Sistema de Suporte de TI

Aplicação web desenvolvida em **Flask** para gestão de chamados de suporte técnico em empresas.  
Permite que usuários abram chamados, acompanhem seu andamento e que administradores gerenciem atendimentos de forma centralizada.

---

## 🚀 Funcionalidades

### 👤 Usuário comum
- Login com **usuário e senha**.  
- Abertura de novos chamados:  
  - Seleção de **setor** (para indicar onde está o problema).  
  - Escolha do **tipo de problema**.  
  - Campo de **descrição adicional** ou opção **“Outros”** para texto livre.  
- Exibição da **posição na fila** após enviar o chamado.  
- Acesso à aba **“Meus Chamados”**, com:  
  - Lista de todos os chamados abertos pelo usuário.  
  - Filtros de busca.  
  - Opções para **visualizar detalhes** ou **cancelar** o chamado.  
  - Detalhes incluem: funcionário que atendeu, horários de abertura, atendimento e conclusão.

### 🛠️ Administrador
- Acesso restrito à aba **“Administrador”**.  
- Visualização de **todos os chamados** do sistema.  
- Opções para **atender**, **cancelar** ou **concluir** chamados.  
- Possibilidade de visualizar detalhes completos de cada chamado.  

---

## 🗄️ Estrutura de Dados

- Banco de dados: **MySQL**
- ORM: **SQLAlchemy**
- Principais tabelas:
  - `usuarios` → login, senha, permissões (admin ou usuário comum)
  - `chamados` → setor, tipo de problema, descrição, status, horários e responsável pelo atendimento

---

## ⚙️ Tecnologias Utilizadas

| Tecnologia | Descrição |
|-------------|------------|
| **Python 3** | Linguagem principal |
| **Flask** | Framework web |
| **SQLAlchemy** | ORM para integração com MySQL |
| **MySQL** | Banco de dados |
| **HTML / CSS / JS** | Interface web |

---

## 🧩 Estrutura do Projeto

```bash
📦 suporte-ti
├── app.py                # Ponto de entrada principal da aplicação Flask
├── models.py             # Modelos SQLAlchemy
├── routes/
│   ├── auth.py           # Rotas de autenticação
│   ├── chamados.py       # Rotas de abertura e listagem de chamados
│   └── admin.py          # Rotas da área administrativa
├── templates/            # Páginas HTML com Jinja2
├── static/               # CSS, JS e imagens
└── requirements.txt      # Dependências do projeto
