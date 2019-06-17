const mongoose = require('mongoose');
const Task = mongoose.model('Task');

module.exports = {
  createTaskObject: (taskID, values) => {
    return new Task({
      id: taskID,
      createdAt: String(Math.floor(Date.now() / 1000)),
      status: 'in progress',
      email: values.email,
      jpgPath: null,
      tifPath: null,
      bounds: null,
      points: values.points,
      boundary: values.boundary,
    });
  }
};

