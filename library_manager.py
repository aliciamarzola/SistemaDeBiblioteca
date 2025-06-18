from datetime import datetime, timedelta
from typing import List, Dict, Optional
import json


class Book:    
    def __init__(self, isbn: str, title: str, author: str, year: int, copies: int = 1):
        self.isbn = isbn
        self.title = title
        self.author = author
        self.year = year
        self.total_copies = copies
        self.available_copies = copies
    
    def __str__(self):
        return f"{self.title} by {self.author} ({self.year}) - ISBN: {self.isbn}"
    
    def to_dict(self):
        return {
            'isbn': self.isbn,
            'title': self.title,
            'author': self.author,
            'year': self.year,
            'total_copies': self.total_copies,
            'available_copies': self.available_copies
        }


class User:    
    def __init__(self, user_id: str, name: str, email: str):
        self.user_id = user_id
        self.name = name
        self.email = email
        self.borrowed_books = []
        self.registration_date = datetime.now()
    
    def __str__(self):
        return f"{self.name} ({self.email}) - ID: {self.user_id}"
    
    def to_dict(self):
        return {
            'user_id': self.user_id,
            'name': self.name,
            'email': self.email,
            'borrowed_books': self.borrowed_books,
            'registration_date': self.registration_date.isoformat()
        }


class Loan:    
    def __init__(self, user_id: str, isbn: str, loan_days: int = 14):
        self.user_id = user_id
        self.isbn = isbn
        self.loan_date = datetime.now()
        self.due_date = self.loan_date + timedelta(days=loan_days)
        self.return_date = None
        self.is_active = True
    
    def return_book(self):
        #Marca o livro como devolvido
        self.return_date = datetime.now()
        self.is_active = False
    
    def is_overdue(self):
        #Verifica se o empréstimo está em atraso
        return self.is_active and datetime.now() > self.due_date
    
    def days_overdue(self):
        #Calcula quantos dias de atraso
        if not self.is_overdue():
            return 0
        return (datetime.now() - self.due_date).days
    
    def to_dict(self):
        #Converte o empréstimo para dicionário
        return {
            'user_id': self.user_id,
            'isbn': self.isbn,
            'loan_date': self.loan_date.isoformat(),
            'due_date': self.due_date.isoformat(),
            'return_date': self.return_date.isoformat() if self.return_date else None,
            'is_active': self.is_active
        }


