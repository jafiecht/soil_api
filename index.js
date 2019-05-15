var express = require('express');
var uuid = require('uuid');
var bodyParser = require('body-parser');
var app = express();


app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: false }));

//Nessesary while in development
app.use(function (req, res, next) {
  res.setHeader('Access-Control-Allow-Origin', 'http://localhost:3000');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST');
  res.setHeader('Access-Control-Allow-Headers', 'X-Requested-With,content-type');
  res.setHeader('Access-Control-Allow-Credentials', false);
  next();
});

app.listen(5000, function() {
  console.log('Listening on port 5000');
})

app.post('/submit', submissionScript);
app.get('/status', statusScript);
app.get('/output', outputScript);

function submissionScript(req, res) {
  
  if (!req.body.points || !req.body.boundary || !req.body.userEmail) {
    return res.status(400).send({
      message: 'User email, field boundary, and point samples are all required.'
    })
  } else {
    var requestID = uuid.v4();
    return res.status(200).send({
      id: requestID,
    });
  }  
}

function statusScript(req, res) {
 
  if (!req.query.id) {
    return res.status(400).send({
      message: 'A request ID is required.'
    })
  } else {
    var integer = Math.floor(Math.random() * Math.floor(4));
    var status;
    if (integer === 0) {
      status = 'not found';
    } else if (integer === 1) {
      status = 'in progress';
    } else if (integer === 2) {
      status = 'server error';
    } else {
      status = 'complete';
    }
    return res.status(200).send({
      status: status,
    });
  }  
}

function outputScript(req, res) {
  
  if (!req.query.id) {
    return res.status(400).send({
      message: 'A request ID is required.'
    })
  } else {
    return res.status(200).send({
      id: requestID,
    });
  }  
}
