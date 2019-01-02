var resultsTable;

window.onload = function() {
    resultsTable = document.getElementById('results_table');
    setSubtitle('Status: ' + res.status);
    if(res.result){
        createTable(res.result);
    }else{
        pollJobStatus(res.job_id);
    }
};


function setSubtitle(){
    output = ''
    for(let i = 0; i < arguments.length; i++){
        if(i > 0){
            output += '<br>';
        }
        output += arguments[i];
    }
    document.getElementById('results_subtitle').innerHTML = output;
}

function pollJobStatus(){
    setTimeout(function(){
        fetch('/job_status/' + res.job_id)
        .then(response => response.json())
        .then(res_json =>{
            if(res_json.result){
                createTable(res_json.result);
            }else{
                setSubtitle('Status: ' + res_json.status);
                console.log('polling');
                pollJobStatus();
            }
        })
    }, 2000)
}


function createTable(results){
    setSubtitle(results.league_info.name)

    const table_headers = ["name", "owner", "wins", "losses", "ties"];
    const table_headers_rounded = ["average", "points_for", "points_against", "expected_wins"]

    //adds the seed numbers to the table depending on how mnay teams in the results
    for(let i in results.team_data){
        var seed_num = document.createElement('th');
        seed_num.innerHTML = "Seed " + i;
        resultsTable.tHead.rows[0].appendChild(seed_num);
    }

    var tbod = document.createElement('tbody');

    //loop through each team (row) in the table
    for(let i in results.team_data){
        //stuff for the logo
        var tr = document.createElement('tr');
        var td_logo = document.createElement('td');
        var img_logo = document.createElement('img');
        img_logo.setAttribute("class", "logo");
        //logo backup image
        img_logo.onerror = function() {
            this.src = "/static/img/default_logo.png";
            console.clear();
        }
        img_logo.src = results.team_data[i].logo;
        td_logo.appendChild(img_logo);
        tr.appendChild(td_logo);

        //loop through the table structure array to make this simpler
        for(let j of table_headers){
            var td = document.createElement('td');
            td.innerHTML = results.team_data[i][j];
            tr.appendChild(td);
        }
        //loops through things that need to be rounded
        //TODO: make the backend return rounded values
        for(let j of table_headers_rounded){
            var td = document.createElement('td');
            //hacky way to round to 2 decimal points
            td.innerHTML = Number(Math.round(results.team_data[i][j] +'e2')+'e-2');;
            tr.appendChild(td);
        }

        //iterates through the odds for each seed
        for(let j in results.team_data){
            var td = document.createElement('td');
            td.innerHTML = Number(Math.round(results.team_data[i].odds[j] +'e2')+'e-2');;
            tr.appendChild(td);
        }

        tbod.appendChild(tr);
    }


    resultsTable.appendChild(tbod);

    resultsTable.style.display = "";
}