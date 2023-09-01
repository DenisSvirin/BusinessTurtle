import sys
from os.path import exists
import pandas as pd
import numpy as np
from collections import Counter
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.Qt import *
from style import StyleSheet
from PyQt5 import QtCore, QtGui, QtWidgets
import datetime
from load_Database import Load_data_bases
'''
Class for creating tables for edit and analysis windows
'''

class createTable:

    def price_comparison_table(self,page,products_db,expenses_db,price_column_name):

        products_names = products_db['Наименование'].unique().tolist()

        data_prices_db = pd.merge(products_db, expenses_db, on='Сессия', how='left')[['Сессия', 'Дата', 'Наименование', price_column_name]]

        # list to create table later
        products_data_and_prices = []

        for _index in range(len(data_prices_db)):
            name = data_prices_db.iloc[_index]['Наименование']
            year = data_prices_db.iloc[_index]['Дата']
            price_rub = round(data_prices_db.iloc[_index][price_column_name], 2)

            products_data_and_prices.append([year, name, price_rub])

        #products_data_and_prices = sorted(products_data_and_prices, key=lambda x: datetime.datetime(int(x[0].split('/')[2]),int(x[0].split('/')[1]), int(x[0].split('/')[0])))
        # create headers
        headers = set()
        for i in products_data_and_prices:
            headers.add(i[0])
        headers = list(headers)
        # sorting headers
        headers = sorted(headers, key=lambda x: datetime.datetime(int(x.split('/')[2]), int(x.split('/')[1]), int(x.split('/')[0])))

        # dict for base values (to calculate price change)
        products_base_price = {}
        for i in products_names:
            products_base_price[i] = 0

        # Creating table
        tableWidget = QTableWidget()
        tableWidget.setObjectName('analysis_table')
        tableWidget.setColumnCount(len(headers))
        tableWidget.setRowCount(len(products_names))
        tableWidget.setHorizontalHeaderLabels(headers)
        tableWidget.setVerticalHeaderLabels(products_names)

        # filling table data
        for i in products_data_and_prices:
            date  = i[0]
            name  = i[1]
            price = i[2]

            if products_base_price[name] == 0:
                products_base_price[name] = price

            base = products_base_price[name]
            products_base_price[name] = price

            column = headers.index(date)
            row = products_names.index(name)

            value = QTableWidgetItem('{:0,.2f}'.format(float(price)))
            value.setTextAlignment(QtCore.Qt.AlignCenter)
            tableWidget.setItem(row, column, value)
            # coloring text depending on price change
            if base > price:
                color = '#70FF68'
            elif base < price:
                color = '#FF4F4F'
            else:
                color = '#837569'

            tableWidget.item(row, column).setForeground(QtGui.QBrush(QtGui.QColor(color)))


        #  ----- styling table -------

        tableWidget.setStyleSheet('background:#1E152A;'
                                  'border: none;'
                                  'font-weight:400;'
                                  'letter-spacing:4px;'
                                  'gridline-color: #837569;')

        tableWidget.horizontalHeader().setObjectName('analysis_Rub_Horizonta_Header')
        tableWidget.horizontalHeader().setStretchLastSection(False)
        tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        tableWidget.horizontalHeader().setMinimumSectionSize(180)

        tableWidget.verticalHeader().setObjectName('analysis_Rub_Vertical_Header')
        tableWidget.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        tableWidget.verticalHeader().setMinimumSectionSize(50)

        tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # ----------------------------
        page.layout.addWidget(tableWidget,1,0,1,6)


    def sum_table(self, page, products_db, expenses_db):
        # column list to take from general table
        analysis_columns = ['Сессия', 'Дата', 'Цена [€]', 'Количество', 'Курс евро [Покупка] [₽]', 'Доставка До [€]', 'Доставка После [€]']
        df_analysis_data = pd.merge(products_db, expenses_db, on='Сессия', how='left')[analysis_columns]

        # Creating DataFrame [ to parce it, and fillthe table in the future]
        df_data = pd.DataFrame()

        arr = []
        for i in range(df_analysis_data['Сессия'].max() + 1):
            df = df_analysis_data[df_analysis_data['Сессия'] == i ]
            arr.append((df['Цена [€]'] * df['Количество']).sum())
        df_data['Σ Заказа [€]'] = np.round(arr, 2)
        df_data['Σ Заказа [₽]'] = np.round(expenses_db['Σ Заказа [₽]'], 2)

        arr = []
        for i in range(df_analysis_data['Сессия'].max() + 1):
            df = df_analysis_data[df_analysis_data['Сессия'] == i ]
            arr.append((df['Доставка До [€]'] + df['Доставка После [€]']).values[0])
        df_data['Σ Доставки [€]'] = np.round(arr, 2)
        df_data['Σ Доставки [₽]'] = np.round(expenses_db['Σ Доставки [₽]'], 2)

        df_data['Банк [₽]'] = expenses_db['Банк [₽]']

        df_data['Таможня [₽]'] = np.round(expenses_db['Таможня УСЛУГИ [₽]'] + expenses_db['Таможня СВХ (БЕЗ НДС) [₽]'], 2)

        df_data['Дата'] = expenses_db['Дата']

        # Creating header
        headers = df_data['Дата'].values
        headers = sorted(headers, key=lambda x: datetime.datetime(int(x.split('/')[2]),int(x.split('/')[1]), int(x.split('/')[0])))

        # Creating table
        tableWidget = QTableWidget()
        tableWidget.setObjectName('analysis_table')
        tableWidget.setColumnCount(len(headers))
        tableWidget.setRowCount(len(df_data.columns) - 1 )
        tableWidget.setHorizontalHeaderLabels(headers)
        tableWidget.setVerticalHeaderLabels(df_data.columns[:-1])

        # filling table data
        for i in range(len(df_data)):
            current_row = df_data.iloc[i]
            for j in range(len(df_data.columns)-1):

                date = current_row['Дата']
                column = headers.index(date)
                row = j

                value = QTableWidgetItem(str(df_data.iloc[column, row]))
                value.setTextAlignment(QtCore.Qt.AlignCenter)
                tableWidget.setItem(row,column, value)
                tableWidget.item(row, column).setForeground(QtGui.QBrush(QtGui.QColor('#837569')))

        #  ----- styling table -------
        tableWidget.setStyleSheet('background:#1E152A;'
                                  'border: none;'
                                  'font-weight:400;'
                                  'letter-spacing:4px;'
                                  'gridline-color: #837569;')


        tableWidget.horizontalHeader().setObjectName('analysis_Rub_Horizonta_Header')
        tableWidget.horizontalHeader().setStretchLastSection(True)
        tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        tableWidget.horizontalHeader().setMinimumSectionSize(180)


        tableWidget.verticalHeader().setObjectName('analysis_Rub_Vertical_Header')
        tableWidget.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        tableWidget.verticalHeader().setMinimumSectionSize(50)

        tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        # ----------------------------

        page.layout.addWidget(tableWidget, 1, 0, 1, 6)

    def price_table(self, page, products_db):
        # dict to keep latest possible price
        latest_price = {}
        df_data_1 = products_db[['Наименование', 'Цена с Банком [₽]']]
        for i in range(len(df_data_1)):
            latest_price[df_data_1.iloc[i, 0]] =  df_data_1.iloc[i, 1]

        # Creating DataFrame with latest prices [ to parce it, and fillthe table in the future]
        df_data = pd.DataFrame(columns=['Наименование', 'Цена с Банком [₽]'])
        for i,k  in enumerate(latest_price.keys()):
            df_data.loc[i] = [k, latest_price[k]]

        # new columns 200% -> price + 100%, 220% ->  column '200%' + 20%
        df_data['200%'] = df_data['Цена с Банком [₽]'] *  ([2] * len(df_data))
        df_data['220%'] = df_data['200%'] * ([1.2] * len(df_data))

        # Creating header
        headers = ['Наименование', 'Стоймость [₽]', '+ 100%', '+ 20%']

        # Creating table
        tableWidget = QTableWidget()
        tableWidget.setObjectName('analysis_table')
        tableWidget.setColumnCount(len(headers))
        tableWidget.setRowCount(len(df_data))
        tableWidget.setHorizontalHeaderLabels(headers)
        tableWidget.verticalHeader().setVisible(False)

        # filling tabel with data
        for i in range(len(df_data)):
            for j in range(len(headers)):
                # formatting price if its not 0 column as its a name
                if j != 0:
                    price = np.round(df_data.iloc[i, j], 2)
                    value = QTableWidgetItem('{:0,.2f}'.format(price))
                else:
                    value = QTableWidgetItem(str(df_data.iloc[i, j]))
                value.setTextAlignment(QtCore.Qt.AlignCenter)
                tableWidget.setItem(i,j, value)
                tableWidget.item(i, j).setForeground(QtGui.QBrush(QtGui.QColor('#837569')))

        #  ----- styling table -------
        tableWidget.setStyleSheet('background:#1E152A;'
                                  'border: none;'
                                  'font-weight:400;'
                                  'letter-spacing:4px;'
                                  'gridline-color: #837569;')


        tableWidget.horizontalHeader().setObjectName('analysis_Rub_Horizonta_Header')
        tableWidget.horizontalHeader().setStretchLastSection(True)
        tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        tableWidget.horizontalHeader().setMinimumSectionSize(290)


        tableWidget.verticalHeader().setObjectName('analysis_Rub_Vertical_Header')
        tableWidget.verticalHeader().setMinimumSectionSize(50)

        tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        # ----------------------------

        page.layout.addWidget(tableWidget, 1, 0, 1, 6)

        return tableWidget

    def history_table(self, page, db, df_name='E'):
        '''
        Table for editing prices
        '''
        # Creating header
        headers = db.columns.tolist()

        # Creating table
        tableWidget = QTableWidget()
        tableWidget.setObjectName('EditProductsTable')
        tableWidget.verticalHeader().setVisible(False)
        tableWidget.setColumnCount(len(headers))
        tableWidget.setRowCount(len(db))
        tableWidget.setHorizontalHeaderLabels(headers)

        for i in range(len(db)):
            for j in range(len(headers)):
                # formatting prices except 'Сессия' and 'Наименование'

                price = db.iloc[i, j]
                value = QTableWidgetItem(str(price))
                value.setTextAlignment(QtCore.Qt.AlignCenter)
                tableWidget.setItem(i,j, value)



        tableWidget.horizontalHeader().setStretchLastSection(False)
        tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        tableWidget.horizontalHeader().setMinimumSectionSize(290)
        tableWidget.verticalHeader().setMinimumSectionSize(50)
        tableWidget.horizontalHeader().setObjectName('EditProductsHorisontalHeader')
        # ----------------------------
        page.layout.addWidget(tableWidget, 2, 0, 1 ,3)

        # Returning created table to parce it later [ when saving ]
        return tableWidget


    def delete_rows_table(self, page):
        '''
        Table for deleting selected rows
        '''
        # loading database
        db, expenses_db = Load_data_bases()._get_data_bases()

        # Creating headers
        headers = db.columns.tolist()
         # adding null column for checkbox column and removing last 3 columns for better ui
        headers = [''] + headers[:len(headers)-3]

        # Creating table
        tableWidget = QTableWidget()
        tableWidget.setObjectName('EditProductsTable')
        tableWidget.verticalHeader().setVisible(False)
        tableWidget.setColumnCount(len(headers))
        tableWidget.setRowCount(len(db))
        tableWidget.setHorizontalHeaderLabels(headers)

        # Dict to save selected rows [keys -> indeces in the products_]
        delete_checkboxes = {}

        # Creating checkbox column [column 0]
        for i in range(len(db)):
            el = QCheckBox()
            delete_checkboxes[str(i)] = el
            # attempt to remove focus on checkbox [green sqaure]
            el.setStyleSheet('*{border:none;padding-top:25px;}*:focus{outline:none;}')
            tableWidget.setCellWidget(i, 0, el)

        # filling table with data
        for i in range(len(db)):
            for j in range(1, len(headers)):
                value = QTableWidgetItem(str(db.iloc[i, j-1]))
                value.setTextAlignment(QtCore.Qt.AlignCenter)
                tableWidget.setItem(i, j, value)



        #  ----- styling table -------
        tableWidget.horizontalHeader().setStretchLastSection(False)
        tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        #tableWidget.horizontalHeader().setSectionResizeMode(290)
        tableWidget.horizontalHeader().setSectionResizeMode(0, 25)
        tableWidget.horizontalHeader().setObjectName('EditProductsHorisontalHeader')
        tableWidget.verticalHeader().setMinimumSectionSize(50)

        tableWidget.setFocusPolicy(Qt.NoFocus)
        tableWidget.setSelectionMode(QAbstractItemView.NoSelection)
        tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        # ----------------------------
        page.layout.addWidget(tableWidget, 2, 0, 1 ,3)

        # returning checkbox dict to run throught it, delete selected rows and save dbs
        return delete_checkboxes


