import sqlite3
import smtplib
import logging
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from reportlab.pdfgen import canvas

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# =============================================================================
# INTERFACES (Abstrações — DIP)
# =============================================================================

class IRepositorio(ABC):
    """Interface base para operações de persistência."""

    @abstractmethod
    def buscar(self, id):
        pass

    @abstractmethod
    def salvar(self, entidade):
        pass


class IServicoNotificacao(ABC):
    """Interface para serviços de notificação."""

    @abstractmethod
    def enviar(self, destinatario: str, assunto: str, mensagem: str):
        pass


class IServicoRelatorio(ABC):
    """Interface para serviços de geração de relatórios."""

    @abstractmethod
    def gerar_comprovante(self, emprestimo_id: int, dados: dict):
        pass


# =============================================================================
# REPOSITÓRIOS — SRP: cada classe lida apenas com sua entidade no banco
# =============================================================================

class RepositorioLivro(IRepositorio):
    """Responsável pelas operações de banco de dados relacionadas a livros."""

    def __init__(self, db_path: str):
        self.db_path = db_path

    def buscar(self, isbn: str):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM livros WHERE isbn = ?", (isbn,))
            return cursor.fetchone()

    def salvar(self, entidade):
        raise NotImplementedError("Use métodos específicos para salvar livros.")

    def atualizar_estoque(self, isbn: str, variacao: int):
        """Incrementa ou decrementa a quantidade de exemplares disponíveis."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE livros SET exemplares_disponiveis = exemplares_disponiveis + ? WHERE isbn = ?",
                (variacao, isbn)
            )
            conn.commit()


class RepositorioLeitor(IRepositorio):
    """Responsável pelas operações de banco de dados relacionadas a leitores."""

    def __init__(self, db_path: str):
        self.db_path = db_path

    def buscar(self, cpf: str):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM leitores WHERE cpf = ?", (cpf,))
            return cursor.fetchone()

    def salvar(self, entidade):
        raise NotImplementedError("Use métodos específicos para salvar leitores.")


class RepositorioEmprestimo(IRepositorio):
    """Responsável pelas operações de banco de dados relacionadas a empréstimos e reservas."""

    def __init__(self, db_path: str):
        self.db_path = db_path

    def buscar(self, emprestimo_id: int):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM emprestimos WHERE id = ?", (emprestimo_id,))
            return cursor.fetchone()

    def salvar(self, entidade: dict) -> int:
        """Registra um novo empréstimo e retorna o ID gerado."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO emprestimos (livro_isbn, leitor_cpf, data_emprestimo, data_devolucao_prevista)
                VALUES (?, ?, ?, ?)
                """,
                (
                    entidade["livro_isbn"],
                    entidade["leitor_cpf"],
                    entidade["data_emprestimo"],
                    entidade["data_devolucao_prevista"],
                )
            )
            conn.commit()
            return cursor.lastrowid

    def salvar_reserva(self, livro_isbn: str, leitor_cpf: str):
        """Registra uma reserva na fila para o livro informado."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO reservas (livro_isbn, leitor_cpf, data_reserva) VALUES (?, ?, ?)",
                (livro_isbn, leitor_cpf, datetime.now().strftime("%Y-%m-%d"))
            )
            conn.commit()

    def salvar_multa(self, emprestimo_id: int, valor: float):
        """Registra uma multa vinculada ao empréstimo informado."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO multas (emprestimo_id, valor) VALUES (?, ?)",
                (emprestimo_id, valor)
            )
            conn.commit()


# =============================================================================
# SERVIÇOS — SRP: cada classe tem uma única responsabilidade
# =============================================================================

class ServicoNotificacaoEmail(IServicoNotificacao):
    """Envia notificações por email via SMTP."""

    def __init__(self, smtp_host: str, smtp_porta: int, usuario: str, senha: str):
        self.smtp_host = smtp_host
        self.smtp_porta = smtp_porta
        self.usuario = usuario
        self.senha = senha

    def enviar(self, destinatario: str, assunto: str, mensagem: str):
        try:
            msg = MIMEText(mensagem)
            msg["Subject"] = assunto
            msg["From"] = self.usuario
            msg["To"] = destinatario

            with smtplib.SMTP(self.smtp_host, self.smtp_porta) as server:
                server.starttls()
                server.login(self.usuario, self.senha)
                server.send_message(msg)

            logger.info(f"Email enviado para {destinatario}")
        except Exception as e:
            logger.error(f"Falha ao enviar email para {destinatario}: {e}")


class ServicoRelatorio(IServicoRelatorio):
    """Gera comprovantes em PDF para os empréstimos realizados."""

    def gerar_comprovante(self, emprestimo_id: int, dados: dict):
        try:
            nome_arquivo = f"comprovante_{emprestimo_id}.pdf"
            c = canvas.Canvas(nome_arquivo)
            c.drawString(100, 750, f"Comprovante de Empréstimo #{emprestimo_id}")
            c.drawString(100, 730, f"Livro: {dados.get('livro', '')}")
            c.drawString(100, 710, f"Leitor: {dados.get('leitor', '')}")
            c.drawString(100, 690, f"Devolução prevista: {dados.get('data_devolucao', '')}")
            c.save()
            logger.info(f"Comprovante gerado: {nome_arquivo}")
        except Exception as e:
            logger.error(f"Falha ao gerar comprovante #{emprestimo_id}: {e}")


class CalculadoraMulta:
    """Responsável exclusivamente pelo cálculo de multas por atraso."""

    VALOR_POR_DIA = 2.0

    def calcular(self, data_prevista_str: str) -> float:
        """Retorna o valor da multa em reais. Retorna 0.0 se não houver atraso."""
        data_prevista = datetime.strptime(data_prevista_str, "%Y-%m-%d")
        dias_atraso = (datetime.now() - data_prevista).days
        return max(0.0, dias_atraso * self.VALOR_POR_DIA)


# =============================================================================
# CLASSE PRINCIPAL REFATORADA — orquestra o fluxo usando injeção de dependências
# =============================================================================

class GerenciadorEmprestimo:
    """
    Orquestra o processo de empréstimo aplicando as regras de negócio.
    Depende de abstrações, não de implementações concretas (DIP).
    """

    def __init__(
        self,
        repo_livro: RepositorioLivro,
        repo_leitor: RepositorioLeitor,
        repo_emprestimo: RepositorioEmprestimo,
        servico_notificacao: IServicoNotificacao,
        servico_relatorio: IServicoRelatorio,
        calculadora_multa: CalculadoraMulta,
    ):
        self.repo_livro = repo_livro
        self.repo_leitor = repo_leitor
        self.repo_emprestimo = repo_emprestimo
        self.notificacao = servico_notificacao
        self.relatorio = servico_relatorio
        self.calculadora = calculadora_multa

    def realizar_emprestimo(self, livro_isbn: str, leitor_cpf: str) -> tuple:
        """
        Tenta realizar o empréstimo. Se o livro não estiver disponível, cria uma reserva.
        Retorna uma tupla (sucesso: bool, mensagem: str).
        """
        livro = self.repo_livro.buscar(livro_isbn)
        if not livro:
            return False, "Livro não encontrado no acervo."

        leitor = self.repo_leitor.buscar(leitor_cpf)
        if not leitor:
            return False, "Leitor não encontrado no cadastro."

        exemplares_disponiveis = livro[4]

        if exemplares_disponiveis > 0:
            data_hoje = datetime.now().strftime("%Y-%m-%d")
            data_devolucao = (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d")

            emprestimo_id = self.repo_emprestimo.salvar({
                "livro_isbn": livro_isbn,
                "leitor_cpf": leitor_cpf,
                "data_emprestimo": data_hoje,
                "data_devolucao_prevista": data_devolucao,
            })

            self.repo_livro.atualizar_estoque(livro_isbn, -1)

            self.notificacao.enviar(
                destinatario=leitor[2],
                assunto="Empréstimo Realizado — BiblioTech",
                mensagem=f"Olá {leitor[1]}, seu empréstimo do livro '{livro[1]}' foi registrado. Devolução prevista: {data_devolucao}."
            )

            self.relatorio.gerar_comprovante(emprestimo_id, {
                "livro": livro[1],
                "leitor": leitor[1],
                "data_devolucao": data_devolucao,
            })

            return True, "Empréstimo realizado com sucesso."

        else:
            self.repo_emprestimo.salvar_reserva(livro_isbn, leitor_cpf)
            return False, "Livro indisponível no momento. Reserva criada com sucesso."
