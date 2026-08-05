"""
Módulo de Gerenciamento do Banco de Dados SQLite (fesisbank_users.db)
Fornece persistência de dados segura para Clientes, Contas e Transações.
"""

import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "fesisbank_users.db")


def get_connection():
    """Retorna uma conexão ativa com o banco de dados SQLite."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Inicializa ou atualiza as tabelas no banco de dados."""
    with get_connection() as conn:
        cursor = conn.cursor()

        # Tabela de Usuários / Clientes
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                nascimento TEXT,
                cpf TEXT UNIQUE NOT NULL,
                endereco TEXT,
                telefone TEXT,
                login TEXT UNIQUE NOT NULL,
                senha TEXT NOT NULL,
                criado_em TEXT NOT NULL
            )
        """)

        # Tabela de Contas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS contas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agencia TEXT NOT NULL DEFAULT '0001',
                numero_conta INTEGER UNIQUE NOT NULL,
                usuario_login TEXT NOT NULL,
                tipo_conta TEXT NOT NULL DEFAULT 'CORRENTE',
                saldo REAL NOT NULL DEFAULT 0.0,
                limite REAL NOT NULL DEFAULT 500.0,
                limite_saques INTEGER NOT NULL DEFAULT 3,
                saques_hoje INTEGER NOT NULL DEFAULT 0,
                data_ultimo_saque TEXT,
                criado_em TEXT NOT NULL,
                FOREIGN KEY(usuario_login) REFERENCES usuarios(login)
            )
        """)

        # Tabela de Transações / Histórico
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transacoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conta_numero INTEGER NOT NULL,
                tipo TEXT NOT NULL,
                valor REAL NOT NULL,
                detalhes TEXT,
                data_hora TEXT NOT NULL,
                FOREIGN KEY(conta_numero) REFERENCES contas(numero_conta)
            )
        """)

        conn.commit()


# Garantir que o banco de dados é inicializado ao importar o módulo
init_db()
