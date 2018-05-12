from flask import Flask, request, render_template, abort, jsonify, make_response
from PlayOddsEngine import simulator, extractor

app = Flask(__name__)



@app.route("/", methods=['GET', 'POST'])
def index():
	error = None
	if(request.method == 'POST'):
		url = str(request.form['espn-url'])
# TODO: add option to submit just leagueID by checking int(id) == id && len(id)
		url_extracted, extracted_data = extractor.extract_leagueId(url) # returns true/fase, leagueId/error
		if(not url_extracted):
			return render_template('index.html', error=extracted_data)
		try:
			results = simulator.simulate(leagueId)
		except Exception as e:
			print(str(e))
			error = 'Simulator Error has Occurred! :O'
			return render_template('index.html', error=data)
		
		return render_template('results.html', results=data)

	return render_template('index.html', error=error)

@app.route("/info")
def info():
	# content = ['Issue?', 'Open a Github issue', 'https://github.com/ejnarvala/ThePlayOdds']
	return render_template('info.html')


@app.route("/api/v1.0/leagueid/<int:api_league_id>", methods=['GET'])
def get_results_leagueid(api_league_id):
	try:
		results = simulator.simulate(api_league_id)
	except Exception as e:
		# print(str(e))
		error = 'Simulator Error has Occurred! :O'
		return make_response(jsonify({'error':error}), 500)

	return jsonify(results)



@app.route("/api/v1.0/url/<api_url>", methods=['GET'])
def get_results_url(api_url):
	url_extracted, extracted_data = extractor.extract_leagueId(api_url) # returns true/fase, leagueId/error
	if(not url_extracted):
		return make_response(jsonify({'error': extracted_data}), 400)
	try:
		results = simulator.simulate(leagueId)
	except Exception as e:
		# print(str(e))
		error = 'Simulator Error has Occurred!'
		return make_response(jsonify({'error':error}), 500)

	return jsonify(results)



if __name__== "__main__":
	app.run()