class LibraryManager:    
    def __init__(self):
        self.books: Dict[str, Book] = {}
        self.users: Dict[str, User] = {}
        self.loans: List[Loan] = []
    
    def add_book(self, isbn: str, title: str, author: str, year: int, copies: int = 1):
        if isbn in self.books:
            # Se o livro já existe, adiciona mais cópias
            self.books[isbn].total_copies += copies
            self.books[isbn].available_copies += copies
            return f"Adicionadas {copies} cópias do livro existente"
        else:
            self.books[isbn] = Book(isbn, title, author, year, copies)
            return f"Livro '{title}' adicionado com sucesso"
    
    def register_user(self, user_id: str, name: str, email: str):
        if user_id in self.users:
            raise ValueError(f"Usuário com ID {user_id} já existe")
        
        # Verifica se email já está em uso
        for user in self.users.values():
            if user.email == email:
                raise ValueError(f"Email {email} já está em uso")
        
        self.users[user_id] = User(user_id, name, email)
        return f"Usuário '{name}' registrado com sucesso"
    
    def borrow_book(self, user_id: str, isbn: str, loan_days: int = 14):
        if user_id not in self.users:
            raise ValueError("Usuário não encontrado")
        
        if isbn not in self.books:
            raise ValueError("Livro não encontrado")
        
        book = self.books[isbn]
        user = self.users[user_id]
        
        if book.available_copies <= 0:
            raise ValueError("Não há cópias disponíveis deste livro")
        
        # Verifica se usuário já tem este livro emprestado
        for loan in self.loans:
            if loan.user_id == user_id and loan.isbn == isbn and loan.is_active:
                raise ValueError("Usuário já possui este livro emprestado")
        
        # Verifica limite de livros por usuário (máximo 5)
        active_loans = [l for l in self.loans if l.user_id == user_id and l.is_active]
        if len(active_loans) >= 5:
            raise ValueError("Usuário atingiu o limite máximo de empréstimos (5 livros)")
        
        # Realiza o empréstimo
        loan = Loan(user_id, isbn, loan_days)
        self.loans.append(loan)
        book.available_copies -= 1
        user.borrowed_books.append(isbn)
        
        return f"Empréstimo realizado: '{book.title}' para {user.name}"
    
    def return_book(self, user_id: str, isbn: str):
        if user_id not in self.users:
            raise ValueError("Usuário não encontrado")
        
        if isbn not in self.books:
            raise ValueError("Livro não encontrado")
        
        # Encontra o empréstimo ativo
        loan = None
        for l in self.loans:
            if l.user_id == user_id and l.isbn == isbn and l.is_active:
                loan = l
                break
        
        if not loan:
            raise ValueError("Empréstimo ativo não encontrado")
        
        # Realiza a devolução
        loan.return_book()
        self.books[isbn].available_copies += 1
        self.users[user_id].borrowed_books.remove(isbn)
        
        overdue_message = ""
        if loan.days_overdue() > 0:
            overdue_message = f" (Devolvido com {loan.days_overdue()} dias de atraso)"
        
        return f"Livro '{self.books[isbn].title}' devolvido por {self.users[user_id].name}{overdue_message}"
    
    def search_books(self, query: str):
        #Busca livros por título ou autor
        results = []
        query_lower = query.lower()
        
        for book in self.books.values():
            if (query_lower in book.title.lower() or 
                query_lower in book.author.lower()):
                results.append(book)
        
        return results
    
    def get_overdue_loans(self):
        #Retorna lista de empréstimos em atraso
        overdue = []
        for loan in self.loans:
            if loan.is_overdue():
                overdue.append(loan)
        return overdue
    
    def get_user_loans(self, user_id: str):
        #Retorna empréstimos ativos de um usuário
        if user_id not in self.users:
            raise ValueError("Usuário não encontrado")
        
        active_loans = []
        for loan in self.loans:
            if loan.user_id == user_id and loan.is_active:
                active_loans.append(loan)
        
        return active_loans
    
    def get_library_stats(self):
        total_books = sum(book.total_copies for book in self.books.values())
        available_books = sum(book.available_copies for book in self.books.values())
        active_loans = len([l for l in self.loans if l.is_active])
        overdue_loans = len(self.get_overdue_loans())
        
        return {
            'total_titles': len(self.books),
            'total_books': total_books,
            'available_books': available_books,
            'registered_users': len(self.users),
            'active_loans': active_loans,
            'overdue_loans': overdue_loans
        }


def main():
    library = LibraryManager()
    
    print("=== Sistema de Gerenciamento de Biblioteca ===\n")
    
    print("Adicionando livros ao acervo...")
    library.add_book("978-0-7475-3269-9", "Harry Potter e a Pedra Filosofal", "J.K. Rowling", 1997, 3)
    library.add_book("978-85-250-4277-1", "Dom Casmurro", "Machado de Assis", 1899, 2)
    library.add_book("978-0-06-112008-4", "1984", "George Orwell", 1949, 2)
    
    print("\nRegistrando usuários...")
    library.register_user("001", "João Silva", "joao@email.com")
    library.register_user("002", "Maria Santos", "maria@email.com")
    
    print("\nRealizando empréstimos...")
    print(library.borrow_book("001", "978-0-7475-3269-9"))
    print(library.borrow_book("002", "978-85-250-4277-1"))
    
    print("\nBuscando livros com 'Harry'...")
    results = library.search_books("Harry")
    for book in results:
        print(f"  - {book}")
    
    print("\nEstatísticas da biblioteca:")
    stats = library.get_library_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print(f"\nDevolvendo livro...")
    print(library.return_book("001", "978-0-7475-3269-9"))
    
    print("\nDemonstração concluída!")


if __name__ == "__main__":
    main()