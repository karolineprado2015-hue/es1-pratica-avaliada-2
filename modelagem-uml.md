# Modelagem UML — Sistema BiblioTech

---

## a) Diagrama de Classes

```mermaid
classDiagram
    class Livro {
        -String isbn
        -String titulo
        -String autor
        -String categoria
        -int totalExemplares
        +cadastrar()
        +consultarDisponibilidade()
    }

    class Exemplar {
        -int id
        -String status
        +marcarComoEmprestado()
        +marcarComoDisponivel()
    }

    class Leitor {
        -String cpf
        -String nome
        -String email
        -String telefone
        +cadastrar()
        +verificarPendencias()
    }

    class Emprestimo {
        -int id
        -String dataEmprestimo
        -String dataPrevistaDevolucao
        -String dataDevolucaoReal
        +renovar()
        +registrarDevolucao()
    }

    class Reserva {
        -int id
        -String dataReserva
        -String status
        +cancelar()
        +notificarLeitor()
    }

    class Bibliotecario {
        -String matricula
        -String nome
        -String login
        +registrarEmprestimo()
        +registrarDevolucao()
    }

    class Multa {
        -int id
        -float valor
        -boolean paga
        +calcular()
        +registrarPagamento()
    }

    Livro "1" --> "*" Exemplar : possui
    Exemplar "1" --> "0..1" Emprestimo : vinculado a
    Leitor "1" --> "*" Emprestimo : realiza
    Leitor "1" --> "*" Reserva : solicita
    Livro "1" --> "*" Reserva : recebe
    Emprestimo "1" --> "0..1" Multa : gera
    Bibliotecario "1" --> "*" Emprestimo : processa
```

---

## b) Diagrama de Sequência — Realizar Empréstimo

```mermaid
sequenceDiagram
    actor B as Bibliotecário
    participant S as Sistema
    participant LV as Livro
    participant LT as Leitor
    participant E as Emprestimo

    B->>S: Solicitar empréstimo (isbn, cpf)
    S->>LV: Verificar disponibilidade de exemplar
    LV-->>S: Retorna exemplares disponíveis

    alt Exemplar disponível
        S->>LT: Verificar situação do leitor
        LT-->>S: Leitor sem pendências

        S->>E: Criar registro de empréstimo
        Note over E: data_devolucao = hoje + 14 dias
        E-->>S: Empréstimo registrado com ID

        S->>LV: Decrementar exemplares disponíveis
        LV-->>S: Estoque atualizado

        S-->>B: Empréstimo realizado com sucesso
    else Sem exemplares disponíveis
        S-->>B: Livro indisponível — sugerir reserva
    end
```

---

## c) Diagrama de Atividades — Devolver Livro e Processar Reservas

```mermaid
flowchart TD
    A([Início]) --> B[Bibliotecário registra devolução]
    B --> C[Sistema localiza o empréstimo]
    C --> D{Devolução em atraso?}

    D -- Sim --> E[Calcular multa: dias × R$ 2,00]
    E --> F[Registrar multa no sistema]
    F --> G[Notificar leitor sobre multa por email]
    G --> H[Atualizar exemplar como disponível]

    D -- Não --> H

    H --> I{Existem reservas para este livro?}

    I -- Sim --> J[Buscar primeiro leitor da fila]
    J --> K[Enviar notificação por email ao leitor]
    K --> L[Atualizar status da reserva]
    L --> M([Fim — com notificação])

    I -- Não --> N([Fim — sem notificação])
```
