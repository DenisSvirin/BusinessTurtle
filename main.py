import sys
from os.path import exists
import pandas as pd
import numpy as np
from collections import Counter
from PyQt5 import QtCore, QtGui, QtWidgets, QtSvg
from PyQt5.Qt import *
from style import StyleSheet
from create_table import createTable, group_table
from load_Database import Load_data_bases
import datetime
import re
import xlwt

# File names, window properties, products data
FILE_NAME_PRODUCTS = 'history.csv'
FILE_NAME_EXPENSES = 'expenses.csv'
WINDOW_WIDTH = 1440
WINDOW_HEIGHT = 650
PRODUCTS_WITH_PRICES = {}
EXPENSES = {}
PRODUCTS = {'EPK-15 2mm':   0, 'EPK-15 3mm':   0, 'EPK-15 4mm':       0, 'EPK-15 5mm':   0, 'EPK-15 6mm':   0,
            'EPK-15 8mm':   0, 'EPK-15 10mm':  0, 'EPK-15 12mm':      0, 'EPK-15 15mm':  0, 'EPK-15 20mm':  0,
            'SFK-20 2mm':   0, 'Neopren 2mm':  0, 'Neopren 3mm':      0, 'Neopren 4mm':  0, 'Neopren 5mm':  0,
            'Neopren 6mm':  0, 'Neopren 8mm':  0, 'Neopren 10mm':     0, 'Neopren 12mm': 0, 'Neopren 15mm': 0,
            'Neopren 20mm': 0, 'EPSO 10mm':    0, 'EPSO 10mm [клей]': 0, '------':       0}

def _get_final_prices(products_db, expenses_db):
    '''
    function to calculate final price
    used on edit page
    '''
    # extracting constanst for current session
    euro_buy =  expenses_db['Курс евро [Покупка] [₽]'].values.astype(np.float)
    customs_service =  expenses_db['Таможня УСЛУГИ [₽]'].values.astype(np.float)
    customs_SVX =  expenses_db['Таможня СВХ (БЕЗ НДС) [₽]'].values.astype(np.float)
    delivery_before = expenses_db['Доставка До [€]'].values.astype(np.float)
    delivery_after = expenses_db['Доставка После [€]'].values.astype(np.float)
    euro_delivery = expenses_db['Курс евро [Доставка] [₽]'].values.astype(np.float)
    euro_tax = expenses_db['Курс евро [Налоги] [₽]'].values.astype(np.float)
    customs = customs_SVX + customs_service
    bank = expenses_db['Банк [₽]'].values.astype(np.float)
    order_sum_rub = expenses_db['Σ Заказа [₽]'].values.astype(np.float)
    dilivery_sum_rub = expenses_db['Σ Доставки [₽]'].values.astype(np.float)
    customs = customs_SVX + customs_service
    customs_tax = expenses_db['Таможенный сбор [₽]'].values.astype(np.float)
    # extracting price and amount columns
    prices = products_db['Цена [€]'].values.astype(np.float)
    amount = products_db['Количество'].values.astype(np.float)

    # calculating tax
    tax = ((prices * amount).sum() + delivery_before) * euro_tax
    expenses_db.loc[:,'Налог'] = tax
    # calculating final sum for 1C

    final_sum = (prices * amount).sum() * euro_buy +0.05 * tax + customs_tax + (delivery_before + delivery_after) * euro_delivery + customs

    # calculating final sum with bank
    final_sum_bank = order_sum_rub +0.05 * tax + customs_tax + dilivery_sum_rub + customs + bank

    # calculating final sum with overall sum in Rub
    final_sum_fact = order_sum_rub +0.05 * tax + customs_tax + dilivery_sum_rub + customs

    # Save new price in RUB to old db
    products_db.loc[:, 'Цена 1С [₽]'] = np.round(prices * final_sum / (prices * amount).sum(), 4)
    products_db.loc[:, 'Цена [₽]'] = np.round(prices * final_sum_fact / (prices * amount).sum(), 4)
    products_db.loc[:, 'Цена с Банком [₽]'] = np.round(prices  * final_sum_bank / (prices * amount).sum(), 4)

    return products_db, expenses_db



