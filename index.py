import os,re
from flask import Flask, request, session, url_for, redirect, \
     render_template, abort, g, flash
from pymongo import Connection

UPLOAD_FOLDER = '/path/to/upload'

app = Flask(__name__)
	
@app.route('/')
def index():
	return render_template('index.html')

@app.route('/search', methods=['GET'])
def search():
	connection = Connection()
	db = connection.test_db
	data = db.test_data
	res = data.find_one({'word':request.args.get('text')})
	return render_template('search.html', res=res)

@app.route('/upload', methods=['GET','POST'])
def upload():
	if request.method == 'POST':
		indexfile = request.files['index']
		indexfile.save(os.path.join(UPLOAD_FOLDER, indexfile.filename))
		datafile = request.files['data']
		datafile.save(os.path.join(UPLOAD_FOLDER, datafile.filename))
		if(file_import(indexfile.filename,datafile.filename)):
			flash('Files imported successfully')
		else:
			flash('Files were not imported.Please try again')
		return redirect(url_for('index'))
	return render_template('upload.html')
	
def file_import(indexfile, datafile):
	#~ Some of the code here taken from the nltk project
	connection = Connection()
	db = connection.test_db
	data = db.test_data
	for i, line in enumerate(open(os.path.join(UPLOAD_FOLDER, indexfile))):
		if line.startswith(' '):
			continue
		lemma_names = []
		next = iter(line.split()).next
		try:
			lemma = next()
			pos = next()
			n_synsets = int(next())
			n_pointers = int(next())
			_ = [next() for _ in xrange(n_pointers)]
			n_senses = int(next())
			_ = int(next())
			synset_offsets = [int(next()) for _ in xrange(n_synsets)]
		except (AssertionError, ValueError):
			return False
		for i, offset in enumerate(synset_offsets):
			data_file = open(os.path.join(UPLOAD_FOLDER, datafile))
			data_file.seek(offset)
			data_file_line = data_file.readline()
			columns_str, gloss = data_file_line.split('|')
			try:
				next = iter(columns_str.split()).next
				synset_offset = int(next())
				lexname_index = int(next())
				synset_pos = next()
				n_lemmas = int(next(), 16)
			except (AssertionError, ValueError):
				return False
			for _ in xrange(n_lemmas):
				lemma_name = next()
				lex_id = int(next(), 16)
				m = re.match(r'(.*?)(\(.*\))?$', lemma_name)
				lemma_name, syn_mark = m.groups()
				lemma_names.append(lemma_name.replace("_"," "))
		post = {"word": lemma.replace("_"," "),"pos" : pos,"def" : gloss,"rel" : lemma_names}
		data.insert(post)
	return True
		
if __name__ == '__main__':
	app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
	app.run(debug=True)
