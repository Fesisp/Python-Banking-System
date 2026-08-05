"""
Módulo de Modelos Orientados a Objetos (OOP) do Sistema Bancário Fesisbank.
Implementa os conceitos de Abstração, Encapsulamento, Herança e Polimorfismo.
"""

from abc import ABC, abstractmethod
from datetime import datetime, date
import hashlib
import os

DIAS_SEMANA_PT = [
    "segunda-feira", "terça-feira", "quarta-feira",
    "quinta-feira", "sexta-feira", "sábado", "domingo"
]


def formatar_data_pt(dt=None):
    """Formata um objeto datetime no padrão brasileiro."""
    if dt is None:
        dt = datetime.now()
    dia_semana = DIAS_SEMANA_PT[dt.weekday()]
    return f"{dia_semana.capitalize()}, {dt.strftime('%d/%m/%Y %H:%M:%S')}"


class Security:
    """Utilitário de segurança para hash e verificação de senhas."""
    
    @staticmethod
    def hash_password(password: str, salt: str = "fesisbank_salt_2026") -> str:
        """Gera um hash SHA-256 para a senha fornecida."""
        salted_pwd = f"{password}{salt}".encode('utf-8')
        return hashlib.sha256(salted_pwd).hexdigest()

    @staticmethod
    def verify_password(password: str, stored_hash: str) -> bool:
        """Verifica se a senha coincide com o hash armazenado."""
        return Security.hash_password(password) == stored_hash


class Historico:
    """Armazena e gerencia o histórico de transações de uma conta."""
    def __init__(self):
        self._transacoes = []

    @property
    def transacoes(self):
        return self._transacoes

    def adicionar_transacao(self, transacao_info: str):
        """Adiciona uma transação ao histórico local."""
        self._transacoes.append(transacao_info)


class Transacao(ABC):
    """Classe abstrata base que representa uma transação bancária."""
    @abstractmethod
    def registrar(self, conta) -> bool:
        pass


class Deposito(Transacao):
    """Representa uma operação de depósito."""
    def __init__(self, valor: float, detalhes: str = "Depósito em conta"):
        self.valor = valor
        self.detalhes = detalhes

    def registrar(self, conta) -> bool:
        if self.valor <= 0:
            print("\n❌ Operação falhou! O valor de depósito deve ser positivo.")
            return False
        conta.saldo += self.valor
        data_str = formatar_data_pt()
        msg = f"{data_str} - Depósito: +R$ {self.valor:.2f} ({self.detalhes})"
        conta.historico.adicionar_transacao(msg)
        return True


class Saque(Transacao):
    """Representa uma operação de saque."""
    def __init__(self, valor: float, detalhes: str = "Saque em caixa eletrônico"):
        self.valor = valor
        self.detalhes = detalhes

    def registrar(self, conta) -> bool:
        if self.valor <= 0:
            print("\n❌ Operação falhou! O valor de saque deve ser positivo.")
            return False
            
        saldo_disponivel = conta.saldo + getattr(conta, 'limite', 0.0)
        if self.valor > saldo_disponivel:
            print("\n❌ Operação falhou! Saldo insuficiente (incluindo limite de crédito).")
            return False
            
        if hasattr(conta, 'limite') and self.valor > conta.limite + conta.saldo:
            print("\n❌ Operação falhou! O valor excede o limite autorizado.")
            return False
            
        if hasattr(conta, 'pode_sacar') and not conta.pode_sacar():
            print("\n❌ Operação falhou! Limite diário de saques atingido.")
            return False

        conta.saldo -= self.valor
        if hasattr(conta, 'incrementar_saque'):
            conta.incrementar_saque()

        data_str = formatar_data_pt()
        msg = f"{data_str} - Saque: -R$ {self.valor:.2f} ({self.detalhes})"
        conta.historico.adicionar_transacao(msg)
        return True


class Transferencia(Transacao):
    """Representa uma operação de transferência entre contas."""
    def __init__(self, valor: float, conta_destino_numero: int, detalhes: str = "Transferência Pix"):
        self.valor = valor
        self.conta_destino_numero = conta_destino_numero
        self.detalhes = detalhes

    def registrar(self, conta_origem) -> bool:
        if self.valor <= 0:
            print("\n❌ Operação falhou! O valor da transferência deve ser positivo.")
            return False
            
        saldo_disponivel = conta_origem.saldo + getattr(conta_origem, 'limite', 0.0)
        if self.valor > saldo_disponivel:
            print("\n❌ Operação falhou! Saldo insuficiente para transferência.")
            return False

        conta_origem.saldo -= self.valor
        data_str = formatar_data_pt()
        msg = f"{data_str} - Transferência Enviada: -R$ {self.valor:.2f} (Para conta {self.conta_destino_numero} - {self.detalhes})"
        conta_origem.historico.adicionar_transacao(msg)
        return True


