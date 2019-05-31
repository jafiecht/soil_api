//Imports
/////////////////////////////////////////////////////////////////////////////
const mongoose = require('mongoose');
const uuid = require('uuid');
const { checkSchema, validationResult } = require('express-validator/check')
const { getTaskSchema } = require('./validation')
const { createTaskObject } = require('./models/taskCreator')
const { sendMail } = require('./mailer')
const Task = mongoose.model('Task');

//Routes
/////////////////////////////////////////////////////////////////////////////
module.exports = (app) => {

/*-------------------------------------------------------------------------*/
  app.post('/submit', checkSchema(getTaskSchema()), (req, res) => {
    console.log('submit');
 
    //Is the correct information supplied?  
    if (req.body.points && req.body.boundary && req.body.email) {
      
      //Is all the information in the correct format?
      const errors = validationResult(req.body);
      if (errors.isEmpty()) {
 
        //Create and attempt to save the task
        const taskID = uuid.v4();
        const taskObject = createTaskObject(taskID, req.body);
        taskObject.save(err => {
      
          //Was there an error while saving?
          if (!err) {
            var spawn = require("child_process").spawn;
            var process = spawn('python', 
              ['./scripts/apicall.py', req.query.id], 
              {
                detached: true,
                stdio:'ignore' 
              }
            );
       
            //Send email to user.
            emailUser(req.body.email, taskID);
 
           //Return Success 
            return res.status(200).send({
              id: taskID,
            });
        
            //Send email to user.
            //emailUser(req.body.email, taskID);
            console.log('test');
 
          //There was an error while saving.
          } else {
            taskObject.delete();
            return res.sendStatus(500);
          }
        })

      //Information supplied in the wrong format 
      } else {
        return res.status(422).send({
          message: 'Information supplied in incorrect format',
          errors: errors.array()
        });
      }
    
    //Incorrect information supplied
    } else {
      return res.status(400).send({
        message: 'User email, field boundary, and point samples are all required.'
      });
   }  
  })

/*-------------------------------------------------------------------------*/
  app.get('/status', (req, res) => {
   
    //Was a taskID provided? 
    if (req.query.id) {

      //Is the taskID a string?
      if (typeof req.query.id === 'string') {
       
        //Check task status 
        Task.find({id: req.query.id}, (err, arr) => {
          
          //Only one result found with no errors
          if (!err) {
          
            //Only one result found
            if (arr && arr.length === 1) {

              //Completed
              if (arr[0].status === 'complete') {

                return res.status(200).send(arr[0]);
            
              //Incomplete
              } else {
                return res.status(200).send({
                  status: arr[0].status,
                });
              }

            //None or more than one result found
            } else {
              return res.status(200).send({
                status: 'not found',
              });
            }

          //Server error
          } else {
            return res.status(500).send();
          }       
        });       

      //TaskID wasn't string
      } else {
        return res.status(400).send({
          message: 'The request id was in an incorrect format.'
        });
      }

    //No taskID provided.
    } else {
      return res.status(400).send({
        message: 'A request ID is required.'
      });
    }
  })
}


//Routes
/////////////////////////////////////////////////////////////////////////////
function pruneData() {
  console.log('prune');
};


function emailUser(email, TaskID) {
  mailParams = {
    to: email,
    subject: 'Interpolation Request Submitted',
    text: `Hello there! Your interpolation request ID is: ${TaskID}. Please allow up to
          two hours for your request to completed. All requests are purged from the
          server after two days.`,
    html: `<p><b style='font-size:20px'>Interpolation Request Submitted</b><br></p>
          <p><b>Request ID:</b> ${TaskID}<br></p>
          <p>Please allow up to two hours for your request to completed. All 
          requests are purged from the server after two days.</p>`
  };
  sendMail(mailParams);
};