class group_table:
    ''' class to create Treeview
        i.e. expandable tables
    '''

    def __init__(self, products_db, expenses_db, page):
        self.page = page
        # Creating group names
        group_names = products_db['Наименование'].unique()

        # Creatin header
        headers = set()
        for i in expenses_db['Дата']:
            headers.add(i)
        headers = list(headers)
        headers = sorted(headers, key=lambda x: datetime.datetime(int(x.split('/')[2]),int(x.split('/')[1]), int(x.split('/')[0])))
        headers.insert(0, '')
        headers.insert(1, 'Наименование')

        # Creatin tree model [8 as each group will have 8 children ]
        model = GroupModel(page, row_count=len(group_names) * 8, headers=headers)
        tree_view = GroupView(model, len_headers=len(headers))

        # preparing data for parcing

        analysis_columns = ['Сессия','Дата','Наименование', 'Количество','Цена с Банком [₽]','Цена [€]','Курс евро [Покупка] [₽]','Курс евро [Налоги] [₽]','Σ Доставки [₽]','Банк [₽]','Таможня УСЛУГИ [₽]','Таможня СВХ (БЕЗ НДС) [₽]','Таможенный сбор [₽]', 'Цена [₽]']
        df_analysis_data = pd.merge(products_db, expenses_db, on='Сессия', how='left')[analysis_columns]
        # list of total percetanges per session [for future calculations]
        percent = []
        for i in range(df_analysis_data['Сессия'].max() + 1):
            df = df_analysis_data[df_analysis_data['Сессия'] == i]
            percent += (df['Количество'] / df['Количество'].sum()).tolist()

        df_analysis_data['percent'] = percent
        df_analysis_data['Доставка [₽]'] = np.round(df_analysis_data['Σ Доставки [₽]'] * df_analysis_data['percent'],4)
        df_analysis_data['Таможня [₽]'] = np.round((df_analysis_data['Таможня УСЛУГИ [₽]'] + df_analysis_data['Таможня СВХ (БЕЗ НДС) [₽]']) * df_analysis_data['percent'],4)
        df_analysis_data['Таможенный сбор [₽]'] = np.round(df_analysis_data['Таможенный сбор [₽]'] * df_analysis_data['percent'],4)
        df_analysis_data['Банк [₽]'] = np.round(df_analysis_data['Банк [₽]'] * df_analysis_data['percent'],4)
        info_columns = ['Количество', 'Цена [€]', 'Доставка [₽]', 'Таможня [₽]', 'Таможенный сбор [₽]','Банк [₽]']
        # TO DO: sort date [just in case]

        #df_analysis_data['Дата'] = pd.to_datetime(df_analysis_data['Дата'])
        #df_analysis_data = df_analysis_data.sort_values(by='Дата')

        # creating data -> groups with children -> [group name -> child1[data, data ...], child2[data, data ...]]
        analysis_data = {}
        for item in group_names:
            analysis_data[item] = []
            for info_name in info_columns:
                analysis_data[item].append([info_name] + [''] * (len(headers) - 2))

        for row in range(len(df_analysis_data)):
            current_row = df_analysis_data.iloc[row]

            for info_name in info_columns:
                for i in analysis_data[current_row['Наименование']]:

                    if i[0] == info_name:
                        index = headers.index(current_row['Дата'])

                        i[index-1] = current_row[info_name]
        order_price = []

        for i in range(df_analysis_data['Сессия'].max() + 1):
            df = df_analysis_data[df_analysis_data['Сессия'] == i]
            order_sum = (df['Цена [€]'] * df['Количество']).sum()

            order_price.append([expenses_db[expenses_db['Сессия'] == i]['Дата'].values[0], order_sum])

        # adding data to the tree model
        for group, childrens in analysis_data.items():


            final_group_price  = (df_analysis_data['Дата'] +' ' + (df_analysis_data[df_analysis_data['Наименование'] == group]['Цена с Банком [₽]']).apply(lambda x: str(x))).dropna().apply(lambda x: x.split())
            group_item = model.add_group(group, (expenses_db['Дата'] + ' ' + expenses_db['Курс евро [Налоги] [₽]'].apply(lambda x: str(x))).apply(lambda x: x.split()),headers, final_group_price,order_price)
            for children in childrens:
                model.append_element_to_group(group_item, children)

        page.layout.addWidget(tree_view, 1, 0, 1, 6)




