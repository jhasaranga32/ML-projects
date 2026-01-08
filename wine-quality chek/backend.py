from flask import Flask,render_template,request,redirect
import joblib
import numpy as np
from flask_mysqldb import MySQL

from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.pagesizes import A4,landscape
from reportlab.lib import colors
from io import BytesIO
from flask import make_response



model = joblib.load(r"C:\Users\mhjha\Desktop\ML projects\wine-quality chek\trained_wine_rf.sav")


app=Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '200106201300'   # your password here
app.config['MYSQL_DB'] = 'wine_db'

mysql = MySQL(app)

@app.route('/')
def index():
   return render_template('wine.html')

@app.route('/getresults', methods=['POST'])
def getresults():
    Barrol_No=request.form['Barrol_No']
    Date=request.form['Date']
    fixed_acidity = request.form['fixed_acidity']
    volatile_acidity = request.form['volatile_acidity']
    citric_acid = request.form['citric_acid']
    residual_sugar = request.form['residual_sugar']
    chlorides = request.form['chlorides']
    free_sulfur_dioxide = request.form['free_sulfur_dioxide']
    total_sulfur_dioxide = request.form['total_sulfur_dioxide']
    density = request.form['density']
    ph = request.form['pH']
    sulphates = request.form['sulphates']
    alcohol = request.form['alcohol']

    test_data = np.array([[float(fixed_acidity), float(volatile_acidity), float(citric_acid),
                           float(residual_sugar), float(chlorides), float(free_sulfur_dioxide),
                           float(total_sulfur_dioxide), float(density), float(ph),
                           float(sulphates), float(alcohol)]])

    prediction = model.predict(test_data)[0]
    result = str(prediction)

    # 🔹 fetch table records to show in same page
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM wine_data")
    records = cur.fetchall()
    cur.close()

    return render_template(
        'result.html',
        Barrol_No=Barrol_No,
        Date=Date,
        fixed_acidity=fixed_acidity,
        volatile_acidity=volatile_acidity,
        citric_acid=citric_acid,
        residual_sugar=residual_sugar,
        chlorides=chlorides,
        free_sulfur_dioxide=free_sulfur_dioxide,
        total_sulfur_dioxide=total_sulfur_dioxide,
        density=density,
        ph=ph,
        sulphates=sulphates,
        alcohol=alcohol,
        result=result,
        records=records       
    )

@app.route('/add', methods=['POST'])
def add_data():
    Barrol_No = request.form['Barrol_No']
    Date = request.form['Date']
    fixed_acidity = request.form['fixed_acidity']
    volatile_acidity = request.form['volatile_acidity']
    citric_acid = request.form['citric_acid']
    residual_sugar = request.form['residual_sugar']
    chlorides = request.form['chlorides']
    free_sulfur_dioxide = request.form['free_sulfur_dioxide']
    total_sulfur_dioxide = request.form['total_sulfur_dioxide']
    density = request.form['density']
    ph = request.form['ph']
    sulphates = request.form['sulphates']
    alcohol = request.form['alcohol']
    result = request.form['result']

    cur = mysql.connection.cursor()
    cur.execute("""
        INSERT INTO wine_data (
            Barrol_No, Date, fixed_acidity, volatile_acidity, citric_acid,
            residual_sugar, chlorides, free_sulfur_dioxide, total_sulfur_dioxide,
            density, ph, sulphates, alcohol, result
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        Barrol_No, Date, fixed_acidity, volatile_acidity, citric_acid,
        residual_sugar, chlorides, free_sulfur_dioxide, total_sulfur_dioxide,
        density, ph, sulphates, alcohol, result
    ))

    mysql.connection.commit()
    cur.close()

    return redirect('/read')



@app.route('/read')
def read():
    # Read all records from the database
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM wine_data")
    data = cur.fetchall()  # fetch all records
    cur.close()
    return render_template('result.html', records=data)


@app.route('/delete/<int:id>')
def delete_data(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM wine_data WHERE id=%s", (id,))
    mysql.connection.commit()
    cur.close()
    return redirect('/read')

@app.route('/download_pdf')
def download_pdf():
    buffer = BytesIO()

    # Create PDF
    pdf = SimpleDocTemplate(buffer, pagesize=landscape(A4))


    # Fetch data from DB
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM wine_data")
    records = cur.fetchall()
    cur.close()

    # Table Header
    data = [[
        "ID","Barrel No","Date","Fixed Acid","Volatile Acid","Citric Acid",
        "Residual Sugar","Chlorides","Free SO2","Total SO2",
        "Density","pH","Sulphates","Alcohol","Result"
    ]]

    # Add DB rows
    for row in records:
        data.append(list(row))

    # Create table
    table = Table(data)

    # Styling
    style = TableStyle([
    ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
    ('GRID', (0,0), (-1,-1), 0.5, colors.black),
    ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
    ('FONTSIZE', (0,0), (-1,-1), 7),
    ('ALIGN', (0,0), (-1,-1), 'CENTER'),
    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
])


    table.setStyle(style)

    elements = [table]
    pdf.build(elements)

    buffer.seek(0)

    response = make_response(buffer.read())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=wine_report.pdf'

    return response


app.run(debug=True)

 