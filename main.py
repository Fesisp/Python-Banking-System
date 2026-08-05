"""
Fesisbank - Sistema Bancário Completo com OOP & Persistência em SQLite
Interface de Linha de Comando (CLI) Interativa
"""

import sys
import os
from datetime import datetime
from db import init_db
from models import formatar_data_pt
import banking_service as service

# Garantir inicialização do Banco de Dados
init_db()


def limpar_tela():
    """Limpa a tela do terminal de forma cross-platform."""
    os.system('cls' if os.name == 'nt' else 'clear')


def exibir_cabecalho(titulo: str = "FESISBANK"):
    print("=" * 60)
    print(f"🏦  {titulo.upper()}  🏦".center(60))
    print("=" * 60)


def formatar_moeda(valor: float) -> str:
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


# BACKWARD COMPATIBILITY HELPERS (SE NECESSÁRIO POR SCRIPTS EXTERNOS OU TESTES)
def buscar_cliente_por_cpf(cpf: str):
    """Busca cliente e retorna mock para compatibilidade com versões antigas."""
    contas = service.carregar_contas_cliente(cpf)
    if contas:
        return contas[0].cliente
    return None


def menu_principal():
    while True:
        limpar_tela()
        exibir_cabecalho("Fesisbank - Sistema Bancário Digital")
        print("\n[1] 👤 Cadastrar Novo Cliente")
        print("[2] 🔐 Acessar Minha Conta (Login)")
        print("[3] 📋 Listar Todas as Contas (Consulta Geral)")
        print("[4] ℹ️  Sobre o Sistema")
        print("[5] 🚪 Sair")
        print("-" * 60)

        opcao = input("Selecione uma opção => ").strip()

        if opcao == "1":
            ui_cadastrar_cliente()
        elif opcao == "2":
            ui_login()
        elif opcao == "3":
            ui_listar_todas_contas()
        elif opcao == "4":
            ui_sobre()
        elif opcao == "5":
            print("\nObrigado por utilizar o Fesisbank! Até logo.\n")
            sys.exit(0)
        else:
            input("\n❌ Opção inválida! Pressione ENTER para tentar novamente...")


def ui_cadastrar_cliente():
    limpar_tela()
    exibir_cabecalho("Cadastro de Novo Cliente")
    
    cpf = input("CPF (somente números): ").strip()
    nome = input("Nome completo: ").strip()
    data_nascimento = input("Data de nascimento (DD/MM/AAAA): ").strip()
    endereco = input("Endereço completo: ").strip()
    telefone = input("Telefone / Celular: ").strip()
    senha = input("Crie uma senha (mínimo 4 caracteres): ").strip()

    ok, msg = service.cadastrar_cliente(cpf, nome, data_nascimento, endereco, telefone, senha)
    print(f"\n{'✅' if ok else '❌'} {msg}")
    
    if ok:
        print("\nDeseja abrir uma conta agora?")
        print("[1] Sim (Conta Corrente)")
        print("[2] Sim (Conta Poupança)")
        print("[3] Não (Abrir mais tarde)")
        op_conta = input("=> ").strip()
        if op_conta == "1":
            s_ok, s_msg, conta = service.criar_conta(cpf, tipo_conta="CORRENTE")
            print(f"{'✅' if s_ok else '❌'} {s_msg}")
        elif op_conta == "2":
            s_ok, s_msg, conta = service.criar_conta(cpf, tipo_conta="POUPANCA")
            print(f"{'✅' if s_ok else '❌'} {s_msg}")
            
    input("\nPressione ENTER para voltar ao menu principal...")


def ui_login():
    limpar_tela()
    exibir_cabecalho("Login no Fesisbank")
    
    cpf = input("Informe o CPF: ").strip()
    senha = input("Informe a senha: ").strip()

    cliente, msg = service.autenticar_cliente(cpf, senha)
    if not cliente:
        print(f"\n❌ {msg}")
        input("\nPressione ENTER para continuar...")
        return

    print(f"\n✅ Bem-vindo(a), {cliente.nome}!")
    contas = service.carregar_contas_cliente(cliente.cpf)

    if not contas:
        print("\n⚠️ Você ainda não possui nenhuma conta cadastrada.")
        print("[1] Criar Conta Corrente")
        print("[2] Criar Conta Poupança")
        print("[3] Voltar")
        op = input("=> ").strip()
        if op == "1":
            service.criar_conta(cliente.cpf, "CORRENTE")
            contas = service.carregar_contas_cliente(cliente.cpf)
        elif op == "2":
            service.criar_conta(cliente.cpf, "POUPANCA")
            contas = service.carregar_contas_cliente(cliente.cpf)
        else:
            return

    ui_menu_cliente(cliente, contas)


