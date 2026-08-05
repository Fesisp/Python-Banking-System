"""
Camada de Serviços Bancários (Business Logic & Database Integration).
Garante persistência de dados em SQLite e atomicidade nas transações.
"""

import sqlite3
from datetime import datetime, date
from db import get_connection
from models import (
    PessoaFisica, Conta, ContaCorrente, ContaPoupanca,
    Security, Deposito, Saque, Transferencia, Rendimento, formatar_data_pt
)


def cadastrar_cliente(cpf: str, nome: str, data_nascimento: str, endereco: str, telefone: str, senha: str) -> tuple[bool, str]:
    """Cadastra um novo cliente no banco de dados com senha criptografada."""
    cpf_limpo = ''.join(filter(str.isdigit, cpf))
    if not cpf_limpo or len(cpf_limpo) != 11:
        return False, "CPF inválido! Deve conter 11 dígitos numéricos."
        
    if not senha or len(senha) < 4:
        return False, "A senha deve ter no mínimo 4 caracteres."

    senha_hash = Security.hash_password(senha)
    criado_em = datetime.now().isoformat()

    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO usuarios (nome, nascimento, cpf, endereco, telefone, login, senha, criado_em)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (nome, data_nascimento, cpf_limpo, endereco, telefone, cpf_limpo, senha_hash, criado_em))
            conn.commit()
            return True, "Cliente cadastrado com sucesso!"
    except sqlite3.IntegrityError:
        return False, "Já existe um cliente cadastrado com este CPF!"
    except Exception as e:
        return False, f"Erro ao cadastrar cliente: {str(e)}"


def autenticar_cliente(cpf: str, senha: str):
    """Autentica o cliente via CPF e Senha. Retorna instância de PessoaFisica se válido."""
    cpf_limpo = ''.join(filter(str.isdigit, cpf))
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE cpf = ?", (cpf_limpo,))
        row = cursor.fetchone()
        
        if not row:
            return None, "Cliente não encontrado!"
            
        if not Security.verify_password(senha, row["senha"]):
            return None, "Senha incorreta!"

        cliente = PessoaFisica(
            cpf=row["cpf"],
            nome=row["nome"],
            data_nascimento=row["nascimento"],
            endereco=row["endereco"],
            telefone=row["telefone"],
            senha_hash=row["senha"]
        )
        return cliente, "Autenticado com sucesso!"


def alterar_senha(cpf: str, senha_atual: str, nova_senha: str) -> tuple[bool, str]:
    """Altera a senha de um cliente autenticado."""
    cliente, msg = autenticar_cliente(cpf, senha_atual)
    if not cliente:
        return False, msg

    if not nova_senha or len(nova_senha) < 4:
        return False, "A nova senha deve possuir pelo menos 4 caracteres."

    novo_hash = Security.hash_password(nova_senha)
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE usuarios SET senha = ? WHERE cpf = ?", (novo_hash, cliente.cpf))
        conn.commit()
        return True, "Senha alterada com sucesso!"


def criar_conta(cpf_cliente: str, tipo_conta: str = "CORRENTE", limite: float = 500.0) -> tuple[bool, str, object]:
    """Cria uma nova conta (Corrente ou Poupança) associada ao CPF fornecido."""
    cpf_limpo = ''.join(filter(str.isdigit, cpf_cliente))
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE cpf = ?", (cpf_limpo,))
        user_row = cursor.fetchone()
        if not user_row:
            return False, "Cliente não encontrado no sistema!", None

        # Gerar número sequencial para nova conta
        cursor.execute("SELECT MAX(numero_conta) as max_num FROM contas")
        res = cursor.fetchone()
        proximo_numero = (res["max_num"] or 0) + 1
        
        tipo_normalizado = tipo_conta.upper()
        criado_em = datetime.now().isoformat()
        agencia = "0001"

        cursor.execute("""
            INSERT INTO contas (agencia, numero_conta, usuario_login, tipo_conta, saldo, limite, limite_saques, saques_hoje, data_ultimo_saque, criado_em)
            VALUES (?, ?, ?, ?, 0.0, ?, 3, 0, ?, ?)
        """, (agencia, proximo_numero, cpf_limpo, tipo_normalizado, limite, date.today().isoformat(), criado_em))
        conn.commit()

        cliente = PessoaFisica(
            cpf=user_row["cpf"],
            nome=user_row["nome"],
            data_nascimento=user_row["nascimento"],
            endereco=user_row["endereco"]
        )

        if tipo_normalizado == "POUPANCA":
            conta = ContaPoupanca(proximo_numero, cliente, agencia=agencia)
        else:
            conta = ContaCorrente(proximo_numero, cliente, agencia=agencia, limite=limite)

        return True, f"Conta {tipo_normalizado} nº {proximo_numero} criada com sucesso!", conta