class GroupDelegate(QtWidgets.QStyledItemDelegate):
    def __init__(self, parent=None):
        super(GroupDelegate, self).__init__(parent)

        self._plus_icon = QtGui.QIcon('data/images/plus1.png')
        self._minus_icon = QtGui.QIcon('data/images/minus1.png')


    def initStyleOption(self, option, index):
        super(GroupDelegate, self).initStyleOption(option, index)
        if not index.parent().isValid():
            is_open = bool(option.state & QtWidgets.QStyle.State_Open)
            option.features |= QtWidgets.QStyleOptionViewItem.HasDecoration
            option.icon = self._minus_icon if is_open else self._plus_icon
            option.label = QtGui.QStandardItem('test')

class GroupView(QtWidgets.QTreeView):
    def __init__(self, model,len_headers, parent=None):
        super(GroupView, self).__init__(parent)
        self.setIndentation(0)
        self.setExpandsOnDoubleClick(False)
        self.clicked.connect(self.on_clicked)
        delegate = GroupDelegate(self)
        self.setItemDelegateForColumn(0, delegate)
        self.setModel(model)
        #self.header().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        self.header().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

        self.header().setSectionResizeMode(QHeaderView.ResizeToContents)

        self.header().setSectionResizeMode(0, 25)

        self.header().setStretchLastSection(True)


        #self.setFocusPolicy(QtCore.Qt.NoFocus)

        font = QtGui.QFont()
        font.setPointSize(20)
        self.header().setFont(font)
        self.header().setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)

        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)

        self.setStyleSheet(TreeStyleSheet)

    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def on_clicked(self, index):
        if not index.parent().isValid() and index.column() == 0:
            self.setExpanded(index, not self.isExpanded(index))

