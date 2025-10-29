# 💻 Sistema de Suporte de TI – Flask

Este é um sistema web de **suporte técnico interno**, desenvolvido com **Flask** e **MySQL**, que permite o **registro, acompanhamento e gestão de chamados técnicos** dentro de uma empresa.

---

## 🚀 Funcionalidades

### 👤 Usuário comum
- Login com autenticação por **usuário e senha**.
- Abertura de chamados informando:
  - Setor onde ocorreu o problema.
  - Tipo de problema (ou “Outros”, com descrição personalizada).
  - Campo opcional para observações adicionais.
- Exibição da **posição do chamado na fila** logo após o envio.
- Acesso à aba **“Meus Chamados”**, onde é possível:
  - Visualizar todos os chamados abertos.
  - Aplicar filtros de busca.
  - Ver detalhes (quem atendeu, horários de abertura, atendimento e conclusão).
  - Cancelar chamados em andamento.

### 🛠️ Administrador
- Acesso restrito apenas a contas com permissão de **admin**.
- Visualização de **todos os chamados do sistema**.
- Ações disponíveis:
  - Atender chamados.
  - Concluir chamados.
  - Cancelar chamados.
- Acesso aos **detalhes completos** de cada chamado.

---

## 🗂️ Estrutura do Projeto

```yaml
suporte-ti-flask
├── app.py
├── db_config.py
│
├── models/
│ └── models.py
│
├── routes/
│ ├── admin_chamados.py
│ ├── auth.py
│ ├── chamados.py
│ └── client_page.py
│
├── utils/
│ ├── getUsername.py
│ ├── validate_auth.py
│ └── getUsuario.py
│
└── templates/
├── login_page.html
├── home.html
├── client_page.html
├── detalhes_chamado.html
├── admin_page.html
├── admin_acesso_negado.html
└── auth_error.html