from abc import ABC, abstractmethod

class Account(ABC):
    def __init__(self, owner, balance):
        self.owner = owner
        self.balance = balance

    def deposit(self, amount):
        self.balance += amount

    @abstractmethod
    def withdraw(self, amount):
        pass

    def check_balance(self):
        return self.balance