def carregar_contas_cliente(cpf_cliente: str) -> list:
    """Carrega todas as contas associadas ao CPF de um cliente."""
    cpf_limpo = ''.join(filter(str.isdigit, cpf_cliente))
    contas = []
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE cpf = ?", (cpf_limpo,))
        user_row = cursor.fetchone()
        if not user_row:
            return []

        cliente = PessoaFisica(
            cpf=user_row["cpf"],
            nome=user_row["nome"],
            data_nascimento=user_row["nascimento"],
            endereco=user_row["endereco"]
        )

        cursor.execute("SELECT * FROM contas WHERE usuario_login = ? ORDER BY numero_conta", (cpf_limpo,))
        rows = cursor.fetchall()
        for r in rows:
            tipo = r["tipo_conta"]
            if tipo == "POUPANCA":
                conta = ContaPoupanca(
                    numero=r["numero_conta"],
                    cliente=cliente,
                    agencia=r["agencia"],
                    saldo=r["saldo"]
                )
            else:
                conta = ContaCorrente(
                    numero=r["numero_conta"],
                    cliente=cliente,
                    agencia=r["agencia"],
                    saldo=r["saldo"],
                    limite=r["limite"],
                    limite_saques=r["limite_saques"],
                    saques_hoje=r["saques_hoje"],
                    data_ultimo_saque=r["data_ultimo_saque"]
                )
            contas.append(conta)
    return contas


def carregar_conta_por_numero(numero_conta: int):
    """Carrega os detalhes de uma conta específica pelo número."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT c.*, u.nome, u.cpf, u.nascimento, u.endereco 
            FROM contas c
            JOIN usuarios u ON c.usuario_login = u.cpf
            WHERE c.numero_conta = ?
        """, (numero_conta,))
        r = cursor.fetchone()
        if not r:
            return None

        cliente = PessoaFisica(
            cpf=r["cpf"],
            nome=r["nome"],
            data_nascimento=r["nascimento"],
            endereco=r["endereco"]
        )

        tipo = r["tipo_conta"]
        if tipo == "POUPANCA":
            return ContaPoupanca(
                numero=r["numero_conta"],
                cliente=cliente,
                agencia=r["agencia"],
                saldo=r["saldo"]
            )
        else:
            return ContaCorrente(
                numero=r["numero_conta"],
                cliente=cliente,
                agencia=r["agencia"],
                saldo=r["saldo"],
                limite=r["limite"],
                limite_saques=r["limite_saques"],
                saques_hoje=r["saques_hoje"],
                data_ultimo_saque=r["data_ultimo_saque"]
            )


def executar_deposito(numero_conta: int, valor: float, detalhes: str = "Depósito em conta") -> tuple[bool, str]:
    """Executa um depósito e o persiste no banco de dados."""
    conta = carregar_conta_por_numero(numero_conta)
    if not conta:
        return False, "Conta não encontrada!"

    deposito = Deposito(valor, detalhes)
    if not deposito.registrar(conta):
        return False, "Falha na operação de depósito."

    data_hora = datetime.now().isoformat()

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE contas SET saldo = ? WHERE numero_conta = ?", (conta.saldo, numero_conta))
        cursor.execute("""
            INSERT INTO transacoes (conta_numero, tipo, valor, detalhes, data_hora)
            VALUES (?, 'DEPÓSITO', ?, ?, ?)
        """, (numero_conta, valor, detalhes, data_hora))
        conn.commit()

    return True, f"Depósito de R$ {valor:.2f} realizado com sucesso!"


