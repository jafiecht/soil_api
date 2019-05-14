var express = require('express');
var bodyParser = require('body-parser');
var app = express();


app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: false }));

app.listen(5000, function() {
  console.log('Listening on port 5000');
})

app.get('/predict', runScript);

function runScript(req, res) {
  var spawn =  require('child_process').spawn;
  
  var process =  spawn('python', ["./../framework/root.py", req.body]);

  process.stdout.on('data', function(data) { 
    console.log(data);
  });
  res.sendStatus(200)
}
