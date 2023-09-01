from os.path import exists
import pandas as pd
FILE_NAME_PRODUCTS = 'history.csv'
FILE_NAME_EXPENSES = 'expenses.csv'

class Load_data_bases:
    def __init__(self):
        self.expenses =  [
            'Имя заказа','Дата' , 'Курс евро [Покупка] [₽]'  , 'Σ Заказа [₽]'  , 'Курс евро [Доставка] [₽]',
            'Доставка До [€]'   , 'Доставка После [€]'       , 'Σ Доставки [₽]', 'Курс евро [Налоги] [₽]'  ,
            'Таможня УСЛУГИ [₽]', 'Таможня СВХ (БЕЗ НДС) [₽]','Таможенный сбор [₽]', 'Банк [₽]']
            
    def _get_data_bases(self):
        if exists('data/'+FILE_NAME_PRODUCTS) and exists('data/'+FILE_NAME_EXPENSES):
            products_db = pd.read_csv('data/'+FILE_NAME_PRODUCTS)
            expenses_db = pd.read_csv('data/'+FILE_NAME_EXPENSES)

        else:
            products_db = pd.DataFrame(columns= ['Сессия', 'Наименование', 'Цена [€]', 'Количество', 'Цена 1С [₽]', 'Цена [₽]', 'Цена с Банком [₽]'] )
            expenses_db = pd.DataFrame(columns= ['Сессия'] + self.expenses)

            products_db = pd.read_csv('data/'+FILE_NAME_PRODUCTS)
            expenses_db = pd.read_csv('data/'+FILE_NAME_EXPENSES)
        return products_db, expenses_db