def executar_saque(numero_conta: int, valor: float, detalhes: str = "Saque em caixa eletrônico") -> tuple[bool, str]:
    """Executa um saque respeitando regras de saldo/limites e persiste no banco."""
    conta = carregar_conta_por_numero(numero_conta)
    if not conta:
        return False, "Conta não encontrada!"

    saque = Saque(valor, detalhes)
    if not saque.registrar(conta):
        return False, "Operação de saque recusada pelas regras da conta."

    data_hora = datetime.now().isoformat()
    saques_hoje = getattr(conta, 'saques_hoje', 0)
    data_ultimo = getattr(conta, 'data_ultimo_saque', date.today().isoformat())

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE contas 
            SET saldo = ?, saques_hoje = ?, data_ultimo_saque = ?
            WHERE numero_conta = ?
        """, (conta.saldo, saques_hoje, data_ultimo, numero_conta))
        cursor.execute("""
            INSERT INTO transacoes (conta_numero, tipo, valor, detalhes, data_hora)
            VALUES (?, 'SAQUE', ?, ?, ?)
        """, (numero_conta, valor, detalhes, data_hora))
        conn.commit()

    return True, f"Saque de R$ {valor:.2f} realizado com sucesso!"


def executar_transferencia(numero_origem: int, numero_destino: int, valor: float, detalhes: str = "Transferência Pix") -> tuple[bool, str]:
    """Executa uma transferência PIX/TED atômica entre duas contas."""
    if numero_origem == numero_destino:
        return False, "Não é possível transferir para a mesma conta."

    conta_origem = carregar_conta_por_numero(numero_origem)
    conta_destino = carregar_conta_por_numero(numero_destino)

    if not conta_origem:
        return False, "Conta de origem não encontrada."
    if not conta_destino:
        return False, "Conta de destino não encontrada."

    transf = Transferencia(valor, numero_destino, detalhes)
    if not transf.registrar(conta_origem):
        return False, "Saldo/limite insuficiente para a transferência."

    conta_destino.saldo += valor
    data_hora = datetime.now().isoformat()

    conn = get_connection()
    try:
        cursor = conn.cursor()
        conn.execute("BEGIN TRANSACTION")

        # Atualiza conta origem
        cursor.execute("UPDATE contas SET saldo = ? WHERE numero_conta = ?", (conta_origem.saldo, numero_origem))
        # Registrar débito na origem
        cursor.execute("""
            INSERT INTO transacoes (conta_numero, tipo, valor, detalhes, data_hora)
            VALUES (?, 'TRANSFERÊNCIA ENVIADA', ?, ?, ?)
        """, (numero_origem, valor, f"Para conta {numero_destino} ({conta_destino.cliente.nome}) - {detalhes}", data_hora))

        # Atualiza conta destino
        cursor.execute("UPDATE contas SET saldo = ? WHERE numero_conta = ?", (conta_destino.saldo, numero_destino))
        # Registrar crédito no destino
        cursor.execute("""
            INSERT INTO transacoes (conta_numero, tipo, valor, detalhes, data_hora)
            VALUES (?, 'TRANSFERÊNCIA RECEBIDA', ?, ?, ?)
        """, (numero_destino, valor, f"De conta {numero_origem} ({conta_origem.cliente.nome}) - {detalhes}", data_hora))

        conn.commit()
        return True, f"Transferência de R$ {valor:.2f} para {conta_destino.cliente.nome} (Conta {numero_destino}) concluída!"
    except Exception as e:
        conn.rollback()
        return False, f"Falha na transferência bancária: {str(e)}"
    finally:
        conn.close()


def aplicar_rendimento(numero_conta: int, taxa: float = 0.5) -> tuple[bool, str]:
    """Aplica rendimento em Conta Poupança."""
    conta = carregar_conta_por_numero(numero_conta)
    if not conta:
        return False, "Conta não encontrada!"

    if not isinstance(conta, ContaPoupanca):
        return False, "Rendimento aplicável apenas para Contas Poupança!"

    if conta.saldo <= 0:
        return False, "Saldo deve ser maior que zero para rendimento."

    rendimento = conta.saldo * (taxa / 100.0)
    conta.saldo += rendimento
    data_hora = datetime.now().isoformat()

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE contas SET saldo = ? WHERE numero_conta = ?", (conta.saldo, numero_conta))
        cursor.execute("""
            INSERT INTO transacoes (conta_numero, tipo, valor, detalhes, data_hora)
            VALUES (?, 'RENDIMENTO', ?, ?, ?)
        """, (numero_conta, rendimento, f"Rendimento de {taxa}% sob saldo anterior", data_hora))
        conn.commit()

    return True, f"Rendimento de R$ {rendimento:.2f} ({taxa}%) aplicado ao saldo!"


def obter_extrato(numero_conta: int) -> list:
    """Retorna o histórico de transações da conta armazenado no banco."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT tipo, valor, detalhes, data_hora 
            FROM transacoes 
            WHERE conta_numero = ? 
            ORDER BY id ASC
        """, (numero_conta,))
        rows = cursor.fetchall()
        return [dict(r) for r in rows]
