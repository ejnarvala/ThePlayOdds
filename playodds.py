from flask import Flask, request, render_template, abort
from Playodds_Engine import simulator, extractor

app = Flask(__name__)


@app.route("/", methods=['GET', 'POST'])
def index():
	error = None
	if(request.method == 'POST'):
		url = str(request.form['espn-url'])
		try:
			leagueId = extractor.extract_leagueId(url)
		except (ValueError, KeyError) as e:
			error = 'Invalid URL'
			return render_template('index.html', error=error)
		try:
			results = simulator.simulate(leagueId)
		except Exception as e:
			error = 'Simulator Error has Occurred! :O'
			return render_template('index.html', error=error)

		return render_template('results.html', results=results)


	return render_template('index.html', error=error)

@app.route("/info")
def info():
	content = ['Issue?', 'Open a Github issue', 'https://github.com/ejnarvala/ThePlayOdds']
	return render_template('info.html', content=content)


if __name__== "__main__":
	app.run()