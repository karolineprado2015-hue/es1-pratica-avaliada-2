# Análise de Design — GerenciadorEmprestimo

---

## 1. Violações dos Princípios SOLID

### SRP — Single Responsibility Principle
A classe `GerenciadorEmprestimo` acumula responsabilidades que deveriam pertencer a classes distintas:
- Gerencia conexões com o banco de dados
- Executa queries SQL diretamente
- Aplica regras de negócio (cálculo de multas, prazos)
- Envia emails via SMTP
- Gera arquivos PDF com ReportLab

Cada uma dessas responsabilidades representa uma razão independente para a classe mudar, violando o princípio de responsabilidade única.

### OCP — Open/Closed Principle
O código está fechado para extensão. Para substituir o banco SQLite por PostgreSQL, ou trocar o envio de email por WhatsApp, seria necessário modificar diretamente o interior da classe, em vez de apenas estender seu comportamento via novas implementações.

### DIP — Dependency Inversion Principle
A classe depende diretamente de implementações concretas: `sqlite3`, `smtplib` e `canvas` (ReportLab). O correto seria depender de abstrações (interfaces), permitindo que as implementações sejam injetadas externamente e substituídas sem alterar a classe principal.

---

## 2. Problemas de Coesão e Acoplamento

### Baixa Coesão
Os métodos da classe misturam camadas diferentes da aplicação. O método `realizar_emprestimo`, por exemplo, executa SQL, valida regras de negócio, envia email e gera PDF — tudo em sequência, dentro de uma única função.

### Alto Acoplamento
- O código está fortemente acoplado ao SQLite por meio de queries SQL embutidas diretamente nos métodos.
- A dependência direta do `smtplib` e do `canvas` significa que qualquer mudança nesses serviços externos exige alteração no código-fonte da classe.
- O tratamento de erros com `except: pass` oculta falhas silenciosamente, dificultando a detecção de problemas em produção.

---

## 3. Sugestões de Refatoração

1. **Padrão Repository**: Criar classes separadas (`RepositorioLivro`, `RepositorioLeitor`, `RepositorioEmprestimo`) para isolar toda a lógica de acesso ao banco de dados, deixando a classe principal livre de SQL.

2. **Serviço de Notificação**: Extrair o envio de email para uma classe `ServicoNotificacao` com interface abstrata, permitindo trocar a implementação (email, SMS, push) sem alterar a lógica de negócio.

3. **Serviço de Relatório**: Isolar a geração de PDF em uma classe `ServicoRelatorio`, desacoplando a infraestrutura de documentos da lógica de empréstimos.

4. **Calculadora de Multa**: Extrair o cálculo de multas para uma classe `CalculadoraMulta` dedicada, facilitando testes unitários e eventuais mudanças na regra de cálculo.

5. **Injeção de Dependências**: Passar todas as dependências pelo construtor da classe `GerenciadorEmprestimo`, em vez de instanciá-las internamente, tornando o código testável e extensível.

6. **Tratamento de Erros**: Substituir os blocos `except: pass` por tratamento específico com logs, permitindo rastreabilidade de falhas sem interromper o fluxo principal.