class Rendimento(Transacao):
    """Representa aplicação de rendimento sobre o saldo de Conta Poupança."""
    def __init__(self, taxa_percentual: float = 0.5):
        self.taxa_percentual = taxa_percentual

    def registrar(self, conta) -> bool:
        if conta.saldo <= 0:
            print("\n⚠️ Não há saldo positivo para aplicar rendimentos.")
            return False
        rendimento = conta.saldo * (self.taxa_percentual / 100.0)
        conta.saldo += rendimento
        data_str = formatar_data_pt()
        msg = f"{data_str} - Rendimento ({self.taxa_percentual}%): +R$ {rendimento:.2f}"
        conta.historico.adicionar_transacao(msg)
        print(f"\n✨ Rendimento de R$ {rendimento:.2f} aplicado com sucesso!")
        return True


class Conta(ABC):
    """Classe abstrata base para contas bancárias."""
    def __init__(self, numero: int, cliente, agencia: str = "0001", saldo: float = 0.0):
        self._saldo = saldo
        self._numero = numero
        self._agencia = agencia
        self._cliente = cliente
        self._historico = Historico()

    @property
    def saldo(self):
        return self._saldo

    @saldo.setter
    def saldo(self, valor):
        self._saldo = valor

    @property
    def numero(self):
        return self._numero

    @property
    def agencia(self):
        return self._agencia

    @property
    def cliente(self):
        return self._cliente

    @property
    def historico(self):
        return self._historico

    @classmethod
    def nova_conta(cls, cliente, numero: int, tipo: str = "CORRENTE"):
        if tipo.upper() == "POUPANCA":
            return ContaPoupanca(numero, cliente)
        return ContaCorrente(numero, cliente)


class ContaCorrente(Conta):
    """Conta Corrente com suporte a limite de cheque especial e saques diários."""
    def __init__(self, numero: int, cliente, agencia: str = "0001", saldo: float = 0.0,
                 limite: float = 500.0, limite_saques: int = 3, saques_hoje: int = 0, data_ultimo_saque: str = None):
        super().__init__(numero, cliente, agencia, saldo)
        self.limite = limite
        self.limite_saques = limite_saques
        self.saques_hoje = saques_hoje
        self.data_ultimo_saque = data_ultimo_saque or date.today().isoformat()
        self._verificar_reset_diario()

    def _verificar_reset_diario(self):
        """Reseta o contador de saques diários se virou o dia."""
        hoje_str = date.today().isoformat()
        if self.data_ultimo_saque != hoje_str:
            self.saques_hoje = 0
            self.data_ultimo_saque = hoje_str

    def pode_sacar(self) -> bool:
        self._verificar_reset_diario()
        return self.saques_hoje < self.limite_saques

    def incrementar_saque(self):
        self._verificar_reset_diario()
        self.saques_hoje += 1


class ContaPoupanca(Conta):
    """Conta Poupança com rendimento mensal/periódico."""
    def __init__(self, numero: int, cliente, agencia: str = "0001", saldo: float = 0.0):
        super().__init__(numero, cliente, agencia, saldo)
        self.limite = 0.0
        self.limite_saques = 5

    def aplicar_rendimento(self, taxa: float = 0.5):
        transacao = Rendimento(taxa)
        return transacao.registrar(self)


class Cliente(ABC):
    """Classe base para clientes do banco."""
    def __init__(self, endereco: str, telefone: str = ""):
        self.endereco = endereco
        self.telefone = telefone
        self.contas = []

    def realizar_transacao(self, conta: Conta, transacao: Transacao) -> bool:
        return transacao.registrar(conta)

    def adicionar_conta(self, conta: Conta):
        self.contas.append(conta)


class PessoaFisica(Cliente):
    """Cliente Pessoa Física."""
    def __init__(self, cpf: str, nome: str, data_nascimento, endereco: str, telefone: str = "", senha_hash: str = ""):
        super().__init__(endereco, telefone)
        self.cpf = cpf
        self.nome = nome
        self.data_nascimento = data_nascimento
        self.senha_hash = senha_hash
