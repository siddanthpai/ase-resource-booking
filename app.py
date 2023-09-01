from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import datetime
from datetime import date
from sqlalchemy import PrimaryKeyConstraint
from flask_migrate import Migrate
from datetime import datetime
from flask import jsonify
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///slots.db'
db = SQLAlchemy(app)
migrate = Migrate(app, db)
class Slot(db.Model):
    resource_id = db.Column(db.Integer, primary_key=True)
    time_slot = db.Column(db.String(5), primary_key=True) 
    booked_by = db.Column(db.String(50))
    booking_date = db.Column(db.Date,primary_key=True)
    __table_args__ = (
        PrimaryKeyConstraint('resource_id', 'time_slot','booking_date'),
    )

resources = ['ASE1', 'ASE2', 'ASE3', 'ASE4', 'ASE5', 'ASE6', 'ASE7']

@app.route('/', methods=['GET', 'POST'])
def index():
    booking_date = date.today()
    if request.method == 'POST':
        resource_id = int(request.form['resource'])
        time_slots = request.form.getlist('time_slots')
        booked_by = request.form['booked_by']
        #booking_date = request.form['booking_date']
        #booking_date = datetime.strptime(request.form['booking_date'], '%Y-%m-%d').date()
        booking_date_str = request.form.get('booking_date')
        if booking_date_str:
            booking_date = datetime.strptime(booking_date_str, '%Y-%m-%d').date()

        for time_slot in time_slots:
            existing_slot = Slot.query.filter_by(resource_id=resource_id, time_slot=time_slot, booking_date=booking_date).first()
            if existing_slot:
               existing_slot = db.session.query(Slot).get((resource_id, time_slot,booking_date))
               existing_slot.booked_by = booked_by
               db.session.add(existing_slot)
            else:
               new_slot = Slot(resource_id=resource_id, time_slot=time_slot, booked_by=booked_by,booking_date=booking_date)
               db.session.add(new_slot)

            db.session.commit()      

        
    #db.session.query(Slot).delete()
    db.session.commit()
    
    booked_slots = Slot.query.filter_by(booking_date=booking_date).all()
    
    return render_template('index.html', resources=resources, booked_slots=booked_slots,booking_date=booking_date)

def is_booked(hour, resource_id,booked_slots):
    for slot in booked_slots:
        if slot.time_slot == "{:02d}:00".format(hour) and slot.resource_id == resource_id:
            return True
    return False



@app.context_processor
def utility_processor():
    return dict(is_booked=is_booked)



@app.route('/update-table', methods=['GET'])
def update_table():
    selected_date = request.args.get('date')
    
    # Fetch data from the database based on the selected date
    # Assuming your Slot model has a field named 'booking_date'
    booked_slots = Slot.query.filter_by(booking_date=selected_date).all()

    data = []
    for hour in range(8, 20, 2):
        row = {
            'timeSlot': "{:02d}:00 - {:02d}:00".format(hour, hour + 2),
            'resources': []
        }
        for resource_id in range(len(resources)):
            booked_by = ""
            for slot in booked_slots:
                if slot.time_slot == "{:02d}:00".format(hour) and slot.resource_id == resource_id:
                    booked_by = slot.booked_by
                    break
            row['resources'].append(booked_by)
        print(selected_date)
        data.append(row)
    print(data)
    return jsonify(data)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