class GroupModel(QtGui.QStandardItemModel):

    def __init__(self, parent=None, row_count=0 ,headers=[]):
        super(GroupModel, self).__init__(parent)
        self.setColumnCount(len(headers))

        self.setHorizontalHeaderLabels(headers)
        for i in range(self.columnCount()):
            it = self.horizontalHeaderItem(i)
            it.setTextAlignment(QtCore.Qt.AlignCenter)
            it.setForeground(QtGui.QColor("#837569"))
            it.setBackground(QtGui.QColor('#1E152A'))
            font = QtGui.QFont()
            font.setPointSize(24)
            font.setWeight(500)
            it.setFont(font)



    def add_group(self, group_name, euro, headers, final_group_price, order_price):
        item_root = QtGui.QStandardItem()
        item_root.setEditable(False)
        item = QtGui.QStandardItem(group_name)
        item.setEditable(False)
        ii = self.invisibleRootItem()
        # filling euro price row [row 0]
        value = QtGui.QStandardItem('Курс евро [Налог]')
        ii.setChild(0,1,value)
        ii.child(0, 1).setForeground(QtGui.QColor('#837569'))
        font = QtGui.QFont()
        font.setPointSize(20)
        font.setWeight(500)
        ii.child(0, 1).setFont(font)
        ii.setEditable(False)
        ii.child(0, 1).setTextAlignment(QtCore.Qt.AlignCenter)
        # Adding euro to first line
        base_euro = 0
        for i in range(len(euro)):
            if base_euro == 0:
                 base_euro = euro[i][1]
            index = headers.index(euro[i][0])
            value = QtGui.QStandardItem(str(np.round(float(euro[i][1]),2)))
            ii.setChild(0,index,value)
            if euro[i][1] > base_euro:
                ii.child(0, index).setForeground(QtGui.QColor('#FF4F4F'))
            elif euro[i][1] < base_euro:
                ii.child(0, index).setForeground(QtGui.QColor('#70FF68'))
            else:
                ii.child(0, index).setForeground(QtGui.QColor('#837569'))

            base_euro = euro[i][1]

            ii.setEditable(False)
            font = QtGui.QFont()
            font.setPointSize(20)
            font.setWeight(700)
            ii.child(0, index).setEditable(False)
            ii.child(0, index).setFont(font)
            ii.child(0, index).setTextAlignment(QtCore.Qt.AlignCenter)
        # --------------------------

        # filling column total price row [row 1]
        value = QtGui.QStandardItem('Σ Заказа [€]')
        ii.setChild(1,1,value)
        ii.child(1, 1).setForeground(QtGui.QColor('#837569'))
        font = QtGui.QFont()
        font.setPointSize(20)
        font.setWeight(500)
        ii.child(1, 1).setFont(font)
        ii.setEditable(False)
        ii.child(1, 1).setTextAlignment(QtCore.Qt.AlignCenter)

        for i in range(len(order_price)):

            index = headers.index(order_price[i][0])
            value = QtGui.QStandardItem(str(np.round(float(order_price[i][1]),2)))
            ii.setChild(1,index,value)

            ii.child(1, index).setForeground(QtGui.QColor('#837569'))
            font = QtGui.QFont()
            font.setPointSize(20)
            font.setWeight(500)
            ii.child(1, index).setFont(font)
            ii.child(1, index).setEditable(False)
            ii.child(1, index).setTextAlignment(QtCore.Qt.AlignCenter)


            ii.setEditable(False)
            font = QtGui.QFont()
            font.setPointSize(20)
            font.setWeight(700)
            ii.child(0, index).setFont(font)
            ii.child(0, index).setTextAlignment(QtCore.Qt.AlignCenter)
        # --------------------------

        i = ii.rowCount()
        base_price = 0
        for j in final_group_price:
            if base_price == 0 :
                base_price = j[1]
            index = headers.index(j[0])
            value = QtGui.QStandardItem(str(np.round(float(j[1]),2)))
            ii.setChild(i,index,value)
            ii.setEditable(False)
            font = QtGui.QFont()
            font.setPointSize(17)
            font.setWeight(600)
            ii.child(i, index).setFont(font)
            ii.child(i, index).setTextAlignment(QtCore.Qt.AlignCenter)
            if base_price > j[1]:
                ii.child(i, index).setForeground(QtGui.QColor('#70FF68'))
            elif base_price < j[1]:
                ii.child(i, index).setForeground(QtGui.QColor('#FF4F4F'))
            base_price = j[1]

        for j, it in enumerate((item_root, item)):
            ii.setChild(i, j, it)
            ii.setEditable(False)
        for j in range(self.columnCount()):
            it = ii.child(i, j)
            if it is None:
                it = QtGui.QStandardItem()
                ii.setChild(i, j, it)
            #ii.child(i, j).setForeground(QtGui.QColor('#837569'))
            font = QtGui.QFont()
            font.setPointSize(18)
            font.setWeight(500)
            #ii.child(i, j).setFont(font)
            #ii.child(i, j).setTextAlignment(QtCore.Qt.AlignCenter)
            it.setEditable(False)

        return item_root

    def append_element_to_group(self, group_item, texts):
        base_info_value = 0
        j = group_item.rowCount()

        for i, text in enumerate(texts):

            if i == 0 or len(str(text)) == 0:
                item = QtGui.QStandardItem(str(text))
            else:
                text = np.round(float(text), 2)
                item = QtGui.QStandardItem('{:0,.2f}'.format(float(text)))
            item.setEditable(False)
            item.setForeground(QtGui.QColor('#837569'))
            if len(str(text)) != 0 and i != 0:


                if i == 1 :
                    base_info_value = float(text)

                elif i > 1:
                    if float(text) > base_info_value and base_info_value !=0:
                        item.setForeground(QtGui.QColor('#FF4F4F'))
                    elif float(text) < base_info_value and base_info_value !=0:
                        item.setForeground(QtGui.QColor('#70FF68'))
                    else:
                        item.setForeground(QtGui.QColor('#837569'))
                    base_info_value = float(text)
                item.setTextAlignment(QtCore.Qt.AlignRight)



            font = QtGui.QFont()
            font.setPointSize(11)
            font.setWeight(700)
            item.setFont(font)


            group_item.setChild(j, i+1, item)

TreeStyleSheet = '''
QTreeView::item{
    border: 0.5px dashed #837569;
}

QTreeView{
    background:#1E152A;
    font-size:17px;
    border: none;
    color:#837569;
    letter-spacing:4px;
}
'''
