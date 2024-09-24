import locale
import textwrap
from abc import ABC, abstractmethod
from datetime import datetime

# Define o local para a formatação de moeda para o Brasil
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

class Cliente:
    def __init__(self, endereco):
        self.endereco = endereco
        self.contas = []

    def realizar_transacao(self, conta, transacao):
        if conta:
            transacao.registrar(conta)
        else:
            print("\n@@@ Conta inválida! @@@")

    def adicionar_conta(self, conta):
        self.contas.append(conta)

    def listar_contas(self):
        for idx, conta in enumerate(self.contas, start=1):
            print(f"[{idx}] Conta: {conta.numero}, Agência: {conta.agencia}, Saldo: {conta.saldo}")

class PessoaFisica(Cliente):
    def __init__(self, nome, data_nascimento, cpf, endereco):
        super().__init__(endereco)
        self.nome = nome
        self.data_nascimento = data_nascimento
        self.cpf = cpf

class Historico:
    def __init__(self):
        self.transacoes = []

    def adicionar_transacao(self, transacao):
        self.transacoes.append({
            "tipo": transacao.__class__.__name__,
            "valor": locale.currency(transacao.valor, grouping=True),
            "data": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        })

class Conta:
    def __init__(self, numero, cliente):
        self._saldo = 0
        self._numero = numero
        self._agencia = "0001"
        self._cliente = cliente
        self._historico = Historico()

    @classmethod
    def nova_conta(cls, cliente, numero):
        return cls(numero, cliente)

    @property
    def saldo(self):
        return locale.currency(self._saldo, grouping=True)

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

    def sacar(self, valor):
        if valor > self._saldo:
            print("\n@@@ Saldo insuficiente! @@@")
            return False
        elif valor > 0:
            self._saldo -= valor
            print(f"\n=== Saque de {locale.currency(valor, grouping=True)} realizado com sucesso! ===")
            return True
        else:
            print("\n@@@ Valor de saque inválido! @@@")
            return False

    def depositar(self, valor):
        if valor > 0:
            self._saldo += valor
            print(f"\n=== Depósito de {locale.currency(valor, grouping=True)} realizado com sucesso! ===")
            return True
        else:
            print("\n@@@ Valor de depósito inválido! @@@")
            return False

class ContaCorrente(Conta):
    def __init__(self, numero, cliente, limite=500, limite_saques=3):
        super().__init__(numero, cliente)
        self._limite = limite
        self._limite_saques = limite_saques

    def sacar(self, valor):
        numero_saques = len([t for t in self.historico.transacoes if t["tipo"] == "Saque"])
        if numero_saques >= self._limite_saques:
            print("\n@@@ Limite de saques excedido! @@@")
            return False
        elif valor > self._limite:
            print("\n@@@ Valor do saque excede o limite permitido! @@@")
            return False
        else:
            return super().sacar(valor)

class Transacao(ABC):
    @property
    @abstractmethod
    def valor(self):
        pass

    @abstractmethod
    def registrar(self, conta):
        pass

class Saque(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        if conta.sacar(self.valor):
            conta.historico.adicionar_transacao(self)

class Deposito(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        if conta.depositar(self.valor):
            conta.historico.adicionar_transacao(self)

def selecionar_conta(cliente):
    if len(cliente.contas) == 0:
        print("\n@@@ Cliente não possui contas cadastradas! @@@")
        return None
    cliente.listar_contas()
    opcao = int(input("Selecione o número da conta: ")) - 1
    if opcao < 0 or opcao >= len(cliente.contas):
        print("\n@@@ Opção inválida! @@@")
        return None
    return cliente.contas[opcao]

def menu():
    return input(textwrap.dedent("""\n
    ================ MENU ================
    [1] Depositar
    [2] Sacar
    [3] Extrato
    [4] Novo cliente
    [5] Nova conta
    [6] Listar contas
    [7] Exibir clientes
    [0] Sair
    => """))

def criar_cliente(clientes):
    cpf = input("Informe o CPF: ")
    if next((c for c in clientes if c.cpf == cpf), None):
        print("\n@@@ Cliente já existe! @@@")
        return
    nome = input("Nome completo: ")
    data_nascimento = input("Data de nascimento (dd/mm/aaaa): ")
    endereco = input("Endereço: ")
    cliente = PessoaFisica(nome, data_nascimento, cpf, endereco)
    clientes.append(cliente)
    print("\n=== Cliente criado com sucesso! ===")

def criar_conta(clientes, contas):
    cpf = input("Informe o CPF do cliente: ")
    cliente = next((c for c in clientes if c.cpf == cpf), None)
    if cliente is None:
        print("\n@@@ Cliente não encontrado! @@@")
        return
    numero = len(contas) + 1
    conta = ContaCorrente.nova_conta(cliente, numero)
    cliente.adicionar_conta(conta)
    contas.append(conta)
    print("\n=== Conta criada com sucesso! ===")

def listar_contas(contas):
    if not contas:
        print("\n@@@ Não há contas cadastradas! @@@")
        return
    for conta in contas:
        print(f"\nConta: {conta.numero}, Agência: {conta.agencia}, Cliente: {conta.cliente.nome}")

def exibir_clientes(clientes):
    if not clientes:
        print("\n@@@ Não há clientes cadastrados! @@@")
        return
    print("\n===== Lista de Clientes =====")
    for cliente in clientes:
        print(f"\nNome: {cliente.nome}")
        print(f"CPF: {cliente.cpf}")
        print(f"Data de Nascimento: {cliente.data_nascimento}")
        print(f"Endereço: {cliente.endereco}")
        print(f"Contas: {len(cliente.contas)}")

def depositar(clientes):
    cpf = input("CPF do cliente: ")
    cliente = next((c for c in clientes if c.cpf == cpf), None)
    if cliente is None:
        print("\n@@@ Cliente não encontrado! @@@")
        return
    conta = selecionar_conta(cliente)
    if conta:
        valor = float(input("Valor do depósito: "))
        transacao = Deposito(valor)
        cliente.realizar_transacao(conta, transacao)

def sacar(clientes):
    cpf = input("CPF do cliente: ")
    cliente = next((c for c in clientes if c.cpf == cpf), None)
    if cliente is None:
        print("\n@@@ Cliente não encontrado! @@@")
        return
    conta = selecionar_conta(cliente)
    if conta:
        valor = float(input("Valor do saque: "))
        transacao = Saque(valor)
        cliente.realizar_transacao(conta, transacao)

def exibir_extrato(clientes):
    cpf = input("CPF do cliente: ")
    cliente = next((c for c in clientes if c.cpf == cpf), None)
    if cliente is None:
        print("\n@@@ Cliente não encontrado! @@@")
        return
    conta = selecionar_conta(cliente)
    if conta:
        print("\n====== Extrato ======")
        for transacao in conta.historico.transacoes:
            print(f"{transacao['tipo']} de {transacao['valor']} em {transacao['data']}")
        print(f"Saldo atual: {conta.saldo}")

def main():
    clientes = []
    contas = []

    while True:
        opcao = menu()

        match opcao:
            case "1":
                depositar(clientes)
            case "2":
                sacar(clientes)
            case "3":
                exibir_extrato(clientes)
            case "4":
                criar_cliente(clientes)
            case "5":
                criar_conta(clientes, contas)
            case "6":
                listar_contas(contas)
            case "7":
                exibir_clientes(clientes)
            case "8":
                print("Saindo...")
                break
            case _:
                print("Operação inválida, por favor selecione novamente a operação desejada.")

main()