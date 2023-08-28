from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import datetime
from datetime import date
from sqlalchemy import PrimaryKeyConstraint
from flask_migrate import Migrate
from datetime import datetime
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
         #  db.session.delete(existing_slot)
         #  db.session.commit()
            #   db.session.delete(existing_slot) 
          #  new_slot = Slot(resource_id=resource_id, time_slot=time_slot, booking_date = booking_date,booked_by=existing_slot.booked_by)

        #else:
        #new_slot = Slot(resource_id=resource_id, time_slot=time_slot, booked_by=booked_by)

        #db.session.add(new_slot)
        
    #db.session.query(Slot).delete()
    db.session.commit()
    
    booked_slots = Slot.query.filter_by(booking_date=booking_date).all()
    #booked_slots = Slot.query.all()
    
    return render_template('index.html', resources=resources, booked_slots=booked_slots)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

