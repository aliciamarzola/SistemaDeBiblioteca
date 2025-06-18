import unittest
from datetime import datetime, timedelta
from library_manager import LibraryManager, Book, User, Loan


class TestLibraryManager(unittest.TestCase):
    """Classe de testes para LibraryManager"""
    
    def setUp(self):
        """Configuração executada antes de cada teste"""
        self.library = LibraryManager()
        
        # Dados de teste
        self.sample_book = {
            'isbn': '978-0-7475-3269-9',
            'title': 'Harry Potter e a Pedra Filosofal',
            'author': 'J.K. Rowling',
            'year': 1997,
            'copies': 2
        }
        
        self.sample_user = {
            'user_id': '001',
            'name': 'João Silva',
            'email': 'joao@email.com'
        }
    
    def test_add_book_new(self):
        """Teste 1: Adicionar novo livro ao acervo"""
        result = self.library.add_book(**self.sample_book)
        
        self.assertIn(self.sample_book['isbn'], self.library.books)
        self.assertEqual(self.library.books[self.sample_book['isbn']].title, self.sample_book['title'])
        self.assertEqual(self.library.books[self.sample_book['isbn']].total_copies, 2)
        self.assertEqual(self.library.books[self.sample_book['isbn']].available_copies, 2)
        self.assertIn("adicionado com sucesso", result)
    
    def test_add_book_existing(self):
        """Teste 2: Adicionar cópias de livro existente"""
        # Adiciona livro inicial
        self.library.add_book(**self.sample_book)
        
        # Adiciona mais cópias
        result = self.library.add_book(
            self.sample_book['isbn'], 
            self.sample_book['title'], 
            self.sample_book['author'], 
            self.sample_book['year'], 
            3
        )
        
        book = self.library.books[self.sample_book['isbn']]
        self.assertEqual(book.total_copies, 5)  # 2 + 3
        self.assertEqual(book.available_copies, 5)
        self.assertIn("Adicionadas 3 cópias", result)
    
    def test_register_user_success(self):
        """Teste 3: Registrar usuário com sucesso"""
        result = self.library.register_user(**self.sample_user)
        
        self.assertIn(self.sample_user['user_id'], self.library.users)
        user = self.library.users[self.sample_user['user_id']]
        self.assertEqual(user.name, self.sample_user['name'])
        self.assertEqual(user.email, self.sample_user['email'])
        self.assertIn("registrado com sucesso", result)
    
    def test_register_user_duplicate_id(self):
        """Teste 4: Tentar registrar usuário com ID duplicado"""
        self.library.register_user(**self.sample_user)
        
        with self.assertRaises(ValueError) as context:
            self.library.register_user(**self.sample_user)
        
        self.assertIn("já existe", str(context.exception))
    
    def test_register_user_duplicate_email(self):
        """Teste 5: Tentar registrar usuário com email duplicado"""
        self.library.register_user(**self.sample_user)
        
        with self.assertRaises(ValueError) as context:
            self.library.register_user('002', 'Maria Santos', self.sample_user['email'])
        
        self.assertIn("já está em uso", str(context.exception))
    
    def test_borrow_book_success(self):
        """Teste 6: Empréstimo bem-sucedido"""
        # Preparar dados
        self.library.add_book(**self.sample_book)
        self.library.register_user(**self.sample_user)
        
        # Realizar empréstimo
        result = self.library.borrow_book(self.sample_user['user_id'], self.sample_book['isbn'])
        
        # Verificações
        book = self.library.books[self.sample_book['isbn']]
        user = self.library.users[self.sample_user['user_id']]
        
        self.assertEqual(book.available_copies, 1)  # 2 - 1
        self.assertIn(self.sample_book['isbn'], user.borrowed_books)
        self.assertEqual(len(self.library.loans), 1)
        self.assertTrue(self.library.loans[0].is_active)
        self.assertIn("Empréstimo realizado", result)
    
    def test_borrow_book_user_not_found(self):
        """Teste 7: Empréstimo com usuário inexistente"""
        self.library.add_book(**self.sample_book)
        
        with self.assertRaises(ValueError) as context:
            self.library.borrow_book('999', self.sample_book['isbn'])
        
        self.assertIn("Usuário não encontrado", str(context.exception))
    
    def test_borrow_book_not_available(self):
        """Teste 8: Empréstimo de livro sem cópias disponíveis"""
        # Adicionar livro com apenas 1 cópia
        self.library.add_book(self.sample_book['isbn'], self.sample_book['title'], 
                            self.sample_book['author'], self.sample_book['year'], 1)
        self.library.register_user(**self.sample_user)
        self.library.register_user('002', 'Maria Santos', 'maria@email.com')
        
        # Primeiro empréstimo (sucesso)
        self.library.borrow_book(self.sample_user['user_id'], self.sample_book['isbn'])
        
        # Segundo empréstimo (deve falhar)
        with self.assertRaises(ValueError) as context:
            self.library.borrow_book('002', self.sample_book['isbn'])
        
        self.assertIn("Não há cópias disponíveis", str(context.exception))
    
    def test_return_book_success(self):
        """Teste 9: Devolução bem-sucedida"""
        # Preparar empréstimo
        self.library.add_book(**self.sample_book)
        self.library.register_user(**self.sample_user)
        self.library.borrow_book(self.sample_user['user_id'], self.sample_book['isbn'])
        
        # Realizar devolução
        result = self.library.return_book(self.sample_user['user_id'], self.sample_book['isbn'])
        
        # Verificações
        book = self.library.books[self.sample_book['isbn']]
        user = self.library.users[self.sample_user['user_id']]
        loan = self.library.loans[0]
        
        self.assertEqual(book.available_copies, 2)  # Volta para 2
        self.assertNotIn(self.sample_book['isbn'], user.borrowed_books)
        self.assertFalse(loan.is_active)
        self.assertIsNotNone(loan.return_date)
        self.assertIn("devolvido", result)
    
    def test_return_book_not_borrowed(self):
        """Teste 10: Tentar devolver livro não emprestado"""
        self.library.add_book(**self.sample_book)
        self.library.register_user(**self.sample_user)
        
        with self.assertRaises(ValueError) as context:
            self.library.return_book(self.sample_user['user_id'], self.sample_book['isbn'])
        
        self.assertIn("Empréstimo ativo não encontrado", str(context.exception))
    
    def test_search_books(self):
        """Teste 11: Busca de livros por título/autor"""
        # Adicionar vários livros
        self.library.add_book('978-1', 'Harry Potter e a Pedra Filosofal', 'J.K. Rowling', 1997)
        self.library.add_book('978-2', 'Harry Potter e a Câmara Secreta', 'J.K. Rowling', 1998)
        self.library.add_book('978-3', '1984', 'George Orwell', 1949)
        
        # Buscar por título
        results = self.library.search_books('Harry')
        self.assertEqual(len(results), 2)
        
        # Buscar por autor
        results = self.library.search_books('Rowling')
        self.assertEqual(len(results), 2)
        
        # Buscar por termo inexistente
        results = self.library.search_books('Inexistente')
        self.assertEqual(len(results), 0)
    
    def test_get_library_stats(self):
        """Teste 12: Estatísticas da biblioteca"""
        # Adicionar dados de teste
        self.library.add_book(**self.sample_book)
        self.library.add_book('978-2', '1984', 'George Orwell', 1949, 1)
        self.library.register_user(**self.sample_user)
        self.library.register_user('002', 'Maria Santos', 'maria@email.com')
        self.library.borrow_book(self.sample_user['user_id'], self.sample_book['isbn'])
        
        stats = self.library.get_library_stats()
        
        self.assertEqual(stats['total_titles'], 2)
        self.assertEqual(stats['total_books'], 3)  # 2 + 1
        self.assertEqual(stats['available_books'], 2)  # 3 - 1 emprestado
        self.assertEqual(stats['registered_users'], 2)
        self.assertEqual(stats['active_loans'], 1)
        self.assertEqual(stats['overdue_loans'], 0)


