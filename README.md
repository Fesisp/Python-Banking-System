# Desafio Bancário em Python (DIO / Suzano)

Este projeto implementa um sistema bancário simples em Python, desenvolvido como parte do desafio da plataforma DIO (Digital Innovation One) em parceria com a Suzano. O objetivo é aplicar conceitos de Programação Orientada a Objetos (POO) e lógica de programação.

## 📋 Funcionalidades

O sistema oferece as seguintes operações bancárias:

*   **Gerenciar Clientes**:
    *   Cadastrar novos clientes (Pessoa Física).
    *   Vincular contas a clientes.
*   **Gerenciar Contas**:
    *   Criar novas contas correntes.
    *   Listar contas existentes.
*   **Operações Financeiras**:
    *   **Depósito**: Adicionar fundos à conta.
    *   **Saque**: Retirar fundos (respeitando saldo, limite de valor e limite de saques diários).
    *   **Extrato**: Visualizar histórico de movimentações.

## 🛠️ Tecnologias Utilizadas

*   **Python 3**: Linguagem principal.
*   **Datetime**: Manipulação de datas e horas.
*   **ABC (Abstract Base Classes)**: Implementação de classes abstratas e interfaces.

## 🚀 Como Executar

1.  Certifique-se de ter o Python 3 instalado.
2.  Clone este repositório.
3.  Execute o arquivo principal:

```bash
python main.py
```

## 📂 Estrutura do Projeto

*   `main.py`: Contém todo o código fonte do sistema (Classes de Domínio e Interface de Console).
*   `README.md`: Documentação do projeto.
*   `requirements.txt`: Lista de dependências (Nenhuma externa necessária).

## 📜 Histórico de Versões

*   **Versão 1**: Estrutura inicial e operações básicas.
*   **Versão 2**: Melhorias na lógica e novas validações.
*   **Versão 3**: Versão completa com funcionalidades extras para personalização.
*   **Versão 4 (Atual)**: Refatoração para atender estritamente ao modelo UML proposto no desafio.

## 👤 Autor

Projeto desenvolvido por [Fesisp](https://github.com/Fesisp).
