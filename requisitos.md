# Requisitos do Sistema BiblioTech

## Requisitos Funcionais

| ID | Descrição | Prioridade |
|----|-----------|------------|
| RF01 | O sistema deve permitir o cadastro de livros com título, autor, ISBN, categoria e quantidade de exemplares | Alta |
| RF02 | O sistema deve permitir o cadastro de leitores com nome, CPF, email e telefone | Alta |
| RF03 | O sistema deve permitir que o bibliotecário registre o empréstimo de um exemplar para um leitor | Alta |
| RF04 | O sistema deve calcular automaticamente a data prevista de devolução como 14 dias após o empréstimo | Alta |
| RF05 | O sistema deve verificar a disponibilidade de exemplares antes de registrar um empréstimo | Alta |
| RF06 | O sistema deve permitir que o leitor faça uma reserva quando não houver exemplares disponíveis | Média |
| RF07 | O sistema deve manter uma fila de reservas ordenada pela data de solicitação | Média |
| RF08 | O sistema deve registrar a devolução de um exemplar e atualizar sua disponibilidade no acervo | Alta |
| RF09 | O sistema deve enviar notificação por email ao primeiro leitor da fila de reservas após uma devolução | Média |
| RF10 | O sistema deve permitir a renovação do prazo de empréstimo estendendo a data de devolução em 14 dias | Média |
| RF11 | O sistema deve bloquear renovações quando houver reservas ativas para o título | Alta |
| RF12 | O sistema deve calcular e registrar automaticamente multas por atraso na devolução | Alta |

## Requisitos Não-Funcionais

| ID | Categoria | Descrição | Métrica |
|----|-----------|-----------|---------|
| RNF01 | Desempenho | O sistema deve responder às operações de empréstimo e devolução de forma rápida | Tempo de resposta inferior a 2 segundos |
| RNF02 | Segurança | O sistema deve exigir autenticação para que bibliotecários acessem funções administrativas | Autenticação via usuário e senha com criptografia bcrypt |
| RNF03 | Usabilidade | O sistema deve apresentar mensagens de erro claras e orientativas ao usuário | 100% das operações com feedback textual ao usuário |
| RNF04 | Confiabilidade | O sistema deve garantir a consistência dos dados em caso de falha durante uma operação | Uso de transações atômicas no banco de dados |
| RNF05 | Disponibilidade | O sistema deve estar disponível durante o horário de funcionamento da biblioteca | Disponibilidade mínima de 99% em dias úteis |

## Regras de Negócio

| ID | Descrição |
|----|-----------|
| RN01 | O prazo padrão de empréstimo é de 14 dias corridos a partir da data do registro |
| RN02 | A renovação de um empréstimo só é permitida se não existirem reservas ativas para o mesmo título |
| RN03 | A multa por atraso é de R$ 2,00 por dia, contabilizada a partir do primeiro dia após a data prevista de devolução |
| RN04 | A fila de reservas segue a ordem de chegada (FIFO): o leitor com reserva mais antiga tem prioridade |
| RN05 | Um leitor com multas não pagas não pode realizar novos empréstimos nem renovações |

---

## User Stories

---

**User Story 1**

Como Bibliotecário  
Quero cadastrar novos livros no sistema informando título, autor, ISBN, categoria e quantidade de exemplares  
Para manter o acervo atualizado e disponível para consulta pelos leitores

Critérios de Aceitação:
- [ ] O sistema deve rejeitar o cadastro caso o ISBN informado já esteja registrado
- [ ] Os campos título, autor e ISBN devem ser obrigatórios para concluir o cadastro
- [ ] O sistema deve confirmar o cadastro com uma mensagem de sucesso

Story Points: 3

---

**User Story 2**

Como Bibliotecário  
Quero registrar o empréstimo de um exemplar para um leitor  
Para controlar quais livros estão fora do acervo e garantir o prazo de devolução

Critérios de Aceitação:
- [ ] O sistema deve calcular a data de devolução automaticamente como 14 dias após a data atual
- [ ] O sistema deve impedir o empréstimo se não houver exemplares disponíveis
- [ ] O sistema deve atualizar a quantidade de exemplares disponíveis após o registro

Story Points: 5

---

**User Story 3**

Como Leitor  
Quero fazer uma reserva de um livro que está com todos os exemplares emprestados  
Para garantir minha posição na fila e ser notificado quando o livro estiver disponível

Critérios de Aceitação:
- [ ] O sistema deve permitir a reserva somente quando a quantidade de exemplares disponíveis for zero
- [ ] O sistema deve registrar a data da reserva para ordenar a fila corretamente
- [ ] O leitor deve receber uma confirmação de que foi inserido na fila

Story Points: 5

---

**User Story 4**

Como Leitor  
Quero renovar o prazo do meu empréstimo antes da data de vencimento  
Para evitar multas por atraso sem precisar devolver e retirar o livro novamente

Critérios de Aceitação:
- [ ] O sistema deve bloquear a renovação se houver outro leitor com reserva ativa para o mesmo título
- [ ] O novo prazo de devolução deve ser estendido em 14 dias a partir da data da renovação
- [ ] O sistema deve exibir a nova data de devolução após a renovação ser concluída

Story Points: 3

---

**User Story 5**

Como Bibliotecário  
Quero registrar a devolução de um livro e visualizar automaticamente o valor da multa, se houver atraso  
Para realizar a cobrança correta no momento da devolução

Critérios de Aceitação:
- [ ] O sistema deve calcular a multa multiplicando os dias de atraso por R$ 2,00
- [ ] O valor da multa deve ser exibido antes da confirmação da devolução
- [ ] Caso não haja atraso, o sistema deve informar que não há multa

Story Points: 3

---

**User Story 6**

Como Sistema  
Quero enviar um email automático ao primeiro leitor da fila de reservas após a confirmação de uma devolução  
Para que ele seja informado prontamente sobre a disponibilidade do livro reservado

Critérios de Aceitação:
- [ ] O email deve ser enviado imediatamente após a confirmação da devolução no sistema
- [ ] O conteúdo do email deve incluir o título do livro e o nome do leitor destinatário
- [ ] Caso o envio falhe, o sistema deve registrar o erro sem interromper o fluxo de devolução

Story Points: 8
