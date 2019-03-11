# CarIdDecoder

python script running on Raspberry Pi Zero W, which takes a GPIO input, measures pulse length and saves to a sqlite3 database.
For testing, the GPIO input is simply a pushbutton.
The purpose is to connect my Scalextric carId circuit to the input, to read teh Infrared pulses coming from various Scalextric digital chips.
The python script also runs a web server on port 8081, which allows setting various additional parameters which get saved to the database along with the pulse widths. This allows us to know which carid, physical chip revision, or firmware any given a sequence of pulses comes from. This data is essential for plotting and analysing the data later
