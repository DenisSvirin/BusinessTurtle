StyleSheet = '''
#centralwidget {
    background-color: #1E152A;
}
#heading {
    font-size: 45px;
    color: "#8FE381";
    letter-spacing:10px;
    font-weight:700;
    margin-bottom:100px;
}
#help_text, #help_text_left{
    font-size: 40px;
    color: "#837569";
    letter-spacing:3px;
    font-weight:700;
}

#help_text_left{
    font-size: 100px;
    letter-spacing:8px;
    margin-left:70px;

}
#EditLogo{
    margin-bottom:50px;
}
#button_calc,#button_analysis,#button_edit, #button_next, #button_previous, #button_back_to_menu{
    font-size: 30px;
    color: "#837569";
    letter-spacing: 4px;
    border: 4px solid #FFA9E7;
    border-radius: 20px;
    margin-bottom: 50px;
}
#switch_to, #selected_switch_to{
    font-size: 15px;
    color: #837569;
    letter-spacing: 1px;
    border: 3px solid #8FE381;
    border-radius: 10px;
    margin: 30px;
}
#switch_to:hover{
background: #8FE381;
color: #1E152A;
}
#selected_switch_to{
background:#8FE381;
color:#1E152A;
border: 4px solid #FFA9E7;
}
#button_next, #button_previous,#button_back_to_menu {
    font-size: 20px;
    border-radius: 15px;
    margin-bottom: 50px;
}
#button_calc:hover, #button_analysis:hover, #button_edit:hover, #button_next:hover, #button_previous:hover
 ,#button_back_to_menu:hover{
    background: #FFA9E7;
    color: #1E152A;
}

QCheckBox {
    border: 1px solid #837569;
    border-radius : 5px;
    letter-spacing: 2px;
    font-size: 15px;
    font-weight: 600;
    color: #837569;
    margin-left: 50%;
    letter-spacing: 2;
    margin-right: 50%;
    padding-top: 5px;
    padding-bottom: 5px;
    margin-bottom: 20px;
}
#scrollArea, #scrollAreaWidgetContents {
    border: none;
    margin-left:75px;
    margin-right:75px;
    background-color: #1E152A;

}
#scrollArea_Header{
border: none;
letter-spacing: 2px;
font-size: 25px;
font-weight: bold;
color: #8FE381;
margin-bottom:30px;
margin-top:30px;
}
#scrollArea_el{
border: 1px solid #837569;
border-radius: 5px;
letter-spacing: 2px;
font-size: 15px;
font-weight: 600;
color: #837569;
}
QLineEdit {
    border: 1px solid #837569;
    border-radius : 5px;
    letter-spacing: 2px;
    font-size: 15px;
    font-weight: 600;
    color: #837569;
    background-color: #1E152A;
}
QLineEdit:focus {
    outline: none !important;
    border: 2px solid #837569;
    border-radius: 5px;
    background-color: #0E051A;
    color: #938579;
}

#mainTableWidget, #expensesTable, #EditProductsTable{


    background:#1E152A;
    color:#837569;
    border: none;
    font-size:17px;
    font-weight:600;
    letter-spacing:4px;
    gridline-color: #837569;


}
 #expensesTable{
    font-size:13px;
    letter-spacing:4px;
    color:#8FE381;

 }

#mainHorizontalHeader, #expensesHorisontalHeader, #EditProductsHorisontalHeader{

    background:#1E152A;
    font-size:27px;
    font-weight:700;
    color:#837569;
    gridline-color: #8FE381;
}
#EditProductsHorisontalHeader{
    font-size:20px;
}
#expensesHorisontalHeader{
    font-size:17px;
    }
#mainVerticalHeader{
    background:#1E152A;
    border: none;
    color:#837569;
    gridline-color: #8FE381;
}
QTableCornerButton::Section{
    background:#1E152A;
}
#control_points{
    color: #8FE381;
    border: 1px solid #8FE381;
}
#analysis_table{
    margin-top:40px;
}
#analysis_Rub_Vertical_Header, #analysis_Rub_Horizonta_Header{
    background:#1E152A;
    border: none;
    font-size:20px;
    font-weight:bold;
    color:#837569;
    gridline-color: #8FE381;
}

QTableWidget::QCheckBox{
border:none;
}
'''
