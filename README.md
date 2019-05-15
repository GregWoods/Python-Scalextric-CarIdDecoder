# CarIdDecoder

Python 3 script running on Raspberry Pi Zero W, which takes a GPIO input, measures pulse length and saves to a sqlite3 database.

The purpose is to connect my Scalextric carId circuit to the input, then record to a database the Infrared pulses coming from various Scalextric digital chips. The data can be analysed later with sql queries or python's MatPlotLib. This data could be used to compare differences between different firmware, different hardware revisions of the Scalextric chip, and most importantly, compare the pulse widths of the 6 different CarIds. This will enable me to fine tune my code in future projects (such as the Scalextric SmartPit) which read the carId.

The python script also runs a web server on port 8081, which allows setting various additional parameters which get saved to the database along with the pulse widths. This allows us to know which carid, physical chip revision, or firmware any given a sequence of pulses comes from. This data is essential for plotting and analysing the data later.

To run:
python3 decoder.py

To set the parameters such as CarId, ChipRevision, Firmware for the current recording, go to:
http://pizero:8081

To plot the results of all CarIds (no filtering on chip revision or firmware)
http://pizero:8081/plot

To analyse the data using sql:
sqlite carid-pulses-sqlite.db
remember the sql will run immediately when terminated with a semicolon.