def ui_menu_cliente(cliente, contas):
    # Selecionar conta padrão (primeira conta)
    conta_atual = contas[0]

    while True:
        # Recarregar dados da conta atual para atualizar saldo/limite
        conta_atual = service.carregar_conta_por_numero(conta_atual.numero)
        limpar_tela()
        tipo_str = "Poupança" if conta_atual.__class__.__name__ == "ContaPoupanca" else "Corrente"
        
        exibir_cabecalho(f"Titular: {cliente.nome}")
        print(f"📌 Agência: {conta_atual.agencia} | Conta Nº: {conta_atual.numero} ({tipo_str})")
        print(f"💰 Saldo Disponível: {formatar_moeda(conta_atual.saldo)}")
        if hasattr(conta_atual, 'limite') and conta_atual.limite > 0:
            print(f"💳 Limite Cheque Especial: {formatar_moeda(conta_atual.limite)}")
        print("-" * 60)
        print("[1] 💵 Depositar")
        print("[2] 💸 Sacar")
        print("[3] 🔄 Transferir (Pix / TED)")
        print("[4] 📜 Ver Extrato")
        if tipo_str == "Poupança":
            print("[5] ✨ Aplicar Rendimento")
        print("[6] 🔀 Alternar / Criar Nova Conta")
        print("[7] 🔑 Alterar Senha")
        print("[8] 🚪 Logout")
        print("=" * 60)

        opcao = input("Escolha uma opção => ").strip()

        if opcao == "1":
            ui_deposito(conta_atual)
        elif opcao == "2":
            ui_saque(conta_atual)
        elif opcao == "3":
            ui_transferencia(conta_atual)
        elif opcao == "4":
            ui_extrato(conta_atual)
        elif opcao == "5" and tipo_str == "Poupança":
            ok, msg = service.aplicar_rendimento(conta_atual.numero, taxa=0.5)
            print(f"\n{'✅' if ok else '❌'} {msg}")
            input("\nPressione ENTER para continuar...")
        elif opcao == "6":
            contas_atualizadas = service.carregar_contas_cliente(cliente.cpf)
            conta_selecionada = ui_gerenciar_contas(cliente, contas_atualizadas)
            if conta_selecionada:
                conta_atual = conta_selecionada
        elif opcao == "7":
            ui_alterar_senha(cliente)
        elif opcao == "8":
            print("\nSessão encerrada com sucesso.")
            break
        else:
            input("\n❌ Opção inválida! Pressione ENTER...")


def ui_deposito(conta):
    print("\n--- OPERAÇÃO DE DEPÓSITO ---")
    try:
        valor = float(input("Digite o valor a depositar (R$): ").replace(",", "."))
        detalhes = input("Descrição / Identificação (opcional): ").strip() or "Depósito via terminal"
        ok, msg = service.executar_deposito(conta.numero, valor, detalhes)
        print(f"\n{'✅' if ok else '❌'} {msg}")
    except ValueError:
        print("\n❌ Valor digitado é inválido!")
    input("\nPressione ENTER para continuar...")


def ui_saque(conta):
    print("\n--- OPERAÇÃO DE SAQUE ---")
    try:
        valor = float(input("Digite o valor a sacar (R$): ").replace(",", "."))
        detalhes = input("Descrição (opcional): ").strip() or "Saque em caixa eletrônico"
        ok, msg = service.executar_saque(conta.numero, valor, detalhes)
        print(f"\n{'✅' if ok else '❌'} {msg}")
    except ValueError:
        print("\n❌ Valor digitado é inválido!")
    input("\nPressione ENTER para continuar...")


def ui_transferencia(conta_origem):
    print("\n--- TRANSFERÊNCIA PIX / TED ---")
    try:
        destino_num = int(input("Digite o número da conta de destino: ").strip())
        valor = float(input("Digite o valor a transferir (R$): ").replace(",", "."))
        detalhes = input("Descrição / Chave Pix (opcional): ").strip() or "Transferência Pix"
        
        ok, msg = service.executar_transferencia(conta_origem.numero, destino_num, valor, detalhes)
        print(f"\n{'✅' if ok else '❌'} {msg}")
    except ValueError:
        print("\n❌ Dados digitados são inválidos!")
    input("\nPressione ENTER para continuar...")


