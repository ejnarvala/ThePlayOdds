from flask import Flask, request, render_template, abort, jsonify, make_response
from PlayOddsEngine import simulator, extractor
from PlayOddsEngine.extractor import *

app = Flask(__name__)


@app.route("/", methods=['GET', 'POST'])
def index():
	error = None
	if(request.method == 'POST'):
		url = str(request.form['espn-url'])
		try:
			league_id = extractor.extract_leagueId(url)
		except Exception as e:
			return render_template('index.html', error=str(e))
		try:
			week = str(request.form['inputWeek'])
			year = str(request.form['inputYear'])
			week = int(week) if (not week == 'Week') else None
			year = int(year) if (not year == 'Year') else simulator.CURRENT_SEASON
			results = simulator.simulate(league_id, year, week)
		except SimulatorError as e:
			return render_template('index', error=str(e))
		except Exception as e:
			print(str(e))
			error = 'Something went wrong!'
			return render_template('index.html', error=error)
		
		return render_template('results.html', results=results)

	return render_template('index.html', error=error)

@app.route("/info")
def info():
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
	app.run(debug=True)
