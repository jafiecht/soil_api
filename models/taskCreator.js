const mongoose = require('mongoose');
const Task = mongoose.model('Task');

module.exports = {
  createTaskObject: (taskID, values) => {
    return new Task({
      id: taskID,
      createdAt: new Date().toUTCString(),
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

