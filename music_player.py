#using modules
from flask import Flask, render_template, url_for, request, redirect,flash
from flask_sqlalchemy import SQLAlchemy
from flask import current_app, send_file, send_from_directory
import os

UPLOAD_FOLDER = '/uploads'
ALLOWED_EXTENSIONS = {'mp3'}


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///songs.db'	#calling database songs.db

db=SQLAlchemy(app) #creating instance of database

#Creating Database model
class Song(db.Model):
	#creating structure of songs database
	song_id=db.Column(db.Integer, primary_key=True) 
	title=db.Column(db.String(100),nullable=False)
	artist=db.Column(db.String(100),nullable=False)
	album=db.Column(db.String(100),nullable=False)
	url=db.Column(db.String(100),nullable=False)
	
	def __repr__(self):
		return '<Song %r>' % self.song_id

#Implementing function to upload restriction(only mp3 files)
def allowed_mp3(filename):
	return '.' in filename and filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS


#Implementing Upload song operation, when upload button is clicked	
@app.route('/',methods=['POST','GET'])
def index():
	if request.method == 'POST':
		#get inputs from form
		song_title=request.form['txtTitle']
		song_artist=request.form['txtArtist']
		song_album=request.form['txtAlbum']
		fileObj=request.files['txtFile']
		if fileObj and allowed_mp3(fileObj.filename):
			fileObj.save(fileObj.filename)  
			song_url=fileObj.filename
			new_song=Song(title=song_title,artist=song_artist,album=song_album,url=song_url)
			try:
				db.session.add(new_song) #insert new song to database
				db.session.commit() #save changes to database
				return redirect('/')
			except:
				return 'Error in uploading new song!!'
		else:
			return 'Only .mp3 files are allowed!!!'
	else:
		songs=Song.query.order_by(Song.title).all() #retrieve existing songs
		return render_template("index.html",songs=songs) #returning index.html as root web app


#Implementing delete operation using current id of song
@app.route('/delete/<int:song_id>')
def deleteSong(song_id):
	song_to_delete=Song.query.get_or_404(song_id)
	try:
		db.session.delete(song_to_delete)
		db.session.commit()
		return redirect('/')
	except:
		return 'Deletion failed!'

#Implementing function for download operation using current filename
@app.route('/download/<path:filename>')
def download_file(filename):
    return send_file(filename, as_attachment=True)

#Implementing function for sharing unique URL
@app.route('/shareURL/<path:filename>')
def file_URL(filename):
	return render_template("play.html",filename=filename) #returning play.html with shared URL
	
#Implementing function for search operation using search string
@app.route('/search_file',methods=['POST','GET'])
def search_file():
	if request.method == 'POST':
		strSearch=request.form['txtSearch']
		columnSearch=request.form['lstSearch']
		
		#execute below query based for searching on title/artist/album
		if columnSearch=='title':
			result=db.engine.execute("Select * from Song where title = '"+strSearch+"'")
		elif columnSearch=='artist':
			result=db.engine.execute("Select * from Song where artist = '"+strSearch+"'")
		elif columnSearch=='album':
			result=db.engine.execute("Select * from Song where album = '"+strSearch+"'")
		else: #default searching criteria is 'none', to display all the play list
			result=db.engine.execute("Select * from Song")
		
		return render_template("index.html",songs=result) #returning index.html as root web app


if __name__ == "__main__":
	app.run(debug=True)
	
