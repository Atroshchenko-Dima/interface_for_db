import flask
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, Response, make_response
import psycopg2
import sys
from datetime import datetime
import openpyxl
import os
import json
from parameters import params
from connection import execute_query
from connection import get_connection

app = Flask(__name__)

# Декоратор @app.route('/') устанавливает маршрут для главной страницы нашего приложения, а метод def index()определяет, что будет отображаться на этой странице.
@app.route("/", methods=["GET","POST"])
def index():  
    if request.method == "POST":
        # Получение переменных выбранных пользователем и обработка массива select multiple
        selected_years = [int(i) for i in request.form.getlist("year") if i.isdigit()]
        selected_stations = [str(i) for i in request.form.getlist("station")]
        selected_indicators = [str(i) for i in request.form.getlist("indicator")]
        # зафиксировал 4 столбца(по умолчанию должны быть выбранными)
        columns_list = ['year','station_name','indicators','unit_measurement']
        columns = columns_list + [str(i) for i in request.form.getlist("columns")]
        all_query_metrics =  ("SELECT * from fact_est_bp;")
        rows_metrics = execute_query(all_query_metrics)
        # забираю из БД наименования показателей и станций(затем передаю в html для запоминания выбора пользователя при срабатывании POST)
        stations_t2, indicators_t2 = [], []
        for row in rows_metrics:
            if row[1] not in stations_t2:
                stations_t2.append(row[1])
            elif row[3] not in indicators_t2:
                indicators_t2.append(row[3])
        # запрос и передача данных в строки
        query = ("SELECT {} FROM fact_est_bp WHERE year = ANY(%s) AND indicators = ANY(%s) AND station_name = ANY(%s);"
                    .format(",".join(["\"{}\"".format(c) for c in columns])))
        rows = execute_query(query, (selected_years, selected_indicators, selected_stations))
        filename = "fact_T2.xlsx"
        filepath = os.path.join(os.path.dirname(__file__), filename)
        # создание новой книги excel
        workbook = openpyxl.Workbook()
        worksheet = workbook.active
        # заполнение таблицы данными из запроса к БД и сохранение файла
        worksheet.append(columns)
        for row in rows:
            worksheet.append(list(row))
        workbook.save(filepath)
        return render_template("index.html", rows=rows, rows_metrics=rows_metrics, columns=columns, selected_years=selected_years, now=datetime.utcnow(), selected_stations=selected_stations,
                               stations_t2=stations_t2, selected_indicators=selected_indicators, indicators_t2=indicators_t2, columns_list=columns_list, form_visible=True)
    else:
        return render_template("index.html", now=datetime.utcnow(), form_visible=False)

@app.route("/ves.html", methods=["GET","POST"])
def ves():  
    if request.method == "POST":
        # Получение переменных выбранных пользователем и обработка массива select multiple
        selected_years = [int(i) for i in request.form.getlist("year") if i.isdigit()]
        selected_stations = [str(i) for i in request.form.getlist("station")]
        selected_indicators = [str(i) for i in request.form.getlist("indicator")]
        # зафиксировал 6 столбцов(по умолчанию являются выбранными)
        columns_list = ['ves_year','ves_park_number','ves_station_name','ves_indicators','ves_unit_measurement','ves_installed_power']
        columns = columns_list + [str(i) for i in request.form.getlist("columns")]
        all_query_metrics =  ("SELECT * from ves;")
        rows_metrics = execute_query(all_query_metrics)
        # забираю из БД наименования показателей и станций(затем передаю в html для запоминания выбора пользователя при срабатывании POST)
        stations_ves, indicators_ves = [], []
        for row in rows_metrics:
            if row[2] not in stations_ves:
                stations_ves.append(row[2])
            elif row[3] not in indicators_ves:
                indicators_ves.append(row[3])
        # запрос и передача данных в строки
        query = ("SELECT {} FROM ves WHERE ves_year = ANY(%s) AND ves_indicators = ANY(%s) AND ves_station_name = ANY(%s);"
                    .format(",".join(["\"{}\"".format(c) for c in columns])))
        rows = execute_query(query, (selected_years, selected_indicators, selected_stations))
        filename = "ves.xlsx"
        filepath = os.path.join(os.path.dirname(__file__), filename)
        # создание новой книги excel
        workbook = openpyxl.Workbook()
        worksheet = workbook.active
        # заполнение таблицы данными из запроса к БД и сохранение файла
        worksheet.append(columns)
        for row in rows:
            worksheet.append(list(row))
        workbook.save(filepath)
        return render_template("ves.html", rows=rows, rows_metrics=rows_metrics, columns=columns, selected_years=selected_years, now=datetime.utcnow(), selected_stations=selected_stations,
                               stations_ves=stations_ves, selected_indicators=selected_indicators, indicators_ves=indicators_ves, columns_list=columns_list, form_visible=True)
    else:
        return render_template("ves.html", now=datetime.utcnow(), form_visible=False)

# Возвращение файла на скачивание(при работе с БД формы Т2)
@app.route("/download", methods=["GET","POST"])
def download():
    if request.method == "GET":
        filename = "fact_T2.xlsx"
        return send_from_directory(os.path.dirname(__file__),  path=filename, as_attachment=True)
    else:
        return redirect(url_for("index"))

# Возвращаем файл на скачивание(при работе с БД ВЭС)
@app.route("/download_ves", methods=["GET","POST"])
def download_ves():
    if request.method == "GET":
        filename = "ves.xlsx"
        return send_from_directory(os.path.dirname(__file__),  path=filename, as_attachment=True)
    else:
        return redirect(url_for("ves"))

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
