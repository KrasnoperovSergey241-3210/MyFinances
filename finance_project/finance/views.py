from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from .forms import RegistrationForm, TransactionForm
from .models import Transaction

# Регистрация пользователя
def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.set_password(form.cleaned_data["password"])
            user.save()
            login(request, user)
            return redirect('home')
    else:
        form = RegistrationForm()
    return render(request, 'finance/register.html', {'form': form})

# Авторизация пользователя
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'finance/login.html', {'form': form})

# Главная страница с транзакциями
def home(request):
    if request.user.is_authenticated:
        # Фильтруем транзакции по типу операции
        income_transactions = Transaction.objects.filter(user=request.user, operation_type='income').order_by('-date')
        expense_transactions = Transaction.objects.filter(user=request.user, operation_type='expense').order_by('-date')

        # Вычисляем разницу между доходами и расходами
        total_income = sum(transaction.amount for transaction in income_transactions)
        total_expense = sum(transaction.amount for transaction in expense_transactions)
        balance = total_income - total_expense

        # Обрабатываем форму добавления транзакции
        if request.method == 'POST':
            form = TransactionForm(request.POST)
            if form.is_valid():
                form.instance.user = request.user  # Устанавливаем текущего пользователя
                form.save()
                return redirect('home')  # Перенаправляем на главную страницу после добавления
        else:
            form = TransactionForm()

        return render(request, 'finance/home.html', {
            'income_transactions': income_transactions,
            'expense_transactions': expense_transactions,
            'balance': balance,
            'total_income': total_income,
            'total_expense': total_expense,
            'form': form,
        })
    else:
        return redirect('login')

# Добавление новой транзакции
def add_transaction(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user
            transaction.save()
            return redirect('home')
    else:
        form = TransactionForm()
    return render(request, 'finance/add_transaction.html', {'form': form})