class Start_Window(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QGridLayout(self)

        # logo
        self.svglogo = QtSvg.QSvgWidget('data/images/logo.svg')
        self.svglogo.setMaximumSize(QSize(256,256))

        # title
        self.heading = QLabel('BUSINESS TURTLE', objectName='heading')
        self.heading.setAlignment(QtCore.Qt.AlignCenter)

        # buttons
        self.button_calc = QPushButton('РАСЧЕТ', objectName='button_calc')
        self.button_analysis = QPushButton('АНАЛИЗ', objectName='button_analysis')
        self.button_edit = QPushButton('РЕДАКТОР', objectName='button_edit')

        # adding widgets to the layout
        self.layout.addWidget(self.svglogo, 0, 0, 1, 3, alignment=QtCore.Qt.AlignCenter)
        self.layout.addWidget(self.heading, 1, 0, 1, 3)
        self.layout.addWidget(self.button_calc, 2, 1)
        self.layout.addWidget(self.button_analysis, 3, 1)
        self.layout.addWidget(self.button_edit, 4, 1)


class Products_Window(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QGridLayout(self)

        # logo
        self.svglogo = QtSvg.QSvgWidget('data/images/logo.svg')
        self.svglogo.setMaximumSize(QSize(64, 70))

        # header
        self.help_text = QLabel('Выберите нужные позиции :', objectName='help_text')

        # 8 checkboxs in the column
        row, column = 2, 0
        for _product in PRODUCTS:
            el = QCheckBox(_product, self)
            PRODUCTS[_product] = el
            if row % 10 == 0 :
                row = 2
                column +=1
            self.layout.addWidget(el, row, column)
            row += 1

        # buttons
        self.button_next = QPushButton('ДАЛЕЕ', objectName='button_next')
        self.button_previous = QPushButton('НАЗАД', objectName='button_previous')

        # adding widgets to the layout
        self.layout.addWidget(self.svglogo, 0, 0, 1, 3, alignment=QtCore.Qt.AlignCenter)
        self.layout.addWidget(self.help_text, 1, 0, 1, 3, alignment=QtCore.Qt.AlignCenter)
        self.layout.addWidget(self.button_next, 11, 2)
        self.layout.addWidget(self.button_previous, 11, 0)


class Input_Prices_Window(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QGridLayout(self)


        self.button_previous = QPushButton('НАЗАД', objectName='button_previous')


    def new_input_prices(self):
        # logo
        self.svglogo = QtSvg.QSvgWidget('data/images/logo.svg')
        self.svglogo.setMaximumSize(QSize(64, 70))

        # buttons
        self.button_next = QPushButton('ДАЛЕЕ', objectName='button_next')

        self.layout.addWidget(self.svglogo, 0, 0, 1, 3, alignment=QtCore.Qt.AlignCenter)

        row, column = 2, 0

        # Creatin list of checked products
        self.names = [i for i in PRODUCTS if PRODUCTS[i].isChecked()]

        self.expenses =  [
            'Имя заказа','Дата' , 'Курс евро [Покупка] [₽]'  , 'Σ Заказа [₽]'       , 'Курс евро [Доставка] [₽]',
            'Доставка До [€]'   , 'Доставка После [€]'       , 'Σ Доставки [₽]'     , 'Курс евро [Налоги] [₽]'  ,
            'Таможня УСЛУГИ [₽]', 'Таможня СВХ (БЕЗ НДС) [₽]', 'Таможенный сбор [₽]', 'Банк [₽]']

        scrollArea = QScrollArea(self)
        scrollArea.setObjectName('scrollArea')
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setObjectName('scrollAreaWidgetContents')

        scrollArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        scrollArea.setWidgetResizable(True)
        ScrollGridLayout = QGridLayout(self.scrollAreaWidgetContents)
        scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.layout.addWidget(scrollArea, 1, 0, 10, 3)

        # regex for validating users input
        reg_ex_number = QRegExp("([0-9]*[.])?[0-9]+")

        #dont validate date corectness ONLY FORMAT
        reg_ex_date = QRegExp("^[0-3]?[0-9]/[0-3]?[0-9]/(?:[0-9]{2})?[0-9]{2}$")

        # flags for category names
        flag_order = True
        flag_delivery = True
        flag_customs = True
        flag_tax = True
        flag_bank = True
        flag_delivery_sum = True

        for _product in self.names + self.expenses:
            # condtioons to ckeep good formating
            if column == 4:
                column = 0
                row += 1
            if _product in ['Курс евро [Доставка] [₽]', 'Курс евро [Налоги] [₽]', 'Таможня УСЛУГИ [₽]', 'Банк [₽]']:
                column = 0
            # ----------

            #  order block
            order = self.names + ['Имя заказа','Дата' , 'Курс евро [Покупка] [₽]'  , 'Σ Заказа [₽]']
            if _product in order:
                if flag_order:
                    flag_order = False

                    scrollArea_Header = QLabel('Заказ')
                    scrollArea_Header.setAlignment(QtCore.Qt.AlignCenter)
                    scrollArea_Header.setObjectName('scrollArea_Header')

                    ScrollGridLayout.addWidget(scrollArea_Header, row, 0, 1, 4)
                    row += 1

                if _product == 'Дата':

                    scrollArea_el = QLabel(_product)
                    scrollArea_el.setObjectName('scrollArea_el')

                    ScrollGridLayout.addWidget(scrollArea_el, row, column)
                    column += 1

                    input_box_price = QLineEdit(self)
                    input_box_price.setPlaceholderText('  Дата [dd/mm/yyyy]')
                    input_validator = QRegExpValidator(reg_ex_date, input_box_price)
                    input_box_price.setValidator(input_validator)

                    ScrollGridLayout.addWidget(input_box_price, row, column, 1, 1)
                    column +=1

                elif _product == 'Имя заказа':

                    scrollArea_el = QLabel(_product)
                    scrollArea_el.setObjectName('scrollArea_el')
                    ScrollGridLayout.addWidget(scrollArea_el, row, column)
                    column +=1

                    input_box_price = QLineEdit(self, placeholderText='  Придумайте имя')

                    ScrollGridLayout.addWidget(input_box_price, row, column, 1, 1)
                    column += 1

                    if column == 4:
                        row += 1

                elif _product == 'Курс евро [Покупка] [₽]':
                    scrollArea_el = QLabel(_product )
                    scrollArea_el.setObjectName('scrollArea_el')

                    ScrollGridLayout.addWidget(scrollArea_el, row, column)
                    column +=1

                    input_box_price = QLineEdit(self)
                    input_box_price.setPlaceholderText('  Цена')

                    input_validator = QRegExpValidator(reg_ex_number, input_box_price)
                    input_box_price.setValidator(input_validator)

                    ScrollGridLayout.addWidget(input_box_price, row, column, 1, 1)
                    column +=1

                elif _product == 'Σ Заказа [₽]':
                    scrollArea_el = QLabel(_product )
                    scrollArea_el.setObjectName('scrollArea_el')
                    ScrollGridLayout.addWidget(scrollArea_el, row, column)
                    column +=1

                    input_box_price = QLineEdit(self)
                    input_box_price.setPlaceholderText('  Цена')
                    input_validator = QRegExpValidator(reg_ex_number, input_box_price)
                    input_box_price.setValidator(input_validator)

                    ScrollGridLayout.addWidget(input_box_price, row, column, 1, 1)
                    column +=1
                else:
                    #print(f"{_product} [€]  -- {row} - {column}") #
                    scrollArea_el = QLabel(_product + ' [€]')
                    scrollArea_el.setObjectName('scrollArea_el')
                    input_box_price = QLineEdit(self)
                    input_box_amount = QLineEdit(self)

                    input_box_price.setPlaceholderText('  Цена')
                    input_validator = QRegExpValidator(reg_ex_number, input_box_price)
                    input_box_price.setValidator(input_validator)

                    input_box_amount.setPlaceholderText('  Количество')
                    input_validator = QRegExpValidator(reg_ex_number, input_box_amount)
                    input_box_amount.setValidator(input_validator)

                    ScrollGridLayout.addWidget(scrollArea_el, row, column)
                    column +=1

                    ScrollGridLayout.addWidget(input_box_price, row, column)
                    ScrollGridLayout.addWidget(input_box_amount, row+1, column)
                    column +=1

                    PRODUCTS_WITH_PRICES[_product] = [input_box_price, input_box_amount]

                    # for good formatting
                    if column == 4:
                        row += 1
            # ----------

            # Delivery block
            delivery = ['Курс евро [Доставка] [₽]', 'Доставка До [€]', 'Доставка После [€]', 'Σ Доставки [₽]']

            if _product in delivery:
                if flag_delivery:
                    flag_delivery = False
                    row += 1
                    scrollArea_Header = QLabel('Доставка')
                    scrollArea_Header.setObjectName('scrollArea_Header')
                    scrollArea_Header.setAlignment(QtCore.Qt.AlignCenter)

                    ScrollGridLayout.addWidget(scrollArea_Header, row, 0, 1, 4)
                    row += 1

                scrollArea_el = QLabel(_product)
                scrollArea_el.setObjectName('scrollArea_el')

                ScrollGridLayout.addWidget(scrollArea_el, row, column)
                column +=1

                input_box_price = QLineEdit(self)
                input_box_price.setPlaceholderText('  Цена')

                input_validator = QRegExpValidator(reg_ex_number, input_box_price)
                input_box_price.setValidator(input_validator)

                ScrollGridLayout.addWidget(input_box_price, row, column, 1, 1)
                column +=1

            if _product in ['Таможня УСЛУГИ [₽]', 'Таможня СВХ (БЕЗ НДС) [₽]', 'Таможенный сбор [₽]']:
                if flag_customs:
                    flag_customs = False
                    row += 1
                    scrollArea_Header = QLabel('Таможня')
                    scrollArea_Header.setObjectName('scrollArea_Header')
                    scrollArea_Header.setAlignment(QtCore.Qt.AlignCenter)

                    ScrollGridLayout.addWidget(scrollArea_Header, row, 0, 1 , 4)
                    row += 1

                scrollArea_el = QLabel(_product )
                scrollArea_el.setObjectName('scrollArea_el')

                ScrollGridLayout.addWidget(scrollArea_el, row, column)
                column +=1

                input_box_price = QLineEdit(self)
                input_box_price.setPlaceholderText('  Цена')

                input_validator = QRegExpValidator(reg_ex_number, input_box_price)
                input_box_price.setValidator(input_validator)

                ScrollGridLayout.addWidget(input_box_price, row, column, 1, 1)
                column +=1

            if _product in ['Курс евро [Налоги] [₽]']:
                if flag_tax:
                    flag_tax = False
                    row += 1
                    scrollArea_Header = QLabel('Налоги')
                    scrollArea_Header.setObjectName('scrollArea_Header')
                    scrollArea_Header.setAlignment(QtCore.Qt.AlignCenter)

                    ScrollGridLayout.addWidget(scrollArea_Header, row, 0, 1 ,4)
                    row += 1

                scrollArea_el = QLabel(_product )
                scrollArea_el.setObjectName('scrollArea_el')

                ScrollGridLayout.addWidget(scrollArea_el, row, column)
                column +=1

                input_box_price = QLineEdit(self)
                input_box_price.setPlaceholderText('  Цена')

                input_validator = QRegExpValidator(reg_ex_number, input_box_price)
                input_box_price.setValidator(input_validator)

                ScrollGridLayout.addWidget(input_box_price, row, column, 1, 1)
                column +=1

            if _product in ['Банк [₽]']:
                if flag_bank:
                    row += 1
                    flag_bank = False
                    scrollArea_Header = QLabel('Банковские Расходы')
                    scrollArea_Header.setObjectName('scrollArea_Header')
                    scrollArea_Header.setAlignment(QtCore.Qt.AlignCenter)

                    ScrollGridLayout.addWidget(scrollArea_Header, row, 0, 1, 4)
                    row += 1

                scrollArea_el = QLabel(_product )
                scrollArea_el.setObjectName('scrollArea_el')

                ScrollGridLayout.addWidget(scrollArea_el, row, column)
                column +=1

                input_box_price = QLineEdit(self)
                input_box_price.setPlaceholderText('  Цена')

                input_validator = QRegExpValidator(reg_ex_number, input_box_price)
                input_box_price.setValidator(input_validator)

                ScrollGridLayout.addWidget(input_box_price, row, column, 1, 1)
                column +=1

            if _product not in self.names:

                EXPENSES[_product] = input_box_price

        # button for price calculations
        self.button_next = QPushButton('ДАЛЕЕ', objectName='button_next')

        #button to go back
        self.button_previous = QPushButton('НАЗАД', objectName='button_previous')

        # adding widgets to the layout
        self.layout.addWidget(self.button_next, 11, 2)
        self.layout.addWidget(self.button_previous, 11, 0)


    def update_products(self):

        # if database exists -> current index -> max from it, else its 0
        if exists('data/'+FILE_NAME_PRODUCTS) and exists('data/'+FILE_NAME_EXPENSES):
            products_db, expenses_db = Load_data_bases()._get_data_bases()
            current_session = int(products_db['Сессия'].max()) + 1

        else:
            products_db, expenses_db = Load_data_bases()._get_data_bases()
            current_session =  0

        row = len(products_db)

        # adding new data to expenses db
        for _element in EXPENSES:
            expenses_db.loc[current_session, 'Сессия'] =  int(current_session)
            expenses_db.loc[current_session, _element] = EXPENSES[_element].text()


        # adding new data to products db
        for _element in PRODUCTS_WITH_PRICES:
            products_db.loc[row] = [current_session, _element, PRODUCTS_WITH_PRICES[_element][0].text(), PRODUCTS_WITH_PRICES[_element][1].text(), None, None, None]
            row += 1


        # creating new db for easier calculations
        new_products_db = products_db[products_db['Сессия'] == current_session]
        new_expenses_db = expenses_db[expenses_db['Сессия'] == current_session]

        # extracting constanst for current session
        euro_buy =  new_expenses_db['Курс евро [Покупка] [₽]'].values.astype(np.float)
        customs_service =  new_expenses_db['Таможня УСЛУГИ [₽]'].values.astype(np.float)
        customs_SVX =  new_expenses_db['Таможня СВХ (БЕЗ НДС) [₽]'].values.astype(np.float)
        delivery_before = new_expenses_db['Доставка До [€]'].values.astype(np.float)
        delivery_after = new_expenses_db['Доставка После [€]'].values.astype(np.float)
        euro_delivery = new_expenses_db['Курс евро [Доставка] [₽]'].values.astype(np.float)
        euro_tax = new_expenses_db['Курс евро [Налоги] [₽]'].values.astype(np.float)
        customs = customs_SVX + customs_service
        bank = new_expenses_db['Банк [₽]'].values.astype(np.float)
        order_sum_rub = new_expenses_db['Σ Заказа [₽]'].values.astype(np.float)
        dilivery_sum_rub = new_expenses_db['Σ Доставки [₽]'].values.astype(np.float)
        customs = customs_SVX + customs_service
        customs_tax = new_expenses_db['Таможенный сбор [₽]'].values.astype(np.float)
        # extracting price and amount columns
        prices = new_products_db['Цена [€]'].values.astype(np.float)
        amount = new_products_db['Количество'].values.astype(np.float)

        # calculating tax

        tax = ((prices * amount).sum() + delivery_before) * euro_tax
        expenses_db.loc[current_session, 'Налог'] = tax

        # calculating final sum for 1C
        final_sum = (prices * amount).sum() * euro_buy +0.05 * tax + customs_tax + (delivery_before + delivery_after) * euro_delivery + customs

        # calculating final sum with bank
        final_sum_bank = order_sum_rub +0.05 * tax + customs_tax + dilivery_sum_rub + customs + bank

        # calculating final sum with overall sum in Rub
        final_sum_fact = order_sum_rub +0.05 * tax + customs_tax + dilivery_sum_rub + customs

        # Save new price in RUB to old db
        products_db.loc[products_db['Сессия'] == current_session, 'Цена 1С [₽]'] = np.round(prices * final_sum      / (prices * amount).sum(), 4)
        products_db.loc[products_db['Сессия'] == current_session, 'Цена [₽]'] = np.round(prices * final_sum_fact / (prices * amount).sum(),4)
        products_db.loc[products_db['Сессия'] == current_session, 'Цена с Банком [₽]'] = np.round(prices  * final_sum_bank / (prices * amount).sum(),4)

        #saving databases
        products_db.to_csv('data/'+FILE_NAME_PRODUCTS, index=False)
        expenses_db.to_csv('data/'+FILE_NAME_EXPENSES, index=False)



class Final_Table_Window(QWidget):
    '''
    Final window. Shows result of the
    calculations in a table
    '''

    def __init__(self):
        super().__init__()
        self.layout = QGridLayout(self)

    def new_table(self):

        # logo
        self.svglogo = QtSvg.QSvgWidget('data/images/logo.svg')
        self.svglogo.setMaximumSize(QSize(64,70))
        self.space = QLabel(objectName='EditSpace')
        self.space.setFixedHeight(15)

        self.layout.addWidget(self.space, 1, 0, 1, 3, alignment=QtCore.Qt.AlignLeft)
        self.layout.addWidget(self.svglogo, 0, 0, 1, 3, alignment=QtCore.Qt.AlignCenter)

        #loading latest dbs
        products_db, expenses_db = Load_data_bases()._get_data_bases()
        products_db = products_db[products_db['Сессия'] == products_db['Сессия'].max()]
        expenses_db = expenses_db[expenses_db['Сессия'] == expenses_db['Сессия'].max()]

        # Date
        date = str(expenses_db['Дата'].values[0])
        date_label = QLabel(date)

        date_label.setStyleSheet('color:#837569;'
                                 'font-size:17px;'
                                 'letter-spacing:4px;'
                                 'font-weight:600;')
        date_label.setAlignment(QtCore.Qt.AlignCenter)
        self.layout.addWidget(date_label, 0,0)

        # Name
        name = str(expenses_db['Имя заказа'].values[0])
        name_label = QLabel(name)

        name_label.setStyleSheet('color:#837569;'
                                 'font-size:17px;'
                                 'letter-spacing:4px;'
                                 'font-weight:600;')
        name_label.setAlignment(QtCore.Qt.AlignCenter)

        self.layout.addWidget(name_label, 0,2)

        # Creating header
        headers = ['Наименование', 'Цена [€]', 'Цена 1С [₽]', 'Цена [₽]', 'Цена с Банком [₽]']

        # Creating table
        tableWidget = QTableWidget()
        tableWidget.setObjectName('mainTableWidget')
        #tableWidget.verticalHeader().setVisible(False)
        tableWidget.setColumnCount(len(headers))
        rows = len(products_db)
        tableWidget.setRowCount(rows)
        tableWidget.setHorizontalHeaderLabels(headers)

        # filling table wit data
        for i in range(rows):
             for j in range(tableWidget.columnCount()):

                col = headers[j]
                if col == 'Цена [€]' or col == 'Цена 1С [₽]':
                    value = QTableWidgetItem("{:0,.2f}".format(products_db[col].iloc[i]))
                    value.setTextAlignment(QtCore.Qt.AlignCenter)

                    tableWidget.setItem(i,j, value)

                else:
                    if col in ['Наименование', 'Цена [₽]', 'Цена с Банком [₽]']:
                        value = QTableWidgetItem(str(products_db[col].iloc[i]))
                        value.setTextAlignment(QtCore.Qt.AlignCenter)

                        tableWidget.setItem(i,j, value)

                    else:
                        value = QTableWidgetItem(str(expenses_db[col].iloc[i]))
                        value.setTextAlignment(QtCore.Qt.AlignCenter)

                        tableWidget.setItem(i,j, value)


        # --------- styling table ---------
        tableWidget.horizontalHeader().setStretchLastSection(True)
        tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        tableWidget.horizontalHeader().setFixedHeight(35)
        tableWidget.horizontalHeader().setObjectName('mainHorizontalHeader')
        tableWidget.setFixedHeight(470)
        tableWidget.verticalHeader().setObjectName('mainVerticalHeader')
        # --------------------------------

        # adding widgets to the layout
        self.layout.addWidget(tableWidget, 3, 0, 1 ,3)

        # Creating header
        headers = ['Σ Заказа [€]', 'Σ Заказа [₽]', 'Σ Доставки [€]', 'Σ Доставки [₽]', 'Таможня [₽]', 'Налог 5%', 'Налог 20%', 'Налог ?']

        # Creating tabel with expenses
        tableWidget = QTableWidget()
        tableWidget.setObjectName('expensesTable')
        tableWidget.verticalHeader().setVisible(False)
        tableWidget.setColumnCount(len(headers))
        tableWidget.setRowCount(1)
        tableWidget.setHorizontalHeaderLabels(headers)

        # cell 0, 0
        # value  = sum(price *  amount)
        value_price = sum(products_db['Цена [€]'] * products_db['Количество'])
        value_price = round(float(value_price), 4)
        value = QTableWidgetItem(str(value_price))
        value.setTextAlignment(QtCore.Qt.AlignCenter)
        tableWidget.setItem(0,0, value)

        # cell 0, 1
        # value = sum(price *  amount) * euro
        value_price = sum(products_db['Цена [€]'] * products_db['Количество']) * expenses_db['Курс евро [Покупка] [₽]']
        value_price = round(float(value_price), 4)
        value = QTableWidgetItem(str(value_price))
        value.setTextAlignment(QtCore.Qt.AlignCenter)
        tableWidget.setItem(0,1, value)

        # cell 0, 2
        # value = delivery_before + delivery_after
        value_price = sum(expenses_db['Доставка До [€]'] + expenses_db['Доставка После [€]'])
        value_price = round(float(value_price), 4)
        value = QTableWidgetItem(str(value_price))
        value.setTextAlignment(QtCore.Qt.AlignCenter)
        tableWidget.setItem(0,2, value)

        # cell 0, 3
        # value = (delivery_before + delivery_after) * euro
        value_price = sum(expenses_db['Доставка До [€]'] + expenses_db['Доставка После [€]']) * expenses_db['Курс евро [Доставка] [₽]']
        value_price = round(float(value_price), 4)
        value = QTableWidgetItem(str(value_price))
        value.setTextAlignment(QtCore.Qt.AlignCenter)
        tableWidget.setItem(0,3, value)

        # cell 0, 4
        # value = customs_1 + customs_2
        value_price = sum(expenses_db['Таможня УСЛУГИ [₽]'] + expenses_db['Таможня СВХ (БЕЗ НДС) [₽]'])
        value_price = round(float(value_price), 4)
        value = QTableWidgetItem(str(value_price))
        value.setTextAlignment(QtCore.Qt.AlignCenter)
        tableWidget.setItem(0,4, value)

        # cell 0, 5
        # value = tax * 0.05
        value_price = expenses_db['Налог'].values[0] * 0.05
        value_price = round(value_price, 4)
        value = QTableWidgetItem(str(value_price))
        value.setTextAlignment(QtCore.Qt.AlignCenter)
        tableWidget.setItem(0,5, value)

        # cell 0, 6
        # value = (tax + tax * 0.05) * 0.2
        value_price = expenses_db['Налог'].values[0] * 1.05 * 0.2
        value_price = round(value_price, 4)
        value = QTableWidgetItem(str(value_price))
        value.setTextAlignment(QtCore.Qt.AlignCenter)
        tableWidget.setItem(0,6, value)

        # cell 0, 7
        # value = users input
        value_price = expenses_db['Таможенный сбор [₽]'].values[0]
        value_price = round(value_price, 4)
        value = QTableWidgetItem(str(value_price))
        value.setTextAlignment(QtCore.Qt.AlignCenter)
        tableWidget.setItem(0,7, value)

        tableWidget.horizontalHeader().setStretchLastSection(True)
        tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    #    tableWidget.horizontalHeader().setFixedHeight(35)
        tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        tableWidget.horizontalHeader().setObjectName('expensesHorisontalHeader')

        # adding widgets to the layout
        self.layout.addWidget(tableWidget, 5, 0, 1, 3)




        self.button_previous = QPushButton('НАЗАД', objectName='button_previous')
        self.button_back_to_menu = QPushButton('ВЕРНУТСЯ В МЕНЮ', objectName='button_back_to_menu')



        # adding widgets to the layout
        self.layout.addWidget(self.button_previous, 6, 0)
        self.layout.addWidget(self.button_back_to_menu, 6, 2)


    def return_back_and_delete_last_session(self):
        products_db, expenses_db = Load_data_bases()._get_data_bases()
        latest_session = expenses_db['Сессия'].max()

        products_db.drop(products_db[products_db['Сессия'] == latest_session].index, inplace=True)
        expenses_db.drop(expenses_db[expenses_db['Сессия'] == latest_session].index, inplace=True)
        products_db.to_csv('data/'+FILE_NAME_PRODUCTS, index=False)
        expenses_db.to_csv('data/'+FILE_NAME_EXPENSES, index=False)

class Analys_Window(QWidget):
    '''
    class for analys of database
    '''
    def __init__(self):
        super().__init__()
        self.layout = QGridLayout(self)


    def analysis_table(self, tab= 'Цена 1С [₽]'):
        # logo
        self.svglogo = QtSvg.QSvgWidget('data/images/logo.svg')
        self.svglogo.setMaximumSize(QSize(64,70))

        # spacing
        self.space = QLabel(objectName='EditSpace')
        self.space.setFixedHeight(15)

        # Header
        self.EditHeader = QLabel('Анализ', objectName='help_text_left')

        # adding widgets to the layout
        self.layout.addWidget(self.EditHeader, 0, 0, 1, 6, alignment=QtCore.Qt.AlignLeft)
        self.layout.addWidget(self.svglogo, 0, 0, 1, 6, alignment=QtCore.Qt.AlignLeft)
        self.layout.addWidget(self.space, 1, 0, 1, 6, alignment=QtCore.Qt.AlignLeft)

        # Checking if database is existing
        if not exists('data/'+FILE_NAME_PRODUCTS) and not exists('data/'+FILE_NAME_EXPENSES):
            label = QLabel('БАЗЫ ДАННЫХ ПУСТАЯ')
            label.setStyleSheet('font-size:30px;'
                                'color:#837569;'
                                'letter-spacing:4px;')
            label.setAlignment(QtCore.Qt.AlignCenter)
            self.layout.addWidget(label, 1, 0, 1, 6)

        # change tabel layout corresponding to a current tab
        else:
            products_db, expenses_db = Load_data_bases()._get_data_bases()
            if tab == 'Цена Заказа':
                group_table(page=self, products_db=products_db, expenses_db=expenses_db)

            elif tab == 'Расходы':
                createTable().sum_table(page=self, products_db=products_db, expenses_db=expenses_db)

            elif tab == 'Прайс':
                createTable().price_table(page=self, products_db=products_db)

            else:
                createTable().price_comparison_table(page=self, products_db=products_db, expenses_db=expenses_db, price_column_name=tab)

            # adding buttons
            self.switch_to_table_1c = QPushButton('Цена 1С [₽]', objectName='switch_to')
            self.switch_to_table_expenses = QPushButton('Цена [₽]', objectName='switch_to')
            self.switch_to_table_bank = QPushButton('Цена с Банком [₽]', objectName='switch_to')
            self.switch_to_table_product = QPushButton('Цена Заказа', objectName='switch_to')
            self.switch_to_table_order_expenses = QPushButton('Расходы', objectName='switch_to')
            self.switch_to_table_prices = QPushButton('Прайс', objectName='switch_to')
            self.button_back_to_menu = QPushButton('ВЕРНУТСЯ В МЕНЮ', objectName='button_back_to_menu')
            self.button_export = QPushButton('ЭКСПОРТ',clicked=lambda: self.savefile(), objectName='button_back_to_menu')
            min_button_width = 220
            self.switch_to_table_1c.setMinimumWidth(min_button_width)
            self.switch_to_table_expenses.setMinimumWidth(min_button_width)
            self.switch_to_table_bank.setMinimumWidth(min_button_width)
            self.switch_to_table_product.setMinimumWidth(min_button_width)
            self.switch_to_table_order_expenses.setMinimumWidth(min_button_width)
            self.switch_to_table_prices.setMinimumWidth(min_button_width)

            # if current tab is selected the change corresponding button color
            if tab == 'Цена 1С [₽]':
                self.switch_to_table_1c.setObjectName('selected_switch_to')

            if tab == 'Цена [₽]':
                self.switch_to_table_expenses.setObjectName('selected_switch_to')

            if tab == 'Цена с Банком [₽]':
                self.switch_to_table_bank.setObjectName('selected_switch_to')

            if tab == 'Цена Заказа':
                    self.switch_to_table_product.setObjectName('selected_switch_to')

            if tab == 'Расходы':
                self.switch_to_table_order_expenses.setObjectName('selected_switch_to')

            if tab == 'Прайс':
                self.switch_to_table_prices.setObjectName('selected_switch_to')


            # adding widgets to the layout
            self.layout.addWidget(self.switch_to_table_1c, 2, 0)
            self.layout.addWidget(self.switch_to_table_expenses, 2, 1)
            self.layout.addWidget(self.switch_to_table_bank, 2,  2)
            self.layout.addWidget(self.switch_to_table_product, 2, 3)
            self.layout.addWidget(self.switch_to_table_prices, 2, 4)
            self.layout.addWidget(self.switch_to_table_order_expenses, 2, 5)
            self.layout.addWidget(self.button_back_to_menu, 4, 0, 1, 2)
            self.layout.addWidget(self.button_export, 4, 4, 1, 2)

    def savefile(self):
        filename = 'wow.xls'
        wbk = xlwt.Workbook()
        self.sheet = wbk.add_sheet("Прайс", cell_overwrite_ok=True)
        self.add2()
        wbk.save(filename)


    def add2(self):
        db, expenses_db = Load_data_bases()._get_data_bases()
        tableWidget = createTable().price_table(page=self, products_db=db)


        for i in range(tableWidget.columnCount()):
            for x in range(tableWidget.rowCount()):
                if x == 0:
                    column_name = tableWidget.horizontalHeaderItem(i).text()

                    self.sheet.write(x, i, column_name)

                teext = str(tableWidget.item(x, i).text())
                self.sheet.write(x+1, i, teext)





# add checking for db existance

class Edit(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QGridLayout(self)
        self.tableWidget = QTableWidget()
        self.delete_check_boxes = {}
        self.history_tables()

    def history_tables(self, tab='Товары'):
        self.svglogo = QtSvg.QSvgWidget('data/images/logo.svg')
        self.svglogo.setMaximumSize(QSize(64,70))
        self.space = QLabel(objectName='EditSpace')
        self.space.setFixedHeight(15)
        self.EditHeader = QLabel('Редактор', objectName='help_text_left')
        self.layout.addWidget(self.EditHeader, 0,0,1,3,alignment=QtCore.Qt.AlignLeft)
        self.layout.addWidget(self.svglogo, 0,0,1,3, alignment=QtCore.Qt.AlignLeft)
        self.layout.addWidget(self.space, 1,0,1,3, alignment=QtCore.Qt.AlignLeft)
        products_db, expenses_db = Load_data_bases()._get_data_bases()
        if tab == 'Товары':
            self.tableWidget = createTable().history_table(page=self, db=products_db, df_name='H')
            self.button_switch_to_history = QPushButton('ТОВАРЫ', objectName='selected_switch_to')
            self.button_switch_to_expenses = QPushButton('РАСХОДЫ', objectName='switch_to')
            self.button_delete_rows =  QPushButton('УДАЛИТЬ СТРОКИ', objectName='switch_to')
            self.button_save= QPushButton('СОХРАНИТЬ',objectName='button_back_to_menu')
            self.layout.addWidget(self.button_save,4,2)
        if tab == 'Расходы':
            self.tableWidget = createTable().history_table(page=self, db=expenses_db, df_name='E')
            self.button_switch_to_history = QPushButton('ТОВАРЫ', objectName='switch_to')
            self.button_delete_rows =  QPushButton('УДАЛИТЬ СТРОКИ', objectName='switch_to')
            self.button_switch_to_expenses = QPushButton('РАСХОДЫ', objectName='selected_switch_to')
            self.button_save= QPushButton('СОХРАНИТЬ', objectName='button_back_to_menu')
            self.layout.addWidget(self.button_save,4,2)
        if tab == 'Удалить':
            self.delete_checkboxes = createTable().delete_rows_table(page=self)
            self.button_switch_to_history = QPushButton('ТОВАРЫ', objectName='switch_to')
            self.button_switch_to_expenses = QPushButton('РАСХОДЫ', objectName='switch_to')
            self.button_delete_rows =  QPushButton('УДАЛИТЬ СТРОКИ', objectName='selected_switch_to')
            self.button_save= QPushButton('УДАЛИТЬ', objectName='button_back_to_menu')
            self.layout.addWidget(self.button_save,4,2)



        self.button_back_to_menu = QPushButton('ВЕРНУТСЯ В МЕНЮ', objectName='button_back_to_menu')

        self.layout.addWidget(self.button_switch_to_history,3,0)
        self.layout.addWidget(self.button_switch_to_expenses,3,1)
        self.layout.addWidget(self.button_delete_rows,3,2)
        self.layout.addWidget(self.button_back_to_menu,4,0)



    def Delete_rows(self):

        products_db, expenses_db = Load_data_bases()._get_data_bases()
        deleted_rows_sessions = set()

        for i in self.delete_checkboxes:
            i = str(int(list(self.delete_checkboxes.keys())[-1]) - int(i))

            if self.delete_checkboxes[i].isChecked():

                deleted_rows_sessions.add(products_db.loc[int(i)]['Сессия'])
                products_db.drop(products_db.index[[int(i)]], inplace=True)

        for session in deleted_rows_sessions:
            rows = len(products_db[products_db['Сессия'] == session])

            if not rows:

                expenses_db.drop([(expenses_db['Сессия'] == int(session)).tolist().index(True)], inplace=True)

        products_db.to_csv('data/'+FILE_NAME_PRODUCTS, index=False)
        expenses_db.to_csv('data/'+FILE_NAME_EXPENSES, index=False)

    def SaveChanges(self,df='Товары'):

        TWidget = self.tableWidget
        products_db, expenses_db = Load_data_bases()._get_data_bases()
        if df == 'Товары':
            db = products_db
            k = [1]
        if df == 'Расходы':
            db = expenses_db
            k = [1,2]

        changed_rows = []
        for i in range(TWidget.rowCount()):
            for j in range(TWidget.columnCount()):

                if str(db.iloc[i, j]) != TWidget.item(i,j).text():

                    if j not in k:
                        if db.iloc[i, j] != float(TWidget.item(i,j).text()):
                            changed_rows.append(i)
                            db.loc[i, db.columns[j]] = float(TWidget.item(i,j).text())
                    else:
                        db.loc[i, db.columns[j]] = TWidget.item(i,j).text()



        for row in changed_rows:
            session = db.loc[row, 'Сессия']
            products_db_session = products_db[products_db['Сессия'] == session]
            expenses_db_session = expenses_db[expenses_db['Сессия'] == session]
            products_db_session, expenses_db_session = _get_final_prices(products_db_session, expenses_db_session)
            products_db[products_db['Сессия']==session] = products_db_session
            expenses_db[expenses_db['Сессия']==session] = expenses_db_session
            print('ok')



        products_db.to_csv('data/'+FILE_NAME_PRODUCTS, index=False)
        expenses_db.to_csv('data/'+FILE_NAME_EXPENSES, index=False)




class Base(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Business Turtle')
        self.setObjectName('centralwidget')
        # setting start window
        self.current_window = Start_Window()

        self.current_window.button_calc.clicked.connect(
            lambda: self.stackedWidget.setCurrentIndex(1))
        self.current_window.button_analysis.clicked.connect(lambda: self.load_analysis())
        self.current_window.button_edit.clicked.connect(lambda: self.load_edit())
        # ------------------

        # Products window
        self.products_window = Products_Window()

        self.products_window.button_next.clicked.connect(self.Update_Products)

        self.products_window.button_previous.clicked.connect(
            lambda: self.stackedWidget.setCurrentIndex(0))
        # ------------------

        # Input prices window
        self.input_prices_window = Input_Prices_Window()
        # ------------------

        # Final table window
        self.final_table_window = Final_Table_Window()
        # ------------------

        # Analysis window
        self.analysis_window = Analys_Window()
        # ------------------

        # Edit window
        self.Edit = Edit()

        self.Edit.button_back_to_menu.clicked.connect(
            lambda: self.stackedWidget.setCurrentIndex(0))
        # ------------------

        # setting up stacked widget
        self.stackedWidget = QStackedWidget(self)
        self.stackedWidget.addWidget(self.current_window)
        self.stackedWidget.addWidget(self.products_window)
        self.stackedWidget.addWidget(self.input_prices_window)
        self.stackedWidget.addWidget(self.final_table_window)
        self.stackedWidget.addWidget(self.analysis_window)
        self.stackedWidget.addWidget(self.Edit)

        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.stackedWidget)

        # 1 window is Start page
        self.stackedWidget.setCurrentIndex(0)


    # Products window functions
    def Update_Products(self):

        while self.input_prices_window.layout.count() > 0:
            widget = self.input_prices_window.layout.takeAt(0).widget()
            widget.hide()
            widget.deleteLater()

        self.input_prices_window.new_input_prices()
        self.input_prices_window.button_previous.clicked.connect(
            lambda: self.stackedWidget.setCurrentIndex(1))

        self.input_prices_window.button_next.clicked.connect(lambda: self.date_validator())

        self.stackedWidget.setCurrentIndex(2)

    def date_validator(self):
        # cheking date and price inputs [basic]
        val = 1
        pat = re.compile(r'^(0?[1-9]|[12][0-9]|3[01])[\/\-](0?[1-9]|1[012])[\/\-]\d{4}$')
        for i in EXPENSES:
            if EXPENSES[i].text() == '':
                val = 0
                break

        if val:
            if re.fullmatch(pat, EXPENSES['Дата'].text()):
                self.update_db(self.input_prices_window)
            else:
                print(EXPENSES['Дата'].text())
                print('WRONG DATE FORMAT !')
    # ------------------


    def update_db(self, page):
        page.update_products()
        while self.final_table_window.layout.count() > 0:
            widget = self.final_table_window.layout.takeAt(0).widget()
            widget.hide()
            widget.deleteLater()

        self.final_table_window.new_table()

        self.final_table_window.button_previous.clicked.connect(self.return_from_final_table)

        self.final_table_window.button_back_to_menu.clicked.connect(
            lambda: self.stackedWidget.setCurrentIndex(0))


        self.stackedWidget.setCurrentIndex(3)


    def return_from_final_table(self):

        self.final_table_window.return_back_and_delete_last_session()

        self.stackedWidget.setCurrentIndex(2)

    # ------------------

    # Edit page functions
    def load_edit(self,tab='Товары'):
        while self.Edit.layout.count() > 0:
            widget = self.Edit.layout.takeAt(0).widget()
            widget.hide()
            widget.deleteLater()

        self.Edit.history_tables(tab)
        self.Edit.button_switch_to_history.clicked.connect(lambda: self.load_edit('Товары'))
        self.Edit.button_switch_to_expenses.clicked.connect(lambda: self.load_edit('Расходы'))
        self.Edit.button_delete_rows.clicked.connect(lambda: self.load_edit('Удалить'))

        self.Edit.button_back_to_menu.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(0))
        if tab == 'Удалить':
            self.Edit.button_save.clicked.connect(lambda : self.edit_delete_button(tab))
        else:
            self.Edit.button_save.clicked.connect(lambda : self.edit_save_button(tab))

        self.stackedWidget.setCurrentIndex(5)

    def edit_delete_button(self, tab):
        self.Edit.Delete_rows()
        self.load_edit(tab)

    def edit_save_button(self, tab):
        self.Edit.SaveChanges(tab)
        self.load_edit(tab)
    # ------------------

    # Analysis page functions
    def load_analysis(self,tab='Цена 1С [₽]'):

        while self.analysis_window.layout.count() > 0:
            widget = self.analysis_window.layout.takeAt(0).widget()
            widget.hide()
            widget.deleteLater()

        self.analysis_window.analysis_table(tab)

        self.analysis_window.button_back_to_menu.clicked.connect(
            lambda: self.stackedWidget.setCurrentIndex(0))

        self.analysis_window.switch_to_table_1c.clicked.connect(lambda: self.load_analysis('Цена 1С [₽]'))

        self.analysis_window.switch_to_table_expenses.clicked.connect(lambda :self.load_analysis('Цена [₽]'))

        self.analysis_window.switch_to_table_product.clicked.connect(lambda: self.load_analysis('Цена Заказа'))

        self.analysis_window.switch_to_table_order_expenses.clicked.connect(lambda: self.load_analysis('Расходы'))

        self.analysis_window.switch_to_table_prices.clicked.connect(lambda: self.load_analysis('Прайс'))

        self.analysis_window.switch_to_table_bank.clicked.connect(lambda:self.load_analysis('Цена с Банком [₽]'))

        self.stackedWidget.setCurrentIndex(4)
    # ------------------







if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(StyleSheet)

    window = Base()
    window.resize(1000, 800)
    window.show()

    sys.exit(app.exec_())
