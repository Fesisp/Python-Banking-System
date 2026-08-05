"""
Suíte de Testes Automatizados para o Fesisbank
Testa persistência, regras de negócio OOP, transferências atômicas e autenticação.
"""

import unittest
import os
import sqlite3
from datetime import date, datetime

# Usar um banco de dados temporário para testes
import db
db.DB_PATH = os.path.join(os.path.dirname(__file__), "test_fesisbank.db")
db.init_db()

import banking_service as service
from models import Security, ContaCorrente, ContaPoupanca


class TestBankingSystem(unittest.TestCase):

    def setUp(self):
        """Limpar o banco de dados de teste antes de cada teste."""
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM transacoes")
            cursor.execute("DELETE FROM contas")
            cursor.execute("DELETE FROM usuarios")
            conn.commit()

    def tearDown(self):
        """Limpar arquivo temporário de teste após execução de todos os testes."""
        if os.path.exists(db.DB_PATH):
            try:
                os.remove(db.DB_PATH)
            except OSError:
                pass

    def test_cadastrar_e_autenticar_cliente(self):
        """Testa o cadastro de novo cliente e verificação de senha hash."""
        ok, msg = service.cadastrar_cliente(
            cpf="12345678901",
            nome="Felipe Spinola",
            data_nascimento="01/01/1995",
            endereco="Rua Teste, 100",
            telefone="11999998888",
            senha="senha_segura_123"
        )
        self.assertTrue(ok)
        self.assertEqual(msg, "Cliente cadastrado com sucesso!")

        # Autenticação bem sucedida
        cliente, auth_msg = service.autenticar_cliente("12345678901", "senha_segura_123")
        self.assertIsNotNone(cliente)
        self.assertEqual(cliente.nome, "Felipe Spinola")

        # Autenticação com senha incorreta
        cliente_invalido, auth_err = service.autenticar_cliente("12345678901", "senha_errada")
        self.assertIsNone(cliente_invalido)
        self.assertEqual(auth_err, "Senha incorreta!")

    def test_alterar_senha(self):
        """Testa a alteração de senha de usuário."""
        service.cadastrar_cliente("11122233344", "Maria Silva", "10/10/1990", "Rua A", "11900001111", "senha123")
        
        ok, msg = service.alterar_senha("11122233344", "senha123", "nova_senha_456")
        self.assertTrue(ok)

        # Login com senha antiga deve falhar
        c1, _ = service.autenticar_cliente("11122233344", "senha123")
        self.assertIsNone(c1)

        # Login com nova senha deve funcionar
        c2, _ = service.autenticar_cliente("11122233344", "nova_senha_456")
        self.assertIsNotNone(c2)

    def test_criar_contas_corrente_e_poupanca(self):
        """Testa a criação de múltiplos tipos de contas para um mesmo cliente."""
        service.cadastrar_cliente("99988877766", "Carlos Eduardo", "05/05/1988", "Rua B", "11977776666", "pass123")
        
        ok1, _, c1 = service.criar_conta("99988877766", tipo_conta="CORRENTE", limite=1000.0)
        self.assertTrue(ok1)
        self.assertIsInstance(c1, ContaCorrente)

        ok2, _, c2 = service.criar_conta("99988877766", tipo_conta="POUPANCA")
        self.assertTrue(ok2)
        self.assertIsInstance(c2, ContaPoupanca)

        contas = service.carregar_contas_cliente("99988877766")
        self.assertEqual(len(contas), 2)

    def test_operacoes_deposito_e_saque(self):
        """Testa operações de depósito e saque com limite diário e cheque especial."""
        service.cadastrar_cliente("55544433322", "Ana Clara", "12/12/2000", "Rua C", "11988887777", "1234")
        _, _, conta = service.criar_conta("55544433322", tipo_conta="CORRENTE", limite=200.0)

        # Depósito
        ok_dep, _ = service.executar_deposito(conta.numero, 500.0, "Depósito Inicial")
        self.assertTrue(ok_dep)

        conta_atual = service.carregar_conta_por_numero(conta.numero)
        self.assertEqual(conta_atual.saldo, 500.0)

        # Saque usando saldo
        ok_saq, _ = service.executar_saque(conta.numero, 300.0)
        self.assertTrue(ok_saq)

        conta_atual = service.carregar_conta_por_numero(conta.numero)
        self.assertEqual(conta_atual.saldo, 200.0)

        # Saque usando cheque especial (saldo + limite)
        ok_saq2, _ = service.executar_saque(conta.numero, 350.0) # Saldo 200, Limite 200 -> total 400
        self.assertTrue(ok_saq2)

        conta_atual = service.carregar_conta_por_numero(conta.numero)
        self.assertEqual(conta_atual.saldo, -150.0)

        # Extrato
        extrato = service.obter_extrato(conta.numero)
        self.assertEqual(len(extrato), 3)

    def test_transferencia_atomica_pix(self):
        """Testa transferência Pix atômica entre duas contas."""
        service.cadastrar_cliente("11111111111", "Remetente", "01/01/1990", "End A", "11111", "pwd1")
        service.cadastrar_cliente("22222222222", "Destinatario", "02/02/1992", "End B", "22222", "pwd2")

        _, _, conta_origem = service.criar_conta("11111111111", "CORRENTE")
        _, _, conta_destino = service.criar_conta("22222222222", "CORRENTE")

        service.executar_deposito(conta_origem.numero, 1000.0)

        # Executar transferência Pix
        ok, msg = service.executar_transferencia(conta_origem.numero, conta_destino.numero, 400.0, "Pagamento do Aluguel")
        self.assertTrue(ok)

        origem_atual = service.carregar_conta_por_numero(conta_origem.numero)
        destino_atual = service.carregar_conta_por_numero(conta_destino.numero)

        self.assertEqual(origem_atual.saldo, 600.0)
        self.assertEqual(destino_atual.saldo, 400.0)

    def test_rendimento_poupanca(self):
        """Testa a aplicação de rendimentos em Conta Poupança."""
        service.cadastrar_cliente("33333333333", "Investidor", "03/03/1993", "End C", "33333", "pwd3")
        _, _, conta_poup = service.criar_conta("33333333333", "POUPANCA")

        service.executar_deposito(conta_poup.numero, 1000.0)
        
        ok, msg = service.aplicar_rendimento(conta_poup.numero, taxa=1.0) # 1% de 1000 = 10
        self.assertTrue(ok)

        poup_atual = service.carregar_conta_por_numero(conta_poup.numero)
        self.assertEqual(poup_atual.saldo, 1010.0)


if __name__ == "__main__":
    unittest.main()