class TestBookClass(unittest.TestCase):
    """Testes para a classe Book"""
    
    def test_book_creation(self):
        """Teste 13: Criação de livro"""
        book = Book('978-1', 'Teste', 'Autor Teste', 2023, 3)
        
        self.assertEqual(book.isbn, '978-1')
        self.assertEqual(book.title, 'Teste')
        self.assertEqual(book.author, 'Autor Teste')
        self.assertEqual(book.year, 2023)
        self.assertEqual(book.total_copies, 3)
        self.assertEqual(book.available_copies, 3)
    
    def test_book_to_dict(self):
        """Teste 14: Conversão de livro para dicionário"""
        book = Book('978-1', 'Teste', 'Autor Teste', 2023, 2)
        book_dict = book.to_dict()
        
        expected_keys = ['isbn', 'title', 'author', 'year', 'total_copies', 'available_copies']
        for key in expected_keys:
            self.assertIn(key, book_dict)
        
        self.assertEqual(book_dict['isbn'], '978-1')
        self.assertEqual(book_dict['total_copies'], 2)


class TestLoanClass(unittest.TestCase):
    """Testes para a classe Loan"""
    
    def test_loan_creation(self):
        """Teste 15: Criação de empréstimo"""
        loan = Loan('001', '978-1', 14)
        
        self.assertEqual(loan.user_id, '001')
        self.assertEqual(loan.isbn, '978-1')
        self.assertTrue(loan.is_active)
        self.assertIsNone(loan.return_date)
        self.assertEqual((loan.due_date - loan.loan_date).days, 14)
    
    def test_loan_return(self):
        """Teste 16: Devolução de empréstimo"""
        loan = Loan('001', '978-1')
        loan.return_book()
        
        self.assertFalse(loan.is_active)
        self.assertIsNotNone(loan.return_date)
    
    def test_loan_overdue(self):
        """Teste 17: Verificação de atraso"""
        # Criar empréstimo com data de vencimento no passado
        loan = Loan('001', '978-1', 1)
        loan.due_date = datetime.now() - timedelta(days=3)
        
        self.assertTrue(loan.is_overdue())
        self.assertEqual(loan.days_overdue(), 3)
        
        # Devolver o livro
        loan.return_book()
        self.assertFalse(loan.is_overdue())
        self.assertEqual(loan.days_overdue(), 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)