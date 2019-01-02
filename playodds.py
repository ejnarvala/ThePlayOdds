from flask import Flask, request, render_template, abort, jsonify, make_response
from PlayOddsEngine import simulator, extractor
from PlayOddsEngine.extractor import *
from rq import Queue
from rq.job import Job
from worker import conn

app = Flask(__name__)
q = Queue(connection=conn)


@app.route("/")
def index():
	if(request.method == 'POST'):
		return render_template('results.html', results=results)
	return render_template('index.html')

@app.route("/simulate", methods=['POST'])
def simulate():
	print('got something')
	output = {
		'job_id': None,
		'error': None
	}
	try:
		payload = request.get_json()
		print('payload:',payload)
		league_id = extractor.extract_leagueId(payload['espnURL'])
		week = str(payload['week'])
		year = str(payload['year'])
		week = int(week) if (not week == 'Week') else None
		year = int(year) if (not year == 'Year') else simulator.CURRENT_SEASON
		print('sim running...')
		results = simulator.simulate(league_id, year, week)
		job = q.enqueue_call(func=simulator.simulate, args=(league_id, year, week), timeout=1000)
		output['job_id'] = job.get_id()
	except Exception as e:
		print('Error:',str(e))
		error = str(e)
		output['error'] = error
	
	print(output)
	return jsonify(output)


@app.route("/job_status/<int:job_id>")
def job_status(job_id):
    q = Queue()
    job = q.fetch_job(job_id)
    if job is None:
        response = {'status': 'unknown'}
    else:
        response = {
            'status': job.get_status(),
            'result': job.result
        }
    return jsonify(response)


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