def ui_extrato(conta):
    limpar_tela()
    exibir_cabecalho(f"Extrato da Conta Nº {conta.numero}")
    transacoes = service.obter_extrato(conta.numero)

    if not transacoes:
        print("\n📭 Nenhuma movimentação registrada nesta conta.")
    else:
        print(f"{'DATA / HORA':<22} | {'TIPO':<22} | {'VALOR':<14} | DETAILS")
        print("-" * 75)
        for t in transacoes:
            try:
                dt_obj = datetime.fromisoformat(t["data_hora"])
                dt_fmt = dt_obj.strftime("%d/%m/%Y %H:%M")
            except Exception:
                dt_fmt = t["data_hora"][:16]

            sinal = "-" if "SAQUE" in t["tipo"] or "ENVIADA" in t["tipo"] else "+"
            cor_val = f"{sinal} {formatar_moeda(t['valor'])}"
            print(f"{dt_fmt:<22} | {t['tipo']:<22} | {cor_val:<14} | {t['detalhes']}")

    print("-" * 75)
    conta_atualizada = service.carregar_conta_por_numero(conta.numero)
    print(f"💰 SALDO ATUAL: {formatar_moeda(conta_atualizada.saldo)}")
    input("\nPressione ENTER para voltar ao menu...")


def ui_gerenciar_contas(cliente, contas):
    print("\n--- SUAS CONTAS BANCÁRIAS ---")
    for idx, c in enumerate(contas, 1):
        tipo = "Poupança" if c.__class__.__name__ == "ContaPoupanca" else "Corrente"
        print(f"[{idx}] Conta {tipo} Nº {c.numero} | Saldo: {formatar_moeda(c.saldo)}")
    print(f"[{len(contas)+1}] ➕ Criar Nova Conta Corrente")
    print(f"[{len(contas)+2}] ➕ Criar Nova Conta Poupança")
    print(f"[{len(contas)+3}] Voltar")

    op = input("=> ").strip()
    try:
        idx = int(op)
        if 1 <= idx <= len(contas):
            return contas[idx - 1]
        elif idx == len(contas) + 1:
            ok, msg, c = service.criar_conta(cliente.cpf, "CORRENTE")
            print(f"\n{'✅' if ok else '❌'} {msg}")
            return c
        elif idx == len(contas) + 2:
            ok, msg, c = service.criar_conta(cliente.cpf, "POUPANCA")
            print(f"\n{'✅' if ok else '❌'} {msg}")
            return c
    except ValueError:
        pass
    return None


def ui_alterar_senha(cliente):
    print("\n--- ALTERAR SENHA DE ACESSO ---")
    senha_atual = input("Digite sua senha atual: ").strip()
    nova_senha = input("Digite sua NOVA senha: ").strip()
    
    ok, msg = service.alterar_senha(cliente.cpf, senha_atual, nova_senha)
    print(f"\n{'✅' if ok else '❌'} {msg}")
    input("\nPressione ENTER para continuar...")


def ui_listar_todas_contas():
    limpar_tela()
    exibir_cabecalho("Consulta de Contas Cadastradas")
    from db import get_connection
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT c.numero_conta, c.agencia, c.tipo_conta, c.saldo, u.nome, u.cpf
            FROM contas c
            JOIN usuarios u ON c.usuario_login = u.cpf
            ORDER BY c.numero_conta ASC
        """)
        rows = cursor.fetchall()
        
        if not rows:
            print("\n📭 Nenhuma conta cadastrada no sistema.")
        else:
            for r in rows:
                print(f"Agência: {r['agencia']} | Conta Nº: {r['numero_conta']} ({r['tipo_conta']})")
                print(f"Titular: {r['nome']} (CPF: {r['cpf']})")
                print(f"Saldo: {formatar_moeda(r['saldo'])}")
                print("=" * 45)

    input("\nPressione ENTER para voltar ao menu principal...")


def ui_sobre():
    limpar_tela()
    exibir_cabecalho("Sobre o Fesisbank")
    print("""
    Fesisbank v2.0 - Sistema Bancário Enterprise
    ----------------------------------------------------------
    Desenvolvido por: Felipe da Silva Spinola (Fesisp)
    
    Principais Recursos:
    • Arquitetura Orientada a Objetos (OOP) Completa
    • Persistência Transacional com Banco SQLite3
    • Criptografia e Hashing Seguro de Senhas (SHA-256)
    • Suporte a Múltiplas Contas (Corrente e Poupança)
    • Operações de Depósito, Saque, Pix/TED e Rendimentos
    • Histórico e Extrato Detalhado de Movimentações
    ----------------------------------------------------------
    """)
    input("Pressione ENTER para voltar...")


if __name__ == "__main__":
    try:
        menu_principal()
    except KeyboardInterrupt:
        print("\n\nEncerrando o Fesisbank. Até logo!")
        sys.exit(0)
