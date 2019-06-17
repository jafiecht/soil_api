const mongoose = require('mongoose');
const { Schema } = mongoose;

const taskSchema = new Schema({
  id: String,
  createdAt: String,
  status: String,
  email: String,
  jpgPath: String,
  tifPath: String,
  message: String,
  bounds: [[String]],
  points: {
    type: String,
    features: [{
      type: String,
      geometry: {
        type: String,
        coordinates: [String]
      },
      properties: {
        value: String
      },
    }],
  },
  boundary: {
    type: String,
    features: [{
      type: String,
      geometry: {
        type: String,
        coordinates: [[[String]]]
      },
      properties: {
        value: String
      },
    }],
  },
}, {typeKey: '$type'});



mongoose.model('Task', taskSchema